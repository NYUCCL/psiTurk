Command-line Interface
======================

The **psiTurk shell** is a simple, interactive command line interface which
allows users to communicate with Amazon Mechanical Turk, psiturk.org, and their
own experiment servers.

Starting the psiTurk shell
----------------------------

The psiTurk shell can be launched from any psiTurk project folder (i.e., any
folder with a ``config.txt`` file) by entering the command

::

  psiturk

in the terminal.

The ``psiturk`` command can also be run with several options.

Options
~~~~~~~

::

   -v, --version

Print the currently installed version of psiTurk and exit.

::
   
   -c, --cabinmode

Launch psiturk in cabin (offline) mode. This allows you to develop test
experiments locally without an internet connection. Cabin mode offers only
limited functionality, and lacks the ``amt``, ``db``, ``hit``, ``mode``, and
``worker`` commands.

::
   
   -s, --script <filename>

Run a list of commands from a text file, then exit. Each line in the file is
treated as a command.



The psiTurk shell prompt
-------------------------

The psiTurk shell prompt looks something like this::

  [psiTurk server:off mode:sdbx #HITs:0]$

and contains several pieces of usefull information. 

The ``server`` field will generally be set to ``on`` or ``off`` and denotes
whether the experiment server is running. If the ``server`` field says
``unknown``, this likely means that a a server process is running from a
previous psiTurk shell session. In this case, the process can be terminated
using the `server off <command_line/server.html#server-off>`__ command and a new server
process can then be started.

The ``mode`` field displays the current mode of the shell. In the full psiturk
shell, the mode will be either ``sdbx`` (sandbox) or ``live``. While in
cabin mode, the mode will be listed as ``cabin``. More about the psiturk shell
mode can be found `here <command_line/mode.html>`__.

The ``#HITs`` field displays the number of HITs currently active, either in the
worker sandbox when in sandbox mode or on the live AMT site when in live
mode. The ``#HITs`` field is not displayed in cabin mode.

Shell commands
---------------

.. toctree::

   command_line/hit.rst
   command_line/server.rst
   command_line/mode.rst
   command_line/worker.rst
