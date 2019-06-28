import pytest
from psiturk.psiturk_exceptions import *

def test_awskeys_invalid(capfd):
    import psiturk.experiment_server_controller as control
    from psiturk.psiturk_config import PsiturkConfig
    from psiturk.psiturk_shell import PsiturkNetworkShell
    import psiturk.psiturk_shell as ps
    
    
    config = PsiturkConfig()
    config.load_config()
    config['Shell Parameters']['persistent_history_file'] = ''
    config['AWS Access']['aws_access_key_id'] = ''
    config['AWS Access']['aws_secret_access_key'] = ''
    server = control.ExperimentServerController(config)

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
    
    
def test_awscreds_notset(capfd):
    import psiturk.experiment_server_controller as control
    from psiturk.psiturk_config import PsiturkConfig
    from psiturk.psiturk_shell import PsiturkNetworkShell
    import psiturk.psiturk_shell as ps
    
    
    config = PsiturkConfig()
    config.load_config()
    config['Shell Parameters']['persistent_history_file'] = ''
    config['AWS Access']['aws_access_key_id'] = 'YourAccessKeyId'
    config['AWS Access']['aws_secret_access_key'] = 'YourSecretAccessKey'
    server = control.ExperimentServerController(config)

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