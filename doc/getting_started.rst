.. _quickstart:

Getting started developing
==========

Generally there is a distinction between using `psiturk` locally to help 
you **develop** your experiment code versus **deploying** it in a way that 
enables data collection.  This guide shows how easy it is to get up and running the
developing your experiment code using `psiturk`.

Generally one develops an experiment entirely on a local personal computer. 
`psiturk` creates a local copy of the web environment that will later run 
on the cloud when deployed. 

For this reason, this section of the guide steps you through the process of
installing psiturk on your personal machine and stepping through common 
debugging steps.


.. contents:: Overview
  :local:


Step 1: Install psiturk
-----------------------

psiturk can be installed easily on any system that has a Python (>=3.6) installation 
and has the python package manager ``pip``.  At the terminal (➜):

::

  ➜ pip install psiturk

.. seealso:: :ref:`install`

After you install it can be helpful to double check that you have the correct version installed:

::

  ➜ psiturk version
  psiTurk version 3.0.6

If you are following this guide you want this to be version 3.0.6 or higher.

Step 2: Create a default project structure
------------------------------------------

psiturk includes a simple example project which you can use to get started.

::

  ➜ psiturk-setup-example

  Creating new folder `psiturk-example` in the current working directory
  ...
  Creating default configuration file (config.txt)

psiturk should be locally run in the top level folder of your project.  
Enter this shell command to enter the newly created folder:

::

  ➜ cd psiturk-example

The default project include several default files you will later modify.  To list them:

::

  ➜ ls -la
  ➜ ls -la
  total 40
  ➜ ls -la
  total 47
  drwxr-xr-x    7 user  staff   224 Mar 29 21:40 .
  drwx------@ 147 user  staff  4704 Mar 29 12:53 ..
  -rw-r--r--    1 user  staff  8649 Mar 29 21:40 config.txt
  -rw-r--r--    1 user  staff  3461 Mar 29 21:40 custom.py
  drwxr-xr-x    8 user  staff   256 Mar 29 21:40 static
  drwxr-xr-x   18 user  staff   576 Mar 29 21:40 templates

.. seealso:: :ref:`anatomy-of-project`


Step 3: Launch psiturk in the new project directory
---------------------------------------------------

psiturk should be run in the top level folder of your project. You should be
greeted with a welcome screen and command prompt.

There is also an extensive help system in the command line. Type ``help`` to see a
list of available commands. Type ``help <cmd>`` to get more information about a
particular command (e.g., ``help server``).

::

  ➜ cd psiturk-example
  ➜ psiturk

  welcome...
  psiTurk version 2.1.1
  Type "help" for more information.
  [psiTurk server:off mode:sdbx #HITs:0]$

.. seealso:: :ref:`command-line-overview`


Step 4: Start the server
------------------------

The psiturk server is the web server which responds to external requests. To
start or stop the server type ``server on``, ``server off``, or ``server restart``.

::

  ➜ [psiTurk server:off mode:sdbx #HITs:0]$ server on

  Experiment server launching...
  Now serving on http://localhost:22362
  [psiTurk server:on mode:sdbx #HITs:0]$


Step 5: Debug/view your experiment
----------------------------------

To debug or test the experiment, simply type debug. This will launch the default
web browser on your system and point it at your experiment in a method which is
helpful for testing.

Hint: If you are running on a remote server and want to disable launching the
browser type ``debug -p`` (print only) which will print the debugging URL but
not launch the browser.

Altering the experiment code is beyond the scope of the quick start, but see
:ref:`this guide <example-project-stroop>` for details on how to modify and extend the stroop example.

A short summary is that you make changes to the files in the `static/` and `templates/`
folder to reflect your experiment design.  You do not need to restart the server as you
change these files locally.  The changes will be reflected the next time you load the
experiment url.

::

  ➜ [psiTurk server:on mode:sdbx #HITs:0]$ debug

  Launching browser pointed at your randomized debug link, feel free to request another.
    http://localhost:22362/ad?assignmentId=debugX12JJ8&hitId=debugA7NP2T&workerId=debugS9K039
  [psiTurk server:on mode:sdbx #HITs:0]$


Notice that the debug link assigns random values to the `assignmentId`, `hitId`, and `workerId`.  
These are values typically provided by the Mechanical Turk system but which are set randomly during
debugging so you can isolate this data in your analysis later.

Step 6: Check your data
-----------------------

By default psiTurk saves your data to a SQLite database participants.db in your
base project folder. You can check that everything is being recorded properly by
opening that file in a SQLite tool like Base.

.. seealso:: :ref:`databases-overview`


At this point you develop your experiment until you are confident it is ready to run.  Then you
move on to our guide to :ref:`collecting-data`.