import pytest
from psiturk.psiturk_exceptions import *

@pytest.fixture()
def experiment_server_controller(mocker):
    import psiturk.experiment_server_controller
    mocker.patch.object(psiturk.experiment_server_controller.ExperimentServerController, 'is_port_available', lambda *args, **kwargs: True)

@pytest.fixture()
def psiturk_shell(mocker):
    import psiturk.psiturk_shell
    mocker.patch.object(psiturk.psiturk_shell.PsiturkNetworkShell, 'get_intro_prompt', lambda *args, **kwargs: '')

def test_awskeys_invalid(capfd, experiment_server_controller, psiturk_shell):
    import psiturk.experiment_server_controller
    from psiturk.psiturk_config import PsiturkConfig
    from psiturk.psiturk_shell import PsiturkNetworkShell
    import psiturk.psiturk_shell as ps
    
    
    config = PsiturkConfig()
    config.load_config()
    config.set('Shell Parameters', 'persistent_history_file', '')
    config.set('AWS Access','aws_access_key_id', '')
    config.set('AWS Access','aws_secret_access_key', '')
    server = psiturk.experiment_server_controller.ExperimentServerController(config)

    launch_in_sandbox_mode = True
    quiet = False
    try:
        shell = PsiturkNetworkShell(
            config, server,
            launch_in_sandbox_mode,
            quiet=quiet)
    except SystemExit:
        pass
    
    out, err = capfd.readouterr()
    assert NoMturkConnectionError().message in out
    
    
def test_awscreds_notset(capfd, experiment_server_controller, psiturk_shell):
    from psiturk.psiturk_config import PsiturkConfig
    from psiturk.psiturk_shell import PsiturkNetworkShell
    import psiturk.psiturk_shell as ps
    import psiturk.experiment_server_controller
    
    config = PsiturkConfig()
    config.load_config()
    config.set('Shell Parameters', 'persistent_history_file', '')
    config.set('AWS Access','aws_access_key_id', 'YourAccessKeyId')
    config.set('AWS Access','aws_secret_access_key', 'YourSecretAccessKey')
    
    server = psiturk.experiment_server_controller.ExperimentServerController(config)

    launch_in_sandbox_mode = True
    quiet = False
    try:
        shell = PsiturkNetworkShell(
            config, server,
            launch_in_sandbox_mode,
            quiet=quiet)
    except SystemExit:
        pass
    
    out, err = capfd.readouterr()
    assert AWSAccessKeysNotSetError().message in out