Configuration Files
===================

There are two types of configuration files for **psiTurk**.
Configuration files contain information needed to run an experiment
as well as options which control how **psiTurk** behaves.

The first file is a "global" configuration file and resides
in your home folder (`~/.psiturkconfig`).  The second file is
a "local" configuration file and resides in the folder of 
each experiment.

In general the "global" configuration file sets project-wide
configuration options (i.e., those you want set the same
for all the experiments or projects you are working on).
The "local" configuration file contains the unique settings for
individual experiments.

In general, changes to either the local and global file
require restarting the server process as it may change
the behavior.  Generally it is best to edit these files while
psiturk is not running, and then restart the command shell.

Global configuration file
--------------------------

The global configuration file resides in your
home folder in a "dot" file (`/.psiturkconfig`).  This
file is created automatically either the first time you
run the `psiturk` command line tool or the first time
you run `psiturk-setup-example`.  The default file looks
like this:

::

	[AWS Access]
	aws_access_key_id = YourAccessKeyId
	aws_secret_access_key = YourSecretAccessKey
	aws_region = us-east-1

	[psiTurk Access]
	psiturk_access_key_id = YourAccessKeyId
	psiturk_secret_access_id = YourSecretAccessKey


Other options can be added if you would like those
to be global to all your projects.  The default options
include your access credentials/API keys for 
`Amazon Web Services <amt_setup.html>`__ (and Mechanical Turk) 
as well as `psiturk.org <psiturk_org_setup.html>`__.
You can learn how to obtain proper values for these
settings by following those links.

Local configuration file
--------------------------

The local configuration file is specific to each
project and resides in a file called `config.txt` in the
top level of the project.  Here is what `config.txt`
looks like for the default **psiTurk** `stroop <stroop.html>`__ 
project:

::

	[HIT Configuration]
	title = Stroop task
	description = Judge the color of a series of words.
	amt_keywords = Perception, Psychology
	lifetime = 24
	us_only = true
	approve_requirement = 95
	contact_email_on_error = youremail@gmail.com
	ad_group = My research project
	psiturk_keywords = stroop
	organization_name = New Great University
	browser_exclude_rule = MSIE, mobile, tablet
	using_sandbox = False

	[Database Parameters]
	database_url = sqlite:///participants.db
	table_name = turkdemo

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

	[Task Parameters]
	experiment_code_version = 1.0
	num_conds = 1
	num_counters = 1

	[Shell Parameters]
	always_launch_in_sandbox = true

This file is divided into a few sections which are
described in detail in the following subsections


HIT Configuration
^^^^^^^^^^^^^^^^^

The HIT Configuration section contains details about
your Human Intelligence Task.  An example looks
like this:

::

	[HIT Configuration]
	title = Stroop task
	description = Judge the color of a series of words.
	amt_keywords = Perception, Psychology
	lifetime = 24
	us_only = true
	approve_requirement = 95
	contact_email_on_error = youremail@gmail.com
	ad_group = My research project
	psiturk_keywords = stroop
	organization_name = New Great University
	browser_exclude_rule = MSIE, mobile, tablet
	using_sandbox = False


title [string]
""""""""""""""
The `title` is the title of the task that will appear on the AMT
worker site.  Workers often use these fields to
search for tasks.  Thus making them descriptive and
informative is helpful.


description [string]
""""""""""""""
The `description` is the accompanying
text that appears on the AMT site. Workers often use these fields to
search for tasks.  Thus making them descriptive and
informative is helpful.

keywords [comma separated string]
"""""""""""""""""""""""""""""""""
`keywords` Workers often use these fields to
search for tasks.  Thus making them descriptive and
informative is helpful.

lifetime [integer]
"""""""""""""""""""""""""""""""""
The `lifetime` how long a worker can "hold on" to your
HIT for.  Sometimes workers will "accept" a HIT which is worth
a lot of money but come back and do the work later in the day.
The lifetime sets a limit on the length of time a worker
can hold onto an assignment.  

us_only [true | false]
"""""""""""""""""""""""
`us_only` controls
if you want this HIT only to be available to US Workers.  This is
not a failsafe restriction but works fairly well in practice.

approve_requirement [integer]
""""""""""""""""""""""""""""""
`approve_requirement` sets a qualification for what type of workers
you want to allow to perform your task.  It is expressed as a 
percentage of past HITs from a worker which were approved.  Thus
95 means 95% of past tasks were successfully approved.  You may want
to be careful with this as it tends to select more seasoned and
expert workers.  This is desirable to avoid bots and scammers, but also
may exclude new sign-ups to the system.

contact_email_on_error [string - valid email address]
"""""""""""""""""""""""""""""""""""""""""""""""""""""
`contact_email_on_error`  is the email you would like to display to
workers in case there is an error in the task.  Workers will often try
to contact you to explain what when want and request partial or full
payment for their time.  Providing a email address that you monitor
regularly is important to being a good member of the AMT community.

