
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
 * [boto](https://github.com/boto/boto) --- A library for interfacing with
   Amazon services, including MTurk.
 
You can install these with the following commands:

    easy_install Flask-SQLAlchemy
    easy_install boto

To serve your experiment to participants online, you will need to run this code
from a web server connected to the internet.

Quick Start
-----------

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

Deployment
----------
We STRONGLY recommend you not deploy your experiment using the debugging server
(the one you start using `python app.py`). It is not robust to failures, which
can leave your participants stranded without a way of submitting their
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


Copyright
---------
You are welcome to use this code for personal or academic uses. If you fork,
please cite the authors (Todd Gureckis and John McDonnell).



