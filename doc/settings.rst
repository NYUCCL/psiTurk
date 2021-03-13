.. _settings:

========
Settings
========

This page is organized by each of the sections of a ``config.txt`` file.

Any of these settings can be set via an environment variable by setting the
setting name (sans section name) prefixed by the key string ``PSITURK_``. For
instance, to set the number of server threads (:ref:`settings-threads`, section
'Server Parameters') to ``1`` via env var, one would set: ``PSITURK_THREADS=1``.

.. seealso:: :ref:`configuration-overview`

.. contents::
   :local:
   :depth: 1


HIT Configuration
-----------------

The ``[HIT Configuration]`` section contains details about
your Human Intelligence Task.


.. _title:

title
~~~~~

Title of the task that will appear on the AMT
worker site.

:Type: ``string``

Workers often use fields like this one to search for tasks.
Thus making them descriptive and
informative is helpful.


.. _description:

description
~~~~~~~~~~~

Descriptive text for your study's listing on AMT.

:Type: ``string``

Workers often use fields like this one to search for tasks.
Thus making them descriptive and
informative is helpful.

.. _keywords:

keywords
~~~~~~~~

A list of keywords to be associated with your study on AMT.

:Type: comma-delimited ``string``

Workers often use fields like this one to search for tasks.
Thus making them descriptive and
informative is helpful.


.. _lifetime:

lifetime
~~~~~~~~

How long your HIT remains visible to workers (in hours).

:Type: ``integer``

After the lifetime of the HIT elapses, the HIT no longer
appears in HIT searches, even if not all of the assignments for the
HIT have been accepted.

This is in contrast to the HIT ``duration``, which specifies how long
workers have to complete your task, and which you provide at HIT
creation time. See the documentation on `hit create <../command_line/hit.html#hit-create>`__ for more details.


.. _us_only:

us_only
~~~~~~~

Controls if you want this HIT only to be available to US Workers.

:Type: ``bool``

This is not a failsafe restriction but works fairly well in practice.


.. _approve_requirement:

approve_requirement
~~~~~~~~~~~~~~~~~~~

Minimum approval percentage for a worker to be able to accept your study.

:Type: ``integer``

Sets a qualification for what type of workers
you want to allow to perform your task. It is expressed as a
percentage of past HITs from a worker which were approved. Thus
95 means 95% of past tasks were successfully approved. You may want
to be careful with this as it tends to select more seasoned and
expert workers. This is desirable to avoid bots and scammers, but also
may exclude new sign-ups to the system.


.. _number_hits_approved:

number_hits_approved
~~~~~~~~~~~~~~~~~~~~

How many hits a worker must have approved before they can take your study.

:Type: ``integer``

Important to use in conjunction with :ref:`approve_requirement`, because
mturk will default ``approve_requirement`` to 100% until a worker has at least
100 HITs approved. Override that behavior by setting this to at least be 100.


.. _require_master_workers:

require_master_workers
~~~~~~~~~~~~~~~~~~~~~~

If True, Will make it so that only workers with the "Master" qualification
can take your study.

:Type: ``bool``

See `Who Are Amazon Mechanical Turk Masters? <https://www.mturk.com/help#what_are_masters>`__

**Note:** Master workers cost an extra 5%.



.. _browser_exclude_rule:

browser_exclude_rule
~~~~~~~~~~~~~~~~~~~~

A set of rules you can apply to exclude
particular web browsers from performing your task.

:Type: comma-delimited ``string``

When a users contact your psiturk server, the server checks
to see if the User Agent reported by the browser matches any of the
terms in this string. It if does the worker is shown a message
indicating that their browser is incompatible with the task.

Matching works as follows. First the string is broken up
by the commas into sub-string. Then a string matching rule is
applied such that it counts as a match anytime a sub-string
exactly matches in the UserAgent string. For example, a user
agent string for Internet Explorer 10.0 on Mac OS X might looks like this::

  Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)

This browser could be excluded by including this full line (see `this website`__
for a partial list of UserAgent strings). Also, "MSIE" would match this string
or "Mozilla/5.0" or "Mac OS X" or "Trident". Thus you should be careful in
applying these rules.

__ https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent

There are also a few special terms that apply to a cross section of browsers.
`mobile` will attempt to deny any browser for a mobile device (including
cell phone or tablet). This matching is not perfect but can be more general
since it would exclude mobile version of Chrome and Safari for instance.
`tablet` denys tablet based computers (but not phones). `touchcapable` would
try to exclude computers or browser with gesture or touch capabilities
(if this would be a problem for your experiment interface). `pc` denies
standard computers (sort of the opposite to the `mobile` and `tablet` exclusions).
Finally `bot` tries to exclude web spiders and non-browser agents like
the Unix curl command.


.. _allow_repeats:

allow_repeats
~~~~~~~~~~~~~

Specifies whether participants may complete the experiment more
than once.

:Type: ``bool``
:Default: ``false``

If it is set to `false` (the default), then participants will be
blocked from completing the experiment more than once. If it is set to `true`,
then participants will be able to complete the experiment any number of times.

Note that this option does not affect the behavior when a participant starts
the experiment but the quits or refreshes the page. In those cases, they will
still be locked out, regardless of the setting of `allow_repeats`.

.. _whitelist_qualification_ids:

whitelist_qualification_ids
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of custom qualifications that participants must possess to
perform your task.

:Type: comma-delimited ``string``

You may need to ensure that workers have some requisite skill or pass some
previous screening factors, such as language proficiency or having already
completed one of your tasks.  AMT uses custom qualification types to perform
this filtering. When you add a custom qualification to
`whitelist_qualification_ids`, AMT will only show your ad to potential
participants who already have that qualification set.  Other MTurk workers will
neither see your ad nor be able to accept the HIT.

See `Managing worker cohorts with qualifications
<https://blog.mturk.com/tutorial-managing-worker-cohorts-with-qualifications-e928cd30b173>`_
and `Best practices for managing workers in follow-up surveys <https://blog.mturk.com/tutorial-best-practices-for-managing-workers-in-follow-up-surveys-or-longitudinal-studies-4d0732a7319b>`_
for additional details on custom qualifications.


.. _blacklist_qualification_ids:

blacklist_qualification_ids
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A list of custom qualifications that participants must not possess to
perform your task.

:Type: comma-delimited ``string``

When you add a custom qualification to `blacklist_qualification_ids`, MTurk
workers with that qualification already set will neither see your ad nor be able
to accept your HIT. This is the recommended way of excluding participants who
have performed other HITs for you from participating in your new HIT.

Hit Configuration -- Ad Url
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Config settings for constructing the task's "landing page" when posting hits on MTurk.


ad_url_domain
^^^^^^^^^^^^^

:Type: ``string``
:Default: ``null``

Server domain name for publicly-accessible route to psiturk server.
If running on heroku, set this to your heroku app url --
for example, if your heroku app name were "example-app," you would set the following::

  ad_url_domain = example-app.herokuapp.com


ad_url_port
^^^^^^^^^^^

:Type: ``int``
:Default: 80

Server port for publicly-accessible route to psiturk server


ad_url_protocol
^^^^^^^^^^^^^^^

:Type: ``string``
:Default: 'https'

HTTPS protocol is required by mturk. Only change this if you have a good reason
to do so.


ad_url_route
^^^^^^^^^^^^

:Type: ``string``
:Default: 'pub'

Flask route that points to the ad. "pub" and "ad" both point to the same place,
but "pub" is safer because of potential issues with ad blockers with a route
named "ad"


ad_url
^^^^^^


Alternatively, instead of using ``ad_url_*`` config vars above,
you may use ``ad_url``. You may want to use this if your
experiment is served from a subdirectory off of the domain name. Otherwise,
leave this as-is. By default, it is dynamically built using the other variables in this section,
using ConfigParser templating as follows::

  %(ad_url_protocol)s://%(ad_url_host)s:%(ad_url_port)s/%(ad_url_route)s




Database Parameters
-------------------

The ``[Database Parameter]`` section contains details about
your database.

.. seealso::

   `Configuring Databases <../databases_overview.html>`__
      For details on how to set up different databases and
      get your data back out.

   `Recording Data <../recording.html>`__
   	  For details on how to put data into your database.


.. _settings-database-url:

database_url
~~~~~~~~~~~~

`database_url` contains the location and access credentials
for your database (i.e., where you want the data from your
experiment to be saved).