ad_group [string]
"""""""""""""""""
`ad_group`  is a unique string that describes your experiment.
All HITs and Ads with the same ad_group string will be grouped together
in your psiturk.org dashboard.  To create a new group in your dashboard
simply create a new unique string.  The best practice is to group all
experiments from the same "project" with the same `ad_group` but assign
different `ad_group` identifiers to different project (e.g., if two
students in a lab were working on different things but shared a psiturk.org
account then they might use different `ad_group` identifiers to keep
things organized.)

psiturk_keywords [comma separated string]
""""""""""""""""""""""""""""""""""""""""""
`psiturk_keywords` [string, comma separated] are a list of key words
that describe your task.  The purpose of these keywords (distinct from 
the `keywords` described above) is to help other researchers know 
what your task involves.  For example, you might include the keyword
`deception` if your experiment involves deception.  If it involves a
common behavioral task like `trolly problems` you might include that 
as well.  In the future we hope to allow researchers to query information
about particular workers and task to find out if your participants
are naive to particular types of manipulations.  You should be careful
not to include too general of terms here.  For example, a researcher
might want to exclude people who in the past had participated in a 
psychology study involving deception.  They probably don't care to
exclude people who did a "decision making task".  Thus, being specific
and using important keywords that are likely to be recognized by the
research community is the best approach.   (Ask yourself, if I wanted
to exclude people who had done this study from a future study what
keywords would I search for.)

organization_name [string]
""""""""""""""""""""""""""
`organization_name` [string] is just an identifier of your academic
institution, business, or organization.  It is used internally
by psiturk.org.

browser_exclude_rule [comma separated string]
""""""""""""""""""""""""""""""""""""""""""""""
`browser_exclude_rule` is a set of rules you can apply to exclude
particular web browsers from performing your task.  When a users
contact the `Secure Ad Server <secure_ad_server>`__ the server checks
to see if the User Agent reported by the browser matches any of the
terms in this string.  It if does the worker is shown a message
indicating that their browser is incompatible with the task.

Matching works as follows.  First the string is broken up
by the commas into sub-string.  Then a string matching rule is 
applied such that it counts as a match anytime a sub-string
exactly matches in the UserAgent string.  For example, a user
agent string for Internet Explorer 10.0 on Mac OS X might looks like this:

::

Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)

This browser could be excluded by including this full line (see `this website <http://www.useragentstring.com/pages/Browserlist/>`__ for a partial list of UserAgent strings).  Also
"MSIE" would match this string or "Mozilla/5.0" or "Mac OS X" or "Trident".
Thus you should be careful in applying these rules.

There are also a few special terms that apply to a cross section of browsers.
`mobile` will attempt to deny any browser for a mobile device (including
cell phone or tablet).  This matching is not perfect but can be more general
since it would exclude mobile version of Chrome and Safari for instance.
`tablet` denys tablet based computers (but not phones).  `touchcapable` would
try to exclude computers or browser with gesture or touch capabilities
(if this would be a problem for your experiment interface).  `pc` denies 
standard computers (sort of the opposite to the `mobile` and `tablet` exclusions).
Finally `bot` tries to exclude web spiders and non-browser agents like
the Unix curl command.

using_sandbox [true | false]
"""""""""""""""""""""""""""""
`using_sandbox` indicates if HITs for this task should be posted to
the sandbox or "live" AMT site.  This variable can be modified while
psiturk is running by typing `mode` at the `command line <command_line_overview>`__.



Database Parameters
^^^^^^^^^^^^^^^^^^^

The Database Parameter section contains details about
your database.  An example looks like this:

::

	[Database Parameters]
	database_url = sqlite:///participants.db
	table_name = turkdemo

database_url [url string]
"""""""""""""""""""""""""""""
`database_url` containes the location and access credentials
for your database (i.e., where you want the data from your
experiment to be saved).  
As described in the `database <configure_databases.html>`__
section there are a variety of options.

To use a SQLLite data base, simply type the name of the
file::

	database_url = sqlite:///participants.db

This example would write to a database file with the name
"participants.db" in the top-level directory of your experiment.

To use an existing MySQL database::

	database_url = mysql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE

