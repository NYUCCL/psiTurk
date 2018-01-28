from psiturk.psiturk_config import PsiturkConfig
import subprocess

CONFIG = PsiturkConfig()
CONFIG.load_config()

sections = ['psiTurk Access','AWS Access']
for section in sections:
    for item in CONFIG.items(section):
        #print 'heroku config:set ' + '='.join(item)
        subprocess.call('heroku config:set ' + '='.join(item), shell=True)
        

subprocess.call('heroku config:set ON_HEROKU=true', shell=True)

    

