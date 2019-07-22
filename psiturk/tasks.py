class TaskUtils():
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
    complete_count = Participant.count_completed(codeversion=campaign.codeversion, mode=campaign.mode)
    if complete_count >= campaign.goal:
        return scheduler.remove_job(kwargs['job_id'])
        
    task_utils.aws_services_wrapper.set_mode(campaign.mode)
    
    # how many for this round?
    remaining = campaign.assignments_per_round
    while remaining:
        this_hit = min(remaining, 9) # max 9 to avoid steep 40% commission
        task_utils.aws_services_wrapper.create_hit(
            num_workers=this_hit, reward=campaign.hit_reward, duration=campaign.hit_duration_hours)
        remaining = remaining - this_hit
    
    
    