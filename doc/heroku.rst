Running psiTurk on Heroku
==========================

`Heroku <http://www.heroku.com>`_ is a cloud service that lets you run applications in the cloud. You can run `psiTurk` on `Heroku` by preparing a git repository and then pushing it to `Heroku` which will deploy and autorun the code for you.

The benefits of `Heroku` are that:

- It's somewhat easier to manage than `Amazon Web Services EC2 <amazon_ec2.html>`_ for the tech-wary (no need for security groups, no need to ssh in).
- You can set up a free PostgreSQL server (which is `highly recommended <configure_databases.html>`_ to use over the default SQLite database that `psiTurk` uses).
- You get free SSL if you want to host your own ad, which is good because the `psiTurk Secure Ad Server <secure_ad_server.html>`_ goes down under heavy load.
- It's scaleable.
- You get a `Heroku` buffering server in front of your `psiTurk` gunicorn instance, which helps with performance a little bit (although it would be better to put nginx in front of gunicorn within the `psiTurk` instance).

One downside with `Heroku` is that it can get expensive if you need any kind of horsepower beyond 512MB memory and one node.

What follows is a step-by-step tutorial for setting up a `psiTurk` example experiment on `Heroku` (both the experiment itself and ad) with a `PostgreSQL` database for collecting data:

#. Go to the `Heroku website <http://www.heroku.com>`_ and create a new account if you don't already have one.

#. Make sure that `psiTurk <install.html>`_, `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_, and the `Heroku Command Line Interface <https://devcenter.heroku.com/articles/heroku-cli>`_ are installed on your computer.

#. Create a psiTurk example at a desired location (all commands listed in this tutorial are meant to be typed into your terminal application): ::

    psiturk-setup-example
    
If you're starting from a preexisting psiturk app, you need to grab three files from `/psiturk/example`: `requirements.txt`, `herokuapp.py`, and `Procfile`. Place them in your project root, next to your `config.txt`

#. Navigate into your newly created psiTurk example folder: ::

    cd psiturk-example
    
   Or if you are starting from an already-existing psiturk project, navigate to your project root dir.

#. Initialize a Git repository in the root dir of your psiturk project the psiTurk (your current working directory): ::

    git init

#. Log in to `Heroku` (and put in your credentials when promted for them):  ::

    heroku login

#. Create a new app on `Heroku`. Running this command will add a `remote` to your `.git/config` file, which will make it easier to run `heroku` commands from your project folder that are automatically associated with your newly-created Heroku app.: ::

    heroku create

#. Create a Postgres database on the newly created `Heroku` app: ::

    heroku addons:create heroku-postgresql

#. Get the URL of the Postgres database that you just created: ::

    heroku config:get DATABASE_URL

#. Get the URL of your app: ::

    heroku domains

#. In your psiTurk example, open the `config.txt` file. Here, find and make the following settings for the these rows, and then save the file: ::

    database_url = <Your Postgres database URL that you retrieved above>
    host = 0.0.0.0
    threads = 1
    ad_location = https://<Your app URL that you retrieved above>/pub
    use_psiturk_ad_server = false    

#. Run the following commands, replacing `<XYZ>` with your access and secret keys for `Amazon Web Services <amt_setup.html#obtaining-aws-credentials>`_ and `psiTurk Secure Ad Server <psiturk_org_setup.html#obtaining-psiturk-org-api-credentials>`_ (you can also use `this Python script <https://github.com/NYUCCL/psiTurk/blob/908ce7bcfc8fb6b38d94dbae480449324c5d9d51/psiturk/example/set-heroku-settings.py>`_ to automatically run these commmands, provided that you've filled out your credentials in your `.psiturkconfig` file. Running this script is the recommended approach!): ::

    heroku config:set ON_HEROKU=true
    heroku config:set psiturk_access_key_id=<XYZ>
    heroku config:set psiturk_secret_access_id=<XYZ>
    heroku config:set aws_access_key_id=<XYZ>
    heroku config:set aws_secret_access_key=<XYZ>

#. Stage all the files in your psiTurk example to your Git repository: ::

    git add .

#. Commit all the staged files to your Git repository: ::

    git commit -m "Initial commit"

#. Push the code to your `Heroku` git remote, which will trigger a build process on Heroku, which, in turn, runs the command specified in `Procfile`, which autolaunches your `psiTurk` server on the Heroku platform. Watch it run: ::

    git push heroku master

#. Run `psiTurk` locally on your machine: ::

    psiturk

#. To verify that your app is running, visit your `heroku` domain url in your browser. Obtain your `heroku` app url by running:: 

    heroku domains 
    
   From that url, you can conveniently obtain a debugging url by clicking "Begin by viewing the `ad`."
   
#. Run through your experiment. You should now have some data in the database. To extract it into `csv` files, type: ::

    download_datafiles

This should generate three datafiles for you in your local directory: `trialdata.csv`, `questiondata.csv`, and `eventdata.csv`. Congratulations, you've now gathered data from an experiment running on `Heroku`!

From your local `psiTurk` session, you can now `create and modify HIT's <command_line/hit.html>`_. When these are accessed by Amazon Mechanical Turk workers, the workers will be directed to the `psiTurk` session running on your `Heroku` app. This means that it is never necessary to launch `psiTurk` and run `server on` from _anywhere_ to run an experiment on Heroku. The server is automatically running, accessible via your Heroku domain url. (Of course, if you want to debug locally, you can still run a local server.)

Note that if you stay on the "Free" Heroku tier, your app will go to "sleep" after a period of inactivity. If your app has gone to sleep, it will take a few seconds before it responds if you visit its url. It should respond quickly once it "awakens". Consider upgrading to a "Hobby" heroku dyno to prevent your app from going to sleep.

Also note that if you desire to run commands against your `postgresql` db, you can run `heroku pg:psql` to connect, from where you can issue postgres commands. You can also connect directly to your heroku postgres db by installing and runinng `postgresql` on your local machine, and passing the `DATABASE_URL` that you set in `config.txt` as a command-line option.
