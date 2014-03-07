Starting the **psiTurk** shell
===============================

.. contents::

Usage
******

::
   psiturk [options]

Description
***********

Launch the psiTurk interactive shell. The shell can be launched from any
psiTurk project folder (i.e., any folder with a `config.txt` file).

options
*******

::
   -v, --version

Print the currently installed version of psiTurk and exit.

::
   -c, --cabinmode

Launch psiturk in cabin (offline) mode. This allows you to develop test
experiments locally without an internet connection.

::
   -s, --script <filename>

Run a list of commands from a text file, then exit. Each line in the file is
treated as a command.