:Type: ``string`` - valid database url

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
is the name of the database on the server. It is wise to test
that you can connect to this url with a MySQL client prior to
launching.


table_name
~~~~~~~~~~

Specifies the table of the database you would like to write to.

:Type: ``string``

**IMPORTANT**: psiTurk prevents the same worker
from performing as task by checking to see if the worker
appears in the current database table already. Thus, for a
single experiment (or sequence of related experiments) you want
to keep the `table_name` value the same. If you start a new
design where it not longer matters that someone has done a
previous version of the task, you can change the `table_name`
value and begin sorting the data into a new table.




Server Parameters
-----------------

The ``[Server Parameter]`` section contains details about
your local web server process that you launch from the
command line.


host
~~~~

Specifies the network address to which your server should bind
(i.e., on which address it should listen).

:Type: ``string``

There are two common values for this.
If host is set to ``localhost`` (or synonymously ``127.0.0.1``), then your
experiment will only work for testing (i.e., even if you
have an internet addressable computer, people outside
of your local machine will not be able to connect). This
is a security feature for developing and testing your
application.

If set to `0.0.0.0`, then your psiturk server will be accessible
to any traffic that can reach the computer on which your server is running. If
your server has a public-internet interface, then participants anywhere in the
world can access your study.


port
~~~~

The port that your server will run on.

:Type: ``integer``

If not running as ``root``, must be greater than 1024. Max 65535.
Typically a number greater than 5000 will work. If another process
is already using a given port you will usually get an
error message.

.. _settings-logfile:

logfile
~~~~~~~

:Type: ``string``

The location of the server log file. Error messages for
the server process are not printed to the terminal or
command line. To help in debugging they are stored in
a log file of your choosing. This file will be located
in the top-level folder of your project.


loglevel
~~~~~~~~

:Type: ``integer``

Sets how "verbose" the log messages are. See
the python `logging <https://docs.python.org/3/library/logging.html>`__
library.


.. _settings-enable-dashboard:

enable_dashboard
~~~~~~~~~~~~~~~~

Whether to enable the dashbaord. If True, then the ``login_username`` and
``login_pw`` must also be set.

:Type: ``bool``
:Default: False


.. _settings-do-scheduler:

do_scheduler
~~~~~~~~~~~~

Whether to run the task scheduler, which is viewable and configurable from the
dashboard.

:Type: ``bool``
:Default: False

Tasks are loaded from the database. If True, then :ref:`settings-threads` must
be no greater than 1, because the task runner is not threadsafe. Will only run
while the psiturk server is running.



.. _settings-login-username:

login_username
~~~~~~~~~~~~~~

:Type: ``string``

If you want to have custom-login section of your
web application (e.g., see `customizing psiturk <../customizing.html>`__)
then you can set a login and password on certain
web pages urls/routes. By default if you aren't
using them, this is ignored.


.. _settings-login-pw:

login_pw
~~~~~~~~

:Type: ``string``

If you want to have  custom-login section of your
web application (e.g., see `customizing psiturk <../customizing.html>`__)
then you can set a login and password on certain
web pages urls/routes. By default if you aren't
using them, this is ignored.


.. _settings-threads:

threads
~~~~~~~

:Type: the ``string`` 'auto' or ``integer``

`threads` controls the number of process threads
the the psiturk webserver will run. This enables multiple
simultanous connections from internet users. If you select
`auto` it will set this based on the number of processor
cores on your current computer.


certfile
~~~~~~~~

Public ssl certificate for the psiturk server to use.

:Type: ``path``

`certfile` should be the /path/to/your/domain/SSL.crt

If both certfile and keyfile are set and the files readable, then
the psiturk gunicorn server will run with ssl. You will need
to execute the psiturk with privileges sufficient to read
the keyfile (typically root). If you run `psiturk` with `sudo` and if you are using
a virtual environment, make sure to execute the full path to the desired psiturk instance in your environment.

If you want to do this, you are responsible for obtaining
your own cert and key. It is not necessary to run the
psiturk server with `ssl` in order to use your own ad server.
You can have a proxy server such as `nginx` in front of
psiturk/gunicorn which handles ssl connections.