where USERNAME and PASSWORD are your access credentials for
the database, HOSTNAME and is the DNS entry or IP address for the
database, PORT is the port number (standard is 3306) and DATABASE
is the name of the database on the server.  It is wise to test
that you can connect to this url with a MySQL client prior to 
launching.

table_name [ string]
"""""""""""""""""""""""""""""
`table_name` specifies the table of the database you would like
to write to.  **IMPORTANT**: psiTurk prevents the same worker
from performing as task by checking to see if the worker
appears in the current database table already.  Thus, for a
single experiment (or sequence of related experiments) you want
to keep the `table_name` value the same.  If you start a new
design where it not longer matters that someone has done a 
previous version of the task, you can change the `table_name`
value and begin sorting the data into a new table.


Server Parameters
^^^^^^^^^^^^^^^^^^^

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

host [ string]
"""""""""""""""""""""""""""""
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

host [ integer ]
"""""""""""""""""""""""""""""
This is the port that your server will run on.  Typically
a number greater than 5000 will work.  If another process
is already using a given port you will usually get an
error message.

cutoff_time [ integer ]
"""""""""""""""""""""""""""""

logfile [ string ]
"""""""""""""""""""""""""""""
The location of the server log file.  Error messages for
the server process are not printed to the terminal or 
command line.  To help in debugging they are stored in
a log file of your choosing.  This file will be located
in the top-level folder of your project.


loglevel [ integer ]
"""""""""""""""""""""""""""""
Sets how "verbose" the log messages are.  See
the python `logging <http://docs.python.org/2/library/logging.html#logging-levels>`__
library.

debug [ true | false ]
"""""""""""""""""""""""""""""
If debug is true, if there is an internal server error
helpful debugging information will be printed into the webpage of
people taking the experiment.  **IMPORANT** this should be 
set to false for live experiments to prevent possible security
holes.

login_username [ string ]
"""""""""""""""""""""""""""""
If you want to have  custom-login section of your
web application (e.g., see `customizing psiturk <customize.txt>`__)
then you can set a login and password on certain
web pages urls/routes.  By default if you aren't
using them, this is ignored.

login_pw  [ string ]
"""""""""""""""""""""""""""""
If you want to have  custom-login section of your
web application (e.g., see `customizing psiturk <customize.txt>`__)
then you can set a login and password on certain
web pages urls/routes.  By default if you aren't
using them, this is ignored.

threads  [ auto | integer ]
"""""""""""""""""""""""""""""
`threads` controls the number of process threads
the the psiturk webserver will run.  This enables multiple
simultanous connections from internet users.  If you select
`auto` it will set this based on the number of processor
cores on your current computer.


Task Parameters
^^^^^^^^^^^^^^^^^^^

The Task Parameters section contains details about
your task.  An example looks like this:

::

	[Task Parameters]
	experiment_code_version = 1.0
	num_conds = 1
	num_counters = 1

experiment_code_version  [ string ]
"""""""""""""""""""""""""""""
Often you might a couple different versions
of an experiment during a research project (e.g.,
Experiment 1 and 2 of a papper).  
`experiment_code_version` is a string which is written into
the database along with your data helping you remember which
version of the code each participant was given.


num_cond  [ integer ]
"""""""""""""""""""""""""""""
**psiTurk** includes a primitive system for counterbalancing
participants to conditions.  If you specify a number of
condition greater than 1, then **psiTurk** will attempt to
assign new participants to conditions to keep them all
with equal N.  It also takes into account the time delay
between a person being assigned to a condition and completing
a condition (or possibly withdrawing).  Thus, you can be
fairly assured that after running 100 subjects in two conditions
each condition will have 50+/- completed participants.

num_counters  [ integer ]
"""""""""""""""""""""""""""""
`num_counters` is identical to `num_cond` but provides
an additional counterbalancing factor beyond condition.
If `num_counters` is greater than 1 then **psiTurk**
behaves as if there are `num_cond*num_counters` conditions
and assigns subjects randomly to the the expanded design.
See `Issue #53 <https://github.com/NYUCCL/psiTurk/issues/53>`__
for more info.


Shell Parameters
^^^^^^^^^^^^^^^^^^^

The Shell Parameters section contains details about
the psiturk shell.

::
	[Shell Parameters]
	always_launch_in_sandbox = true

always_launch_in_sandbox  [ true | false]
"""""""""""""""""""""""""""""
If set to `true` this option will cause the psiturk shell
to always launch in sandbox mode.  This is to avoid
errors where the user "forgets" that they are "live".
This means you interact with the live AMT site you
must manually switch the mode each time.  Otherwise
psiturk will use the setting of the `using_sandbox`
described `above <configuration.html#using-sandbox-true-false>`__.