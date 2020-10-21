import pytest
from importlib import reload  # Python 3.4+


@pytest.fixture()
def client():
    import psiturk.experiment
    reload(psiturk.experiment)
    
    from psiturk.experiment import app
    
    from psiturk.dashboard import init_app
    
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True
    init_app(app)
    
    with app.test_client() as client:
        yield client


def test_task_get_list(client):
    rv = client.get('/api/tasks/', follow_redirects=True)
    json_data = rv.get_json()


def test_task_post_approve_all(client):
    rv = client.post('/api/tasks/', json={"name": "approve_all",
                                          "interval": '2.00'})
    json_data = rv.get_json()