**However, if you configure the psiturk server to run with SSL by setting the
`certfile` and `keyfile` here, you must use a proxy server in front of psiturk
to serve the content in your /static folder. An SSL-enabled psiturk/gunicorn
server will not serve static content -- it will only serve dynamic content.**

See https://docs.gunicorn.org/en/stable/deploy.html for more information on
setting up proxy servers with the psiturk (gunicorn) server.


keyfile
~~~~~~~

Private ssl certificate for the psiturk server to use.

:Type: ``path``

`certfile` should be the /path/to/your/domain/private-SSL.key. Although .crts
can contain .key files within them,
psiturk currently requires that you point to separate .crt and .key files for
this feature to work.

See the documentation for `certfile` for more information.



server_timeout
~~~~~~~~~~~~~~

:Type: ``integer``
:Default: 30

Number of seconds gunicorn will wait before killing an unresponsive worker.
This timeout applies to any individual request.

If you expect that your experiment may take more than 30 seconds to respond to
a request, you may want to increase this.

.. note::
    See https://docs.gunicorn.org/en/stable/settings.html#timeout for more information.



Task Parameters
---------------

The ``[Task Parameters]`` section contains details about
your task.


.. _settings-experiment-code-version:

experiment_code_version
~~~~~~~~~~~~~~~~~~~~~~~

:Type: ``string``

Often you might run a couple different versions
of an experiment during a research project (e.g.,
Experiment 1 and 2 of a paper). Or, perhaps you make modifications to a single
study after having already begun data collection.

`experiment_code_version` is a string which is written into
the database along with your data helping you remember which
version of the code each participant was given.

This variable is used by the server along with `num_conds` and `num_counters` to
ensure an equal number of workers per condition for the current
`experiment_code_version`. In other words, changing the experiment_code_version
resets the number of workers per condition to [0 0].


num_conds
~~~~~~~~~

:Type: ``integer``

psiTurk includes a primitive system for counterbalancing
participants to conditions. If you specify a number of
condition greater than 1, then psiTurk will attempt to
assign new participants to conditions to keep them all
with equal N. It also takes into account the time delay
between a person being assigned to a condition and completing
a condition (or possibly withdrawing). Thus, you can be
fairly assured that after running 100 subjects in two conditions
each condition will have 50+/- completed participants.

.. note::

    If you want to reset the random assignment when changing `num_conds`, update the `experiment_code_version`.


num_counters
~~~~~~~~~~~~

:Type: ``integer``

`num_counters` is identical to `num_cond` but provides
an additional counterbalancing factor beyond condition.
If `num_counters` is greater than 1 then psiTurk
behaves as if there are `num_cond*num_counters` conditions
and assigns subjects randomly to the the expanded design.
See `Issue #53 <https://github.com/NYUCCL/psiTurk/issues/53>`__
for more info.


.. _contact_email_on_error:

contact_email_on_error
~~~~~~~~~~~~~~~~~~~~~~

The email you would like to display to
workers in case there is an error in the task.

:Type: ``string``, valid email address

Workers will often try
to contact you to explain what when want and request partial or full
payment for their time. Providing a email address that you monitor
regularly is important to being a good member of the AMT community.


cutoff_time
~~~~~~~~~~~

Maximum time in minutes that it should take for a participant to
finish the task.

:Type: ``integer``

Exclusively used in determining random assignment -- basically, how long should
a participant be given to complete the task after starting? How long should the
task last? This is different than the `duration` specified when running
`hit create`, because a participant may not start the task immediately after
accepting it, while the hit `duration` starts ticking as soon as the hit is
accepted (some workers queue their accepted hits before starting it).




Shell Parameters
----------------

The ``[Shell Parameters]`` section contains details about
the psiturk shell.


launch_in_sandbox_mode
~~~~~~~~~~~~~~~~~~~~~~

:Type: ``bool``

If set to `true`, the psiturk shell will launch in sandbox mode. if set to
`false`, the shell will launch in live mode. We recommend leaving this option
to `true` to lessen the chance of accidentally posting a live HIT to mTurk.



bonus_message
~~~~~~~~~~~~~

:Type: ``string``

If set, automatically uses this string as the message to
participants when bonusing them for an assignment. If not set, you will be
prompted to type in a message each time you bonus participants. (This message is
required by AMT.)
