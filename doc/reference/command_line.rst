.. _command-line:

psiTurk commands
================

Each of these commands can be run either from an interactive shell, or as
arguments to the psiturk command (e.g., ``psiturk amt_balance`` or
``psiturk hit create 1 0.01 1`` from a bash prompt).

.. seealso:: :ref:`command-line-overview`

.. contents:: Commands
  :local:
  :depth: 1


``amt_balance``
~~~~~~~~~~~~~~~

Displays your current AMT balance, or your worker sandbox balance
(always $10,000.00) if you are in sandbox mode.

An example of checking your balance in sandbox mode::

  [psiTurk server:off mode:sdbx #HITs:1]$ amt_balance
  $10,000.00

``config``
~~~~~~~~~~

Used with a variety of subcommands to control the
current configuration context.

.. contents:: Commands
    :local:

``config print``
----------------

Prints the current configuration context.

Example::

  [psiTurk server:off mode:sdbx #HITs:0]$ config print
  [Server parameters]
  threads=auto
  ...
  [Shell parameters]
  launch_in_sandbox_mode=true
  [psiTurk server:on mode:sdbx #HITs:0]$

``config reload``
-----------------

Reloads the current config context (both local and global files). This will
cause the server to restart.

Example::

  [psiTurk server:on mode:sdbx #HITs:0]$ config reload
 	Reloading configuration requires the server to restart. Really reload? y or n: y
 	Shutting down experiment server at pid 82701...
 	Please wait. This could take a few seconds.
 	Experiment server launching...
 	Now serving on http://localhost:22362
  [psiTurk server:off mode:sdbx #HITs:0]$

``config help``
---------------

Display a help message concerning the config subcommand.


``debug``
~~~~~~~~~

Makes it possible to locally test your experiment without contacting Mechanical
Turk servers. Type ``debug`` to automatically launch your experiment in a
browser window. The server must be `running <server.html#server-on>`__ to debug
your experiment. When debugging, the server feature that prevents participants
from reloading the experiment is disabled, allowing you to make changes to the
experiment on the fly and reload the debugging window to see the results.

* ``debug -p, --print-only``

  Use the ``-p`` flag to print a URL to use for debugging the experiment,
  without attempting to automatically launch a browser. This is particularly
  useful if your experiment server is running remotely.

  Example using the ``-p`` flag to request a debug link::

     [psiTurk server:on mode:sdbx #HITs:0]$ debug -p
     Here's your randomized debug link, feel free to request another:
     http://localhost:22362/ad?assignmentId=debugDKSAAE&hitId=debug2YW8RI&workerId=debugM1QUH4
     [psiTurk server:on mode:sdbx #HITs:0]$



.. _command-download-datafiles:

``download_datafiles``
~~~~~~~~~~~~~~~~~~~~~~

Accesses the current experiment database table (defined in `config.txt
<../config/database_parameters.html>`__) and creates a copy of the
experiment data in a csv format. ``download_datafiles`` creates three
files in your current folder:

* ```eventdata.csv``

  Contains events such as window-resizing, and is
  formatted as follows::

    ===============   ===========   ==========  ==========    =========
    column 1          column 2      column 3    column 4      column 5
    ===============   ===========   ==========  ==========    =========
    unique user ID    event type    interval    value         time
    ===============   ===========   ==========  ==========    =========


* ``questiondata.csv``


  Contains data recorded with `psiturk.recordUnstructuredData()
  <../api.html#psiturk-recordunstructureddata-field-value>`__, and is
  formatted as follows::

    ===============   ==============   ==========
    column 1          column 2         column 3
    ===============   ==============   ==========
    unique user ID    question name    response
    ===============   ==============   ==========


* ``trialdata.csv``

  Contains data recorded with `psiturk.recordTrialData()
  <../api.html#psiturk-recordtrialdata-datalist>`__, and is formatted as follows::

    ===============   ===========   ==========  ===========
    column 1          column 2      column 3    column 4
    ===============   ===========   ==========  ===========
    unique user ID    trial #       time        trial data
    ===============   ===========   ==========  ===========

.. note::
   More information about how to record different types of data in an
   experiment can be found `here <../recording.html>`__.



``help``
~~~~~~~~

Usage::

  help
  help <command>

The ``help`` command displays a list of valid psiturk shell commands.
Entering ``help`` followed by the name of a command brings up information about
that command.



Examples:

1. List all commands:

    ::

       [psiTurk server:on mode:sdbx #HITs:0]$ help

       psiTurk command help:
       \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=
       amt_balance  debug               mode            server
       config       download_datafiles  open            setup_example  version
       db           hit                 psiturk_status  status         worker

       basic CMD command help:
       \=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=\=
       EOF             ed    help     li     py    run    shortcuts
       _load           edit  hi       list   q     save   show
       _relative_load  eof   history  load   quit  set
       cmdenvironment  exit  l        pause  r     shell

    psiTurk commands are listed first, followed by commands inherited from the
    python `cmd2` module. More information about `cmd2` commands can be found
    `here <https://cmd2.readthedocs.io/en/latest/overview/index.html>`__.

2. View the help menu for a command and its subcommands

    ::

       [psiTurk server:on mode:sdbx #HITs:0]$ help server

       Usage:
         server on
         server off
         server restart
         server log
         server help

       'server' is used with the following subcommands:
         on        Start server. Will not work if server is already running.
         off       Stop server. May take several seconds.
         restart   Run 'server off', followed by 'server on'.
         log       Open live server log in a separate window.
         help      Display this screen.

.. note::
   With commands with subcommands such as ``server``,
   you can also view the help screen by entering ``<command> help``. For
   example, ``server help`` has the same effect at ``help server``.


``hit``
~~~~~~~

The ``hit`` command is used to create, view, delete, and modify Human Intelligence
Tasks ("HITs") on Amazon Mechanical Turk.

.. contents:: Commands
    :local:

``hit create``
--------------

Usage::

  hit create [<numWorkers> <reward> <duration>]

Create a HIT with the specified number of assignments, reward amount, and
duration. Will be posted either live to AMT or to the Worker Sandbox depending
upon your current mode. ``hit create`` can also be run interactively by
entering the command without parameters.

The ``duration`` specifies how long a worker can "hold on" to your HIT
(in hours or hours.<fraction_of_hour>). This should be long enough for workers
to actually
complete your HIT, but sometimes workers will "accept" a HIT which is
worth a lot of money but come back and do the work later in the
day. You can specify a shorter duration if you want workers to
complete your HIT immediately.

Example of creating a HIT in the sandbox with three assignments that pays $2.00 and has a
1.5 hour time limit::

   [psiTurk server:on mode:sdbx #HITs:0]$ hit create 3 2.00 1.5
   *****************************
     Creating sandbox HIT
       HITid:  2XE40SPW1INMXUF9OJUNDB6BT8W2F4
       Max workers: 3
       Reward: $2.00
       Duration: 1.5 hours
       Fee: $0.60
       ________________________
       Total: $6.60
     Ad for this HIT now hosted at: https://ad.psiturk.org/view/Q3HWnfqzg3MP9VDbu3kFyn?assignmentId=debugJCI80S&hitId=debug9AWC90
   [psiTurk server:on mode:sdbx #HITs:1]$


``hit extend``
--------------

Usage::

  hit extend <HITid> [--assignments <number>] [--expiration <time>]

Extend an existing HIT by increasing the amount of time before the HIT expires
(and and is no longer available to workers) or by increasing the number of
workers who can complete the HIT.


Example adding both time and assignments to a HIT::

  psiTurk server:on mode:sdbx #HITs:1]$ hit list --active
  Stroop task
	Status: Assignable
	HITid: 2776AUC26DG6NRIGNVRFN0COYO0B4R
	max:3/pending:0/complete:0/remain:3
	Created:2014-03-07T21:36:33Z
	Expires:2014-03-08T21:36:33Z

  [psiTurk server:on mode:sdbx #HITs:1]$ hit extend 2776AUC26DG6NRIGNVRFN0COYO0B4R --assignments 10 --expiration 12
  HIT extended.
  [psiTurk server:on mode:sdbx #HITs:1]$ hit list --active
  Stroop task
	Status: Assignable
	HITid: 2776AUC26DG6NRIGNVRFN0COYO0B4R
	max:13/pending:0/complete:0/remain:13
	Created:2014-03-07T21:36:33Z
	Expires:2014-03-08T21:48:33Z

Note that both the remaining number of assignments and the expiration time of
the HIT have increased. One can also increase the number of assignments or the
expiration independently.


``hit expire``
--------------

Usage::

  hit expire (--all | <HITid> ...)

Expire one or more existing HITs, or expire all HITs using the ``--all``
flag.


Examples:

1. Expiring two HITs at once::

     [psiTurk server:on mode:sdbx #HITs:4]$ hit expire 2Y0T3HVWAVKIMG42A2S75Z9943NNFG 2RVZXR24SMEZFG314ME9X8P9CPPH0X
     expiring sandbox HIT 2Y0T3HVWAVKIMG42A2S75Z9943NNFG
     expiring sandbox HIT 2RVZXR24SMEZFG314ME9X8P9CPPH0X
     [psiTurk server:on mode:sdbx #HITs:2]$

2. Expiring all active HITs::

     [psiTurk server:on mode:sdbx #HITs:2]$ hit expire --all
     expiring sandbox HIT 2776AUC26DG6NRIGNVRFN0COYO0B4R
     expiring sandbox HIT 2VUWA6X3YOCCVET8PKOPWINIWJFPO0
     [psiTurk server:on mode:sdbx #HITs:0]$



``worker``
~~~~~~~~~~

The ``worker`` command is used to list, approve and reject, and bonus worker
assignments on Amazon mechanical Turk.

.. contents:: Commands
  :local:


``worker approve``
------------------


Usage::

   worker approve (--hit <hit_id> | <assignment_id> ...)

Approve worker assignments for one or more assignment ID's, or use the
``--hit`` flag to approve all workers for a specific HIT.


Examples:

1. Approve a single assignment::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker approve 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     approved 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7

2. Approve all assignments for a given hit::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker approve --hit 2QKHECWA6X3Y4QTYKCG5NXPTWYGMLF
     approving workers for HIT 2QKHECWA6X3Y4QTYKCG5NXPTWYGMLF
     approved 2MB011K274J7PY7FQ1ZN76UXH0ECED
     approved 2UO4ZMAZHHRR1T7J8NEVUH1KJCAKBY


``worker reject``
-----------------


Usage::

  worker reject (--hit <hit_id> | <assignment_id> ...)

Reject worker assignments for one or more assignment ID's, or use the ``--hit``
flag to reject all workers for a specific HIT.




Example rejecting a single assignment::

  [psiTurk server:on mode:sdbx #HITs:0]$ worker reject 2Y9OVR14IXKOIZQL1E3WD6X30CD98U
  rejected 2Y9OVR14IXKOIZQL1E3WD6X30CD98U


``worker unreject``
-------------------

Usage::

     worker unreject (--hit <hit_id> | <assignment_id> ...)

Unreject worker assignments for one or more assignment ID's, or use the
``--hit`` flag to unreject all workers for a specific HIT.

.. note::
   Unrejecting an assignment automatically approves that assignment.


Example of unrejecting a single assignment::

  [psiTurk server:on mode:sdbx #HITs:0]$ worker unreject 2Y9OVR14IXKOIZQL1E3WD6X30CD98U
  unrejected 2Y9OVR14IXKOIZQL1E3WD6X30CD98U


``worker bonus``
----------------

Usage::

  worker bonus  (--amount <amount> | --auto) (--hit <hit_id> | <assignment_id> ...)

Grant bonuses to workers for one or more assignment ID's, or use the ``--hit``
flag to bonus all workers for a specific HIT.

Enter the bonus ``--amount <amount>`` in an X.XX format, or use the ``--auto``
flag to bonus each worker according to the 'bonus' field of hte database
(requires a `custom bonus route <../customizing.html>`__ in the experiment's
`custom.py` file).

Upon running ``worker bonus``, you will be asked to input a reason for the
bonus. This message will be displayed to workers who receive the bonus.

.. note::
   You must approve the worker assignment *before* you grant a bonus.

.. warning::
   While it isn't possible to approve an assignment more than once, it is
   possible to grant a bonus repeatedly. When running ``worker bonus`` with the
   ``--hit`` flag, only workers who have not yet received a bonus for the
   assignment will be bonused. However, when running ``worker bonus`` on
   individual assignments the worker will be bonused regardless of whether they
   have already received one.


Examples:

1. Bonusing an individual assignment. The bonus can be granted repeatedly,
   making this risky::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --amount 2.00 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     Type the reason for the bonus. Workers will see this message: Here's a bonus!
     gave bonus of $2.00 to 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --amount 2.00 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     Type the reason for the bonus. Workers will see this message: Here's another one!
     gave bonus of $2.00 to 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7

2. Say there are approved assignments for a HIT, one already bonused, one not yet
   bonused. Bonusing by HIT prevents repeated bonuses::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --amount 2.00 --hit 2ECYT3DHJHP4RRU304P8USX9BCXU1O
     Type the reason for the bonus. Workers will see this message: you haven't been bonused yet. Here's a bonus!
     bonusing workers for HIT 2ECYT3DHJHP4RRU304P8USX9BCXU1O
     gave a bonus of $2.00 to 2MB011K274J7PY7FQ1ZN76UXH0ECED
     bonus already awarded to 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7

3. If a compute-bonus route exists in the experiment `custom.py`, we can also
   use the ``--auto`` flag to automatically give each worker the correct
   bonus::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --auto --hit 2ECYT3DHJHP4RRU304P8USX9BCXU1O
     Type the reason for the bonus. Workers will see this message: Thanks for moving science forward!
     bonusing workers for HIT 2ZQIUB2YU98JX6A4V3C0IBJ9W0HL9P
     gave a bonus of $3.00 to 27UQ45UUKQOYW1ZFLNJ8RG012VYDVP
     gave a bonus of $2.50 to 24IIHPCGJ2D2H2KFPX80MPPSKQM933

.. note::
   Unlike the commands to approve, reject, or unreject workers, the ``worker
   bonus`` command requires the psiturk shell to be launched in the same
   project as the HIT for which workers are being bonused, since the
   information about which workers have been bonused is stored in the
   experiment database.


``worker list``
----------------

Usage::

   worker list [--submitted | --approved | --rejected] [--hit <hit_id>]

List all worker assignments, or list worker assignments fitting a
given condition using the provided flags. Use the ``--hit`` flag to
list workers for a specific HIT.


Examples:

1. Listing all submitted workers::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker list --submitted
     [
         {
             "status": "Submitted",
             "assignmentId": "2VQHVI44OS2K18PW7EQSEAP5DPV5ZY",
             "workerId": "A2O6BB9HXEUXX1",
             "submit_time": "2014-03-04T16:14:32Z",
             "hitId": "2ZRNZW6HEZ6OUI7FRTZ6CGUMGIQPZ0",
             "accept_time": "2014-03-04T16:14:05Z"
         },
         {
             "status": "Submitted",
             "assignmentId": "2XB92NJKM05B2XAD1YN2JTP9TYXAFG",
             "workerId": "A2O6BB9HXEUXX1",
             "submit_time": "2014-03-03T23:35:17Z",
             "hitId": "2RWSCWY2AOO2W03X0OFGTSCMKZZ22I",
             "accept_time": "2014-03-03T23:34:19Z"
         }
     ]

2. Listing approved workers for a specific HIT::

    [psiTurk server:on mode:sdbx #HITs:0]$ worker list --approved  --hit 2ECYT3DHJHP4RRU304P8USX9BCXU1O
    listing workers for HIT 2ECYT3DHJHP4RRU304P8USX9BCXU1O
    [
        {
            "status": "Approved",
            "assignmentId": "21A8IUB2YU98ZV9C5BUL3FBJB5B8K7",
            "workerId": "A2O6BB9HXEUXX1",
            "submit_time": "2014-02-26T03:26:55Z",
            "hitId": "2ECYT3DHJHP4RRU304P8USX9BCXU1O",
            "accept_time": "2014-02-26T03:26:36Z"
        }
    ]



``psiturk_status``
------------------

Usage::

   psiturk_status

Display startup screen with message from `psiturk.org <http://psiturk.org>`__.

Example::

   [psiTurk server:off mode:sdbx #HITs:1]$ psiturk_status


   http://psiturk.org
    ______   ______     __     ______   __  __     ______     __  __
   /\  == \ /\  ___\   /\ \   /\__  _\ /\ \/\ \   /\  == \   /\ \/ /
   \ \  _-/ \ \___  \  \ \ \  \/_/\ \/ \ \ \_\ \  \ \  __<   \ \  _"-.
    \ \_\    \/\_____\  \ \_\    \ \_\  \ \_____\  \ \_\ \_\  \ \_\ \_\
     \/_/     \/_____/   \/_/     \/_/   \/_____/   \/_/ /_/   \/_/\/_/

                an open platform for science on Amazon Mechanical Turk

   --------------------------------------------------------------------
   System status:
   Hi all, You need to be running psiTurk version >= 1.0.5dev to use the
   Ad Server feature!

   Check https://github.com/NYUCCL/psiTurk or http://psiturk.org for
   latest info.
   psiTurk version 1.0.8dev
   Type "help" for more information.
   [psiTurk server:off mode:sdbx #HITs:1]$



``quit``
~~~~~~~~

Usage::

   quit

Quits the psiTurk shell. If you have a server running,
psiTurk will confirm that you want to quit before exiting, since quitting
psiTurk turns off the server.


Example of quitting psiTurk with the server running::

   [psiTurk server:on mode:sdbx #HITs:0]$ quit
   Quitting shell will shut down experiment server. Really quit? y or n: y
   Shutting down experiment server at pid 40182...
   Please wait. This could take a few seconds.
   $


``server``
~~~~~~~~~~

The ``server`` command is used with a variety of subcommands to control the
experiment server.

.. contents::
  :local:

``server on``
-------------

Start the experiment server.

Example::

   [psiTurk server:off mode:sdbx #HITs:0]$ server on
   Experiment server launching...
   Now serving on http://localhost:22362
   [psiTurk server:on mode:sdbx #HITs:0]$


``server off``
--------------

Shut down the experiment server.

Example::

   [psiTurk server:on mode:sdbx #HITs:0]$ server off
   Shutting down experiment server at pid 32911...
   Please wait. This could take a few seconds.
   [psiTurk server:off mode:sdbx #HITs:0]$


``server restart``
------------------

Runs ``server off``, followed by ``server on``.


``server log``
--------------

Opens the server log in a separate window. Uses Console.app on Max OS X and
xterm on other systems.


``status``
~~~~~~~~~~

Usage::

  status

The ``status`` command updates and displays the server status and
number of HITs available on AMT or in the worker sandbox.



.. note::
   This information is also displayed in the psiTurk shell prompt, but
   `#HITs` is not updated after every command (as every update
   requires contacting the AMT server). ``status`` provides a
   way to make sure the prompt is up-to-date.


Example of using the ``status`` command in sandbox mode::

  [psiTurk server:off mode:sdbx #HITs:1]$ status
  Server: currently offline
  AMT worker site - sandbox: 1 HITs available



``mode``
~~~~~~~~

Usage::

  mode
  mode <which>

The ``mode`` command controls the current mode of the psiTurk shell. Type
``mode live`` or ``mode sandbox`` to switch to either mode, or simply ``mode``
to switch to the opposite mode. The current mode affects almost every psiturk
shell command. For example, running ``hit create`` while in sandbox mode will
create a HIT in the sandbox, while running it in live mode will create a HIT on
the live AMT site. Similarly, commands like ``worker list all`` or ``hit list
all`` will list assignments and HITs from either the live site or the sandbox,
depending on your mode.



.. note::

   Switching the psiturk shell mode while the server is running requires the
   server to restart, since at the end of the experiment participants need to
   be correctly redirected back to either the live AMT site or the
   sandbox. Therefore, **you should not change modes while you are serving a
   live HIT to workers**.


Examples:

1. Switching mode, with and without ``<which>`` specifier::

     [psiTurk server:off mode:sdbx #HITs:0]$ mode
     Entered live mode
     [psiTurk server:off mode:live #HITs:0]$ mode sandbox
     Entered sandbox mode
     [psiTurk server:off mode:sdbx #HITs:0]$

2. Switching mode with the server running:

    ::

     [psiTurk server:on mode:sdbx #HITs:0]$ mode
     Switching modes requires the server to restart. Really switch modes? y or n: y
     Entered live mode
     Shutting down experiment server at pid 33447...
     Please wait. This could take a few seconds.
     Experiment server launching...
     Now serving on http://localhost:22362
     [psiTurk server:on mode:live #HITs:0]$

   Type ``n`` instead to abort the mode switch harmlessly.
