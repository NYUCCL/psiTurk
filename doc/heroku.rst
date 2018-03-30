Running psiTurk on heroku
==========================

#. Go to http://www.heroku.com and create a new account if you don't already have one.

#. Make sure that `psiTurk`, `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_, and the `Heroku Command Line Interface <https://devcenter.heroku.com/articles/heroku-cli>`_ are installed on your computer.

#. Create a psiTurk example (all commands listed in this tutorial are meant to be typed into your terminal application): ::

    psiturk-setup-example

#. Navigate into your newly created psiTurk example folder: ::

    cd psiturk-example

#. Log in to `Heroku` (and put in your credentials when promted for them):  ::

    heroku login

#. Create a new app on `Heroku`: ::

    heroku create

#. Get the name of your newly created app: ::

    heroku apps

#. Create a Postgres database on the newly created `Heroku` app: ::

    heroku addons:create heroku-postgresql --app <name of your app>

#. Get the URL of the Postgres database that you just created: ::

    heroku config:get DATABASE_URL --app <name of your app>

#. Get the URL of your app: ::

    heroku domains --app <name of your app>

#. In your psiTurk example, open the `config.txt` file. Here, make the following settings: ::

    database_url = <Your Postgres database URL that you retrieved above>
    adserver_revproxy_host = <Your app URL that you retrieved above>
    host = 0.0.0.0
    threads = 1

#. Also, if you're not using the `psiTurk` Ad server, make the following settings: ::

    use_psiturk_ad_server = false
    ad_location = https://your-heroku-domain.herokuapp.com/pub

#. Run the following commands, replacing `XYZ` with your access and secret keys (you can also use `this Python script <https://github.com/NYUCCL/psiTurk/blob/908ce7bcfc8fb6b38d94dbae480449324c5d9d51/psiturk/example/set-heroku-settings.py>`_ to automatically run these commmands, provided that you've filled out your credentials in your .psiconfig file): ::

    heroku config:set --app <name of your app> ON_HEROKU=true
    heroku config:set --app <name of your app> psiturk_access_key_id=XYZ
    heroku config:set --app <name of your app> psiturk_secret_access_id=XYZ
    heroku config:set --app <name of your app> aws_access_key_id=XYZ
    heroku config:set --app <name of your app> aws_secret_access_key=XYZ

#. Initialize a Git repository inside the psiTurk example folder: ::

    git init

#. Stage all the files: ::

    git add .

#. Commit all the staged files: ::

    git commit -m "Initial commit"

#. I have no idea what I'm doing: ::

    heroku git:remote --app <name of your app>

#. Launch the app on `Heroku` (generates an error right now): ::

    git push heroku master

#. Run `psiTurk` locally on your machine: ::

    psiturk

! Explain the relationship between you running psiTurk locally and Heroku.


My own notes (will be removed in the final commit)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- First tip where I'm offering to write the docs: https://github.com/NYUCCL/psiTurk/issues/306

   The benefits of heroku are that:

   you get free SSL if you want to host your own ad, which is good because the psiturk ad server goes down under heavy load
   you get a heroku buffering server in front of your psiturk gunicorn instance, which helps with performance a little bit
   although it would be better to put nginx in front of gunicorn within the psiturk instance
   it's somewhat easier to manage than ec2 for the tech-wary (no need for security groups, no need to ssh in)
   free psql server (you're not using sqlite on your ec2 instance, are you?)
   scaleable
   Downsides:

   can get expensive if you need any kind of horsepower beyond 512MB memory and one node (I haven't needed any more than the "hobby" class yet)
   Definitely would be good to build some scripts into psiturk that handle getting up and going with heroku

- Summary: https://github.com/NYUCCL/psiTurk/issues/296#issuecomment-361039062
- Step-by-step: https://github.com/NYUCCL/psiTurk/issues/254#issuecomment-282862588

   Thanks for your work, @suchow. I just set up psiturk proper to work with heroku following the pattern of your fork. Env vars for what would normally go in .psiturkconfig now are respected in psiturk_config.py, so psiturk_shell.py didn't have to be altered except for the improved logging bit.

   Changes from your instructions:

   one new env var (ON_HEROKU)
   one new config.txt setting (adserver_revproxy_host -- replaces the HOST env var step)
   hit can be created without needing to run bash on the server (no need to run heroku run bash)
   This is compatible with the use_psiturk_ad_server=false functionality.

   I've copied your instructions below, with edits.

   Create a Heroku account

   Install the Heroku toolbelt (https://toolbelt.heroku.com/)

   Install psiTurk (install from github until >v2.2.0 is released)

   Create a copy of the demo app (psiturk-setup-example). **

   Initialize a Git repository inside the demo app (git init)

   Create a new app using the Heroku toolbelt (heroku create)

   Add a Postgres database to the Heroku app (heroku addons:create heroku-postgresql)

   Get the URL of the Postgres database that you have just created (heroku config:get DATABASE_URL)

   In the demo app, you should see a file config.txt. Replace the database_url (should start with postgresql://) with the URL that you retrieved in Step 8.

   Also in config.txt, if using the psiturk ad server, set adserver_revproxy_host to your heroku domain name. Run heroku domains to see your domain name.

   In config.txt, also do this:

   host: 0.0.0.0
   threads: 1
   10.5 If not using the psiturk ad server, in config.txt,

   use_psiturk_ad_server = false
   ad_location = https://your-heroku-domain.herokuapp.com/pub
   Use /pub, not /ad, because .com/ad gets blocked by ad blockers

   Run the following command to tell your code that it is running on Heroku:
   heroku config:set ON_HEROKU=true.

   Set environment variables for your psiTurk and MTurk, replacing XYZ with your access and secret keys:

       heroku config:set psiturk_access_key_id=XYZ
       heroku config:set psiturk_secret_access_id=XYZ
       heroku config:set aws_access_key_id=XYZ
       heroku config:set aws_secret_access_key=XYZ
   See this comment for a convenience script for running all 'heroku config:set' commands.

   Stage all the files in the demo app (git add .)

   Commit all the staged files (git commit -m "Initial commit")

   Launch the app (git push heroku master)

   Run psiTurk (psiturk)

   Create the HIT and answer the questions it asks (hit create), saying yes (y) when it asks if you're using an external process.

   Go to the sandbox and try out your HIT.

   paging @braingineer to make sure you see this

   ** If you're starting from a preexisting psiturk app, you need to grab three files from /psiturk/example : requirements.txt, herokuapp.py, and Procfile. Place them in your project root, next to your config.txt.

- Python script in a commentary: https://github.com/NYUCCL/psiTurk/issues/254#issuecomment-305229718
- The same Python script in a file: https://github.com/NYUCCL/psiTurk/blob/908ce7bcfc8fb6b38d94dbae480449324c5d9d51/psiturk/example/set-heroku-settings.py

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
