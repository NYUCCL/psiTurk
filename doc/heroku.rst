Running psiTurk on Heroku
==========================

`Heroku <http://www.heroku.com>`_ is a cloud service that let's you run applications in the cloud. You can run `psiTurk` on `Heroku` by preparing a git repository and then push it to `Heroku` which will deploy and autorun the code for you.

The benefits of `Heroku` are that:

- It's somewhat easier to manage than `Amazon Web Services EC2 <amazon_ec2.html>`_ for the tech-wary (no need for security groups, no need to ssh in).
- You can set up a free PostgreSQL server (which is `highly recommended <configure_databases.html>`_ to use over SQLite when running `psiTurk`).
- You get free SSL if you want to host your own ad, which is good because the `psiTurk Secure Ad Server <secure_ad_server.html>`_ goes down under heavy load.
- It's scaleable.
- You get a `Heroku` buffering server in front of your `psiTurk` gunicorn instance, which helps with performance a little bit (although it would be better to put nginx in front of gunicorn within the `psiTurk` instance).

One downside with `Heroku` is that it can get expensive if you need any kind of horsepower beyond 512MB memory and one node.

What follows is a step-by-step tutorial for setting up a `psiTurk` example experiment on `Heroku` (both the experiment itself and ad) with a `PostgreSQL` database for collecting data:

#. Go to the `Heroku website <http://www.heroku.com>`_ and create a new account if you don't already have one.

#. Make sure that `psiTurk <install.html>`_, `git <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>`_, and the `Heroku Command Line Interface <https://devcenter.heroku.com/articles/heroku-cli>`_ are installed on your computer.

#. Create a psiTurk example at a desired location (all commands listed in this tutorial are meant to be typed into your terminal application): ::

    psiturk-setup-example

#. Navigate into your newly created psiTurk example folder: ::

    cd psiturk-example

#. Initialize a Git repository inside the psiTurk example folder: ::

    git init

#. Log in to `Heroku` (and put in your credentials when promted for them):  ::

    heroku login

#. Create a new app on `Heroku` (this command will also set this app as the default remote location for your newly created `Git` repository): ::

    heroku create

#. Create a Postgres database on the newly created `Heroku` app: ::

    heroku addons:create heroku-postgresql

#. Get the URL of the Postgres database that you just created: ::

    heroku config:get DATABASE_URL

#. Get the URL of your app: ::

    heroku domains

#. In your psiTurk example, open the `config.txt` file. Here, find and make the following settings for the these rows (make sure to remove the `#` sign before `adserver_revproxy_host`), and then save the file: ::

    database_url = <Your Postgres database URL that you retrieved above>
    host = 0.0.0.0
    threads = 1
    adserver_revproxy_host = <Your app URL that you retrieved above>
    ad_location = https://<Your app URL that you retrieved above>/pub
    use_psiturk_ad_server = false

#. Run the following commands, replacing `<XYZ>` with your access and secret keys for `Amazon Web Services <amt_setup.html#obtaining-aws-credentials>`_ and `psiTurk Secure Ad Server <psiturk_org_setup.html#obtaining-psiturk-org-api-credentials>`_ (you can also use `this Python script <https://github.com/NYUCCL/psiTurk/blob/908ce7bcfc8fb6b38d94dbae480449324c5d9d51/psiturk/example/set-heroku-settings.py>`_ to automatically run these commmands, provided that you've filled out your credentials in your .psiconfig file): ::

    heroku config:set ON_HEROKU=true
    heroku config:set psiturk_access_key_id=<XYZ>
    heroku config:set psiturk_secret_access_id=<XYZ>
    heroku config:set aws_access_key_id=<XYZ>
    heroku config:set aws_secret_access_key=<XYZ>

#. Stage all the files in your psiTurk example to your Git repository: ::

    git add .

#. Commit all the staged files to your Git repository: ::

    git commit -m "Initial commit"

#. Push the code to your `Heroku` app, which then auto runs the code: ::

    git push heroku master

#. Run `psiTurk` locally on your machine: ::

    psiturk

From your local `psiTurk` session, you can now `create and modify HIT's <command_line/hit.html>`_. When these are accessed by Amazon Mechanical Turk workers, the workers will be directed to the `psiTurk` session running on your `Heroku` app. This means that you safely can close your local psiTurk session once you're done creating and modifying HIT's.
