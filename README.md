
What is this?
------------

PsiTurk is an open platform for conducting custom behvioral experiments on
Amazon's Mechanical Turk. 

It is intended to provide most of the backend machinery necessary to run your
experiment. It uses AMT's _External Question_ HIT type, meaning that you can
collect data using any website. As long as you can turn your experiment into a
website, you can run it with PsiTurk!

Dependencies
------------

You will need to use a relatively recent version of [Python
2](http://python.org) with the following modules installed:

 * [Flask](http://flask.pocoo.org/) --- A lightweight web framework.
 * [SQLAlchemy](http://www.sqlalchemy.org/) --- A powerful SQL abstraction layer.

You will also need to run this from a web server connected to the internet, and
you will need a database compatible with SQL Alchemy (MySQL, SQLite, or
PostgreSQL would all work).

Quick Start
-----------

Just follow these directions to get started:

1. Installing the dependencies, including the database. 
2. Sign up for Mechanical Turk, including an AWS account.
3. Move the config file from `config.txt.example` to `config.txt`. Update it
   with your Amazon secret code and a correct URL to your database (the default
   database URL is set up for [MAMP](http://mamp.info) on OSX). 
4. Making sure that the configuration file is set up to use the Amazon sandbox,
  issue the following commands from the PsiTurk root folder:

        python mturk/createHIT.py    # To post a HIT to the sandbox
        python app.py                # To start the web server

5. You should be ready to go! Point your browser to the [worker
  sandbox](https://workersandbox.mturk.com) and try to find your HIT!

Copyright
---------
You are welcome to use this code for personal or academic uses. If you fork,
please cite the authors (Todd Gureckis and John McDonnell).



