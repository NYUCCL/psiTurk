``help`` command
=================

Usage
-----

::

   help
   help <command>

The ``help`` command displays a list of valid psiturk shell commands. Entering ``help`` followed by the name of a command brings up information about that command.

Examples
---------

1. List all commands::

   [psiTurk server:on mode:sdbx #HITs:0]$ help

   psiTurk command help:
   =====================
   amt_balance  debug               mode            server         tunnel 
   config       download_datafiles  open            setup_example  version
   db           hit                 psiturk_status  status         worker 

   basic CMD command help:
   =======================
   EOF             ed    help     li     py    run    shortcuts
   _load           edit  hi       list   q     save   show
   _relative_load  eof   history  load   quit  set
   cmdenvironment  exit  l        pause  r     shell

psiTurk commands are listed first, followed by commands inherited from the
python `cmd2` module. More information about `cmd2` commands can be found
`here <http://pythonhosted.org/cmd2/index.html>`__.

2. View the help menu for a command and its subcommands::

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
