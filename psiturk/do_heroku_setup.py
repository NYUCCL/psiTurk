from __future__ import generator_stop
import os
import subprocess
import shutil


def _check_heroku_cmd_found():
    command = 'heroku'
    if not shutil.which(command):
        from psiturk.psiturk_exceptions import HerokuCmdNotFound
        raise HerokuCmdNotFound()


def _check_heroku_logged_in():
    if subprocess.getstatusoutput('heroku auth:whoami')[0]:
        from psiturk.psiturk_exceptions import HerokuNotLoggedIn
        raise HerokuNotLoggedIn()


def _check_is_git_repo():
    if subprocess.getstatusoutput('git rev-parse --git-dir')[0]:
        from psiturk.psiturk_exceptions import HerokuNotAGitRepo
        raise HerokuNotAGitRepo()


def _check_heroku_app_set():
    if subprocess.getstatusoutput('heroku config')[0]:
        from psiturk.psiturk_exceptions import HerokuAppNotSet
        raise HerokuAppNotSet()


def _set_heroku_config_vars():
    from psiturk.psiturk_config import PsiturkConfig

    CONFIG = PsiturkConfig()
    CONFIG.load_config()

    subprocess.call(['heroku', 'config:set', 'ON_CLOUD=true'])

    print()
    print('psiturk has finished setting heroku config vars.')


def _add_postgresql_db():
    subprocess.call(['heroku', 'addons:create', 'heroku-postgresql:hobby-dev'])
    print()
    print("\n".join([
        "Your psiturk heroku app will use the just-added postgresql database instead of whatever is set in your config.txt.",
        "If you don't want this, then change or unset the heroku config var 'DATABASE_URL'",
        "and/or remove the heroku postgresql addon."]))


HEROKU_FILES_DIR = os.path.join(os.path.dirname(__file__), "heroku_files")


def _copy_heroku_files():
    """
    Heroku needs a Procfile, a requirements.txt, and a file that stores the
    """
    _TARGET = os.curdir
    from distutils import dir_util
    print("Copying {} to {}".format(HEROKU_FILES_DIR, _TARGET))
    dir_util.copy_tree(HEROKU_FILES_DIR, _TARGET)
    print('Remember to commit these new files to your git repository.')


def do_heroku_setup():
    _check_heroku_cmd_found()
    _check_heroku_logged_in()
    _check_is_git_repo()
    _check_heroku_app_set()
    _set_heroku_config_vars()
    _copy_heroku_files()
    # _add_postgresql_db()

    print()
    print("Heroku config done.")
    print()
    print("Don't forget that your database needs to be a persistent datastore!")


if __name__ == '__main__':
    do_heroku_setup()
