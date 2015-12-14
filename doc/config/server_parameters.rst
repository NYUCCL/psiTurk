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
