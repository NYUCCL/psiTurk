from __future__ import generator_stop
import logging
logger = logging.getLogger('apscheduler')


class TaskUtils:
    _scheduler_aws_services_wrapper = None

    @property
    def aws_services_wrapper(self):
        if not self._scheduler_aws_services_wrapper:
            from .amt_services_wrapper import MTurkServicesWrapper
            self._scheduler_aws_services_wrapper = MTurkServicesWrapper()
        return self._scheduler_aws_services_wrapper


task_utils = TaskUtils()


def do_campaign_round(campaign, **kwargs):
    from .models import Participant
    from .experiment import app
    from .db import db_session

    # cancel if codeversion changes
    config_code_version = task_utils.aws_services_wrapper.config['Task Parameters']['experiment_code_version']
    if config_code_version != campaign.codeversion:
        logger.info(f'Codeversion changed (campaign: {campaign.codeversion}, config {config_code_version}), removing job.')
        return app.apscheduler.remove_job(kwargs['job_id'])

    # cancel if campaign goal met
    complete_count = Participant.count_completed(codeversion=campaign.codeversion, mode=campaign.mode)
    if complete_count >= campaign.goal:
        logger.info(f'Campaign goal met ({campaign.goal}), removing job.')
        campaign.end()
        db_session.add(campaign)
        db_session.commit()
        return

    task_utils.aws_services_wrapper.set_mode(campaign.mode)

    # how many for this round?
    all_hits = task_utils.aws_services_wrapper.get_all_hits().data
    available_count = task_utils.aws_services_wrapper.count_available(hits=all_hits).data
    pending_count = task_utils.aws_services_wrapper.count_pending(hits=all_hits).data

    maybe_will_complete_count = available_count + pending_count

    campaign_remaining = campaign.goal - maybe_will_complete_count - complete_count
    round_remaining = campaign.assignments_per_round
    remaining = min(campaign_remaining, round_remaining)
    logger.info(f'Posting total of {remaining} assignments this round.')
    while remaining:
        this_hit = min(remaining, 9)  # max 9 to avoid steep 40% commission
        result = task_utils.aws_services_wrapper.create_hit(
            num_workers=this_hit, reward=campaign.hit_reward, duration=campaign.hit_duration_hours)
        logger.info(result)
        remaining = remaining - this_hit
    return


# Approve All task_utils
def do_approve_all(mode):
    task_utils.aws_services_wrapper.set_mode(mode)
    result = task_utils.aws_services_wrapper.approve_all_assignments()
    if result.success:
        logger.info('Approved all.')
    else:
        logger.error(str(result.exception))
