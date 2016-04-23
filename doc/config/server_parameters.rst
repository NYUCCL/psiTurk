Server Parameters
=================

The Server Parameter section contains details about
your local web server process that you launch from the
command line.  An example looks like this:

::

    [Server Parameters]
    host = 0.0.0.0
    port = 22362
    cutoff_time = 30
    logfile = server.log
    loglevel = 2
    debug = true
    login_username = examplename
    login_pw = examplepassword
    threads = auto
    #certfile = <path_to.crt> 
    #keyfile = <path_to.key>

`host` [ string]
--------------
`host` specifies the hostname of your server.
There are really only two meaningful values of this.
If host is set to 'localhost' or '127.0.0.1' then your
experiment will only work for testing (i.e., even if you
have an internet addressable computer, people outside
of your local machine will not be able to connect).  This
is a security feature for developing and testing your 
application.

If `host` is set to `0.0.0.0` or the actual ip address
or hostname of your current computer then your task
will be available to the general internet.

`port` [ integer ]
----------------
This is the port that your server will run on.  Typically
a number greater than 5000 will work.  If another process
is already using a given port you will usually get an
error message.

`cutoff_time` [ integer ]
-----------------------
Maximum time in minutes to finish the task. The connection 
will be closed after this time is up.

`logfile` [ string ]
------------------
The location of the server log file.  Error messages for
the server process are not printed to the terminal or 
command line.  To help in debugging they are stored in
a log file of your choosing.  This file will be located
in the top-level folder of your project.


`loglevel` [ integer ]
--------------------
Sets how "verbose" the log messages are.  See
the python `logging <http://docs.python.org/2/library/logging.html#logging-levels>`__
library.

`debug` [ true | false ]
----------------------
If debug is true, if there is an internal server error
helpful debugging information will be printed into the webpage of
people taking the experiment.  **IMPORANT** this should be 
set to false for live experiments to prevent possible security
holes.

`login_username` [ string ]
-------------------------
If you want to have  custom-login section of your
web application (e.g., see `customizing psiturk <../customizing.html>`__)
then you can set a login and password on certain
web pages urls/routes.  By default if you aren't
using them, this is ignored.

`login_pw`  [ string ]
--------------------
If you want to have  custom-login section of your
web application (e.g., see `customizing psiturk <../customizing.html>`__)
then you can set a login and password on certain
web pages urls/routes.  By default if you aren't
using them, this is ignored.

`threads`  [ auto | integer ]
---------------------------
`threads` controls the number of process threads
the the psiturk webserver will run.  This enables multiple
simultanous connections from internet users.  If you select
`auto` it will set this based on the number of processor
cores on your current computer.

`certfile` [ string ]
----------------------
.. warning::
    
    SSL support for the psiturk server is an experimental feature.

`certfile` should be the /path/to/your/domain/SSL.crt
    
If both certfile and keyfile are set and the files readable, then 
the psiturk gunicorn server will run with ssl. You will need 
to execute the psiturk with privileges sufficient to read 
the keyfile (typically root). If you run `psiturk` with `sudo` and if you are using
a virtual environment, make sure to execute the full path to the desired psiturk instance in your environment. 
See `launch-sudo-psiturk in this gist`_ for an example.

If you want to do this, you are responsible for obtaining 
your own cert and key. It is not necessary to run the 
psiturk server with `ssl` in order to use your own ad server.
You can have a proxy server such as `nginx` in front of 
psiturk/gunicorn which handles ssl connections. See `this gist`_ for an example.

See http://docs.gunicorn.org/en/stable/deploy.html for more information on setting up proxy servers with the psiturk (gunicorn) server.

.. seealso::

    `use_psiturk_ad_server <shell_parameters.html#use-psiturk-ad-server-true-false>`__
        How to use your on ad_location. Does not require that the **psiTurk** server be SSL-enabled. (Although you will still need your own SSL certificate and key)

`keyfile` [ string ]
----------------------
.. warning::
    
    SSL support for the psiturk server is an experimental feature.

`certfile` should be the /path/to/your/domain/private-SSL.key. Although .crts can contain .key files within them,
psiturk currently requires that you point to separate .crt and .key files for this experimental feature to work.

See the documentation for `certfile` for more information.

.. _launch-sudo-psiturk in this gist: gist_
.. _this gist: gist_
.. _gist: https://gist.github.com/deargle/5d8c01660a77b8090a2cd24efcda2c59