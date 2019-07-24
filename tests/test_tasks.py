import pytest

@pytest.fixture()
def campaign():
    from psiturk.models import Campaign
    parameters = {
        'codeversion': '1.0',
        'mode': 'sandbox',
        'goal': 100,
        'minutes_between_rounds': 1,
        'assignments_per_round': 10,
        'hit_reward': 1.00,
        'hit_duration_hours': 1,
    }
    new_campaign = Campaign(**parameters)
    
    from psiturk.db import db_session
    db_session.add(new_campaign)
    db_session.commit()
    return new_campaign

def test_campaign_round_codeversion_change_cancel(campaign, mocker, caplog):
    from psiturk.tasks import do_campaign_round
    
    campaign_args = {
        'campaign': campaign,
        'job_id': campaign.campaign_job_id
    }
    
    from psiturk.experiment import app
    mocker.patch.object(app.apscheduler,
        'remove_job', lambda *args, **kwargs: True)
    
    from psiturk.amt_services_wrapper import MTurkServicesWrapper
    aws_services_wrapper = MTurkServicesWrapper()
    aws_services_wrapper.config['Task Parameters']['experiment_code_version'] = '1.1'
    
    import psiturk.tasks
    mocker.patch.object(psiturk.tasks.TaskUtils, 'aws_services_wrapper', aws_services_wrapper)
    
    
    import psiturk.experiment    
    remove_job_mock = mocker.patch.object(psiturk.experiment.app.apscheduler, 'remove_job')
    do_campaign_round(**campaign_args)
    remove_job_mock.assert_called()
    
    