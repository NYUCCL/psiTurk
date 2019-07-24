class TaskUtils():
    _scheduler_aws_services_wrapper = None
    
    @property
    def aws_services_wrapper(self):
        if not self._scheduler_aws_services_wrapper:
            from .amt_services_wrapper import MTurkServicesWrapper
            self._scheduler_aws_services_wrapper = MTurkServicesWrapper()
        return self._scheduler_aws_services_wrapper

task_utils = TaskUtils()
import logging
logger = logging.getLogger('apscheduler')

def do_campaign_round(campaign, **kwargs):
    from .models import Participant
    from .experiment import app
    
    # cancel if codeversion changes
    config_code_version = task_utils.aws_services_wrapper.config['Task Parameters']['experiment_code_version']
    if config_code_version != campaign.codeversion:
        logger.info('Codeversion changed (campaign: {}, config {}), removing job.'.format(campaign.codeversion, config_code_version))
        return app.apscheduler.remove_job(kwargs['job_id'])
    
    # cancel if campaign goal met
    complete_count = Participant.count_completed(codeversion=campaign.codeversion, mode=campaign.mode)
    if complete_count >= campaign.goal:
        logger.info('Campaign goal met ({}), removing job.'.format(campaign.goal))
        return app.apscheduler.remove_job(kwargs['job_id'])
        
    task_utils.aws_services_wrapper.set_mode(campaign.mode)
    
    # how many for this round?
    all_hits = task_utils.aws_services_wrapper.get_all_hits().data
    available_count = task_utils.aws_services_wrapper.count_available(hits=all_hits).data
    pending_count = task_utils.aws_services_wrapper.count_pending(hits=all_hits).data
    
    maybe_will_complete_count = available_count + pending_count
    
    campaign_remaining = campaign.goal - maybe_will_complete_count - complete_count
    round_remaining = campaign.assignments_per_round
    remaining = min(campaign_remaining, round_remaining)
    logger.info('Posting total of {} assignments this round.'.format(remaining))
    while remaining:
        this_hit = min(remaining, 9) # max 9 to avoid steep 40% commission
        task_utils.aws_services_wrapper.create_hit(
            num_workers=this_hit, reward=campaign.hit_reward, duration=campaign.hit_duration_hours)
        remaining = remaining - this_hit
    
    
    