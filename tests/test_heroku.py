import pytest
from psiturk.psiturk_exceptions import *


def test_heroku_cmd_not_found(mocker):
    from psiturk.do_heroku_setup import _check_heroku_cmd_found
    import shutil
    mocker.patch.object(shutil, 'which', lambda *args, **kwargs: None)
    with pytest.raises(HerokuCmdNotFound):
        _check_heroku_cmd_found()


def test_heroku_cmd_found(mocker):
    from psiturk.do_heroku_setup import _check_heroku_cmd_found
    import shutil
    mocker.patch.object(shutil, 'which',
                        lambda *args, **kwargs: 'heroku' if args[0] == 'heroku' else None)
    _check_heroku_cmd_found()


def test_heroku_not_logged_in(mocker):
    from psiturk.do_heroku_setup import _check_heroku_logged_in
    import subprocess
    mocker.patch.object(subprocess, 'getstatusoutput', lambda *args, **kwargs: (1, ''))
    with pytest.raises(HerokuNotLoggedIn):
        _check_heroku_logged_in()


def test_is_git_dir(mocker):
    from psiturk.do_heroku_setup import _check_is_git_repo
    import subprocess
    mocker.patch.object(subprocess, 'getstatusoutput', lambda *args, **kwargs: (1, ''))
    with pytest.raises(HerokuNotAGitRepo):
        _check_is_git_repo()


def test_heroku_app_set(mocker):
    from psiturk.do_heroku_setup import _check_heroku_app_set
    import subprocess
    mocker.patch.object(subprocess, 'getstatusoutput', lambda *args, **kwargs: (1, ''))
    with pytest.raises(HerokuAppNotSet):
        _check_heroku_app_set()


def test_set_heroku_config_vars(mocker):
    from psiturk.do_heroku_setup import _set_heroku_config_vars
    import subprocess
    mocker.patch.object(subprocess, 'call', lambda *args, **kwargs: 0)
    _set_heroku_config_vars()


def test_heroku_copy_files(mocker, tmpdir):
    from psiturk.do_heroku_setup import _copy_heroku_files, HEROKU_FILES_DIR
    import os

    _copy_heroku_files()

    files_in_heroku_dir = os.listdir(HEROKU_FILES_DIR)
    files_in_thisdir = os.listdir()
    for heroku_file in files_in_heroku_dir:
        assert heroku_file in files_in_thisdir


def test_add_heroku_psql_db(mocker):
    from psiturk.do_heroku_setup import _add_postgresql_db
    import subprocess
    mocker.patch.object(subprocess, 'call', lambda *args, **kwargs: 0)
    _add_postgresql_db()
