
What is this?
============

PsiTurk is an open platform for conducting custom behvioral experiments on
Amazon's Mechanical Turk. 

It is intended to provide most of the backend machinery necessary to run your
experiment. It uses AMT's _External Question_ HIT type, meaning that you can
collect data using any website. As long as you can turn your experiment into a
website, you can run it with PsiTurk!

Dependencies
============

You will need to use a relatively recent version of [Python
2](http://python.org) with the following modules installed:

 * [Flask](http://flask.pocoo.org/) – A lightweight web framework.
 * [SQLAlchemy](http://www.sqlalchemy.org/) – A powerful SQL abstraction layer.
 * [Boto](https://github.com/boto/boto) – A library for interfacing with
   Amazon services, including MTurk.
 
You can install these with the following commands:

    easy_install Flask-SQLAlchemy
    easy_install boto

To serve your experiment to participants online, you will need to run this code
from a web server connected to the internet.

Quick Start
===========

Just follow these directions to get started:

1. Install the dependencies. 
2. Sign up for an AWS account, available [here](http://aws.amazon.com/).
3. Sign up for a Mechanical Turk requester account, available
   [here](https://requester.mturk.com/).
4. Rename the config file from `config.txt.example` to `config.txt`. Update it
   with your secret AWS code.
5. Making sure that the configuration file is set up to use the Amazon sandbox,
   issue the following commands from the PsiTurk root folder:

        python mturk/createHIT.py    # To post a HIT to the sandbox
        python app.py                # To start the debugging server

6. You should be ready to go! Point your browser to the [worker
   sandbox](https://workersandbox.mturk.com/mturk/findhits) and try to find your
   HIT.

*Note*: If you are just testing the server without posting your HIT to Amazon,
you can see the experiment at the following link:
http://localhost:5001/mturk?assignmentId=debug&hitId=debug&workerId=debug


Experiment design
=================

We have provided an example stroop experiment that could form the basis of your
own experiment. It is a Javascript experiment, with task logic inside the
participant's browser using Javascript code in `static/task.js`. This
Javascript code works by dynamically changing the html document served to
participants in `templates/exp.html`. PsiTurk assigns a condition and
counterbalance to each participant. These are fed into JavaScript by plugging
them into `templates/exp.html`. PsiTurk actively manages the condition and
counterbalance subjects are assigned to, helping you fill them in evenly. To
tell PsiTurk how many conditions and counterbalance identities are possible in
your experiment, adust `num_conds` and `num_counters` in `config.txt`.

Deployment
==========

Configuration
------------
To make your experiment available on the internet, you will need to make the
following changes to the configuration file:

    host: 0.0.0.0
    question_url: http://yoururl:yourport/mturk

replacing `yoururl` with the url to your surver, and `yourport` with the port
you have configured in the `config.txt` file (by default, 5001).


Server
------
We **strongly** recommend you not deploy your experiment using the debugging
server (the one you start using `python app.py`). It is not robust to failures,
which can leave your participants stranded without a way of submitting their
completed HITs. Additionally, if you accidentally leave debug mode on, you will
expose yourself to major security holes.

An alternative we have set up is gunicorn. You can install gunicorn using the
following command:

    easy_install gunicorn

Then simply run using:

    sh run_gunicorn.sh

You can configure gunicorn in the `config.txt` file under `Server Parameters`.

Flask apps like PsiTurk can be deployed as a CGI, fastCGI, or WSGI app on any
server system, so there are many alternative options for deployment.
Additional options for deploying Flask can be found
[here](http://flask.pocoo.org/docs/deploying/).

Database
--------

We recommend using a deployment-robust database solution such as
[MySQL](http://www.mysql.org) or [PostgreSQL](http://www.postgresql.org).
SQLite does not allow concurrent access to the database, so if the locks work
properly, simultaneous access (say, from multiple users submitting their data
at the same time) could destabilize your database. In the worst (unlikely)
scenario, the database could become corrupted, resulting in data loss.

Instructions for setting up a MySQL server on a Mac can be found 
[in the wiki](https://github.com/NYUCCL/psiTurk/wiki/Macintosh-Configuration).
Other platforms, check out instructions at
[mysql.org](http://dev.mysql.com/doc/refman/5.5/en//installing.html).

Copyright
=========
You are welcome to use this code for personal or academic uses. If you fork,
please cite the authors (Todd Gureckis and John McDonnell).



