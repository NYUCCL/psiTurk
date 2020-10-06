from __future__ import print_function
from distutils import file_util
import os
from future import standard_library
standard_library.install_aliases()
import os
import sys
from distutils import file_util
from configparser import ConfigParser
from dotenv import load_dotenv, find_dotenv
from .psiturk_exceptions import EphemeralContainerDBError, PsiturkException

class PsiturkConfig(ConfigParser):

    def __init__(self, localConfig="config.txt",
                 **kwargs):
        load_dotenv(find_dotenv(usecwd=True))
        self.parent = ConfigParser
        self.parent.__init__(self, **kwargs)
        self.localFile = localConfig

    def load_config(self):
        defaults_folder = os.path.join(
            os.path.dirname(__file__), "default_configs")
        local_defaults_file = os.path.join(
            defaults_folder, "local_config_defaults.txt")

        # Read default local, then user's local, and then env vars. This way
        # any field not in the user's config file will be set to the default value.
        self.read([local_defaults_file, self.localFile])
        # import pytest; pytest.set_trace()
        # prefer environment
        these_as_they_are = ['PORT','DATABASE_URL'] # heroku sets these
        for section in self.sections():
            for config_var in self[section]:        
                config_var_upper = config_var.upper()
                config_val_env_override = None

                if config_var_upper in these_as_they_are:
                    config_val_env_override = os.environ.get(config_var_upper)

                # prefer any PSITURK_ key even over `these_as_they_are` variants
                psiturk_key = f'PSITURK_{config_var_upper}'
                if psiturk_key in os.environ:
                    config_val_env_override = os.environ.get(psiturk_key)

                if config_val_env_override:
                    self.set(section, config_var, config_val_env_override)

        # heroku files are ephemeral. Error if we're trying to use a file as the db
        if 'ON_CLOUD' in os.environ:
            database_url = self.get('Database Parameters', 'database_url')
            if ('localhost' in database_url) or ('sqlite' in database_url):
                raise EphemeralContainerDBError(database_url)

    def get_ad_url(self):
        if self.has_option('hit_configuration', 'ad_url'):
            return self.get('hit_configuration', 'ad_url')
        else:
            need_these = ['ad_url_domain','ad_url_protocol','ad_url_port','ad_url_route']
            for need_this in need_these:
                if not self.get('hit_configuration', need_this):
                    raise PsiturkException(message=f'missing ad_url config var `{need_this}`')
            ad_url_domain = self.get('hit_configuration', 'ad_url_domain')
            ad_url_protocol = self.get('hit_configuration', 'ad_url_protocol')
            ad_url_port = self.get('hit_configuration', 'ad_url_port')
            ad_url_route = self.get('hit_configuration', 'ad_url_route')
            return f"{ad_url_protocol}://{ad_url_domain}:{ad_url_port}:{ad_url_route}"
