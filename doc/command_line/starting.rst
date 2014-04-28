Starting the psiTurk shell
===============================

Usage
------

The psiTurk shell can be launched from any psiTurk project folder (i.e., any
folder with a ``config.txt`` file) by entering the command

::

  psiturk

in the terminal.

Options
----------

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
