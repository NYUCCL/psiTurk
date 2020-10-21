.. _quickstart:

Quickstart
==========

Interested in psiTurk? Try out this quick start guide to running a simple
experiment online! It steps you from installing to paying participants and
should work for most people using updated versions of Linux or Mac OS X.

This guide uses a simple example experiment provided in the defaul psiTurk
installation, but can be used to run any psiTurk experiment.

.. contents:: Contents
  :local:


Step 1: Install psiTurk
-----------------------

psiTurk can be installed easily on any system that has the python package
manager ``pip``.

::

  $ pip install psiturk

.. seealso:: :ref:`install`


Step 2: Create a default project structure
------------------------------------------

psiTurk includes a simple example project which you can use to get started.

::

  $ psiturk-setup-example

  Creating new folder `psiturk-example` in the current working directory
  ...
  Creating default configuration file (config.txt)


Step 3: Enter credentials
-------------------------

In order to get access to the Amazon Mechanical Turk features of psiTurk, you
need obtain and enter credentials for accessing Amazon Web Services. Both of
these can be added to ``~/.psiturkconfig``. You can leave the ``aws_region`` at
the default value.


::

  $ cat ~/.psiturkconfig

  [AWS Access]
  AWS_ACCESS_KEY_ID = YourAccessKeyId
  AWS_SECRET_ACCESS_KEY = YourSecretAccessKey
  aws_region = us-east-1

.. seealso:: :ref:`amt-setup`

Step 4: Launch psiTurk in the new project directory
---------------------------------------------------

psiTurk should be run in the top level folder of your project. You should be
greeted with a welcome screen and command prompt.

There is also an extensive help system in the command line. Type ``help`` to see a
list of available commands. Type ``help <cmd>`` to get more information about a
particular command (e.g., ``help server``).

::

  $ cd psiturk-example
  $ psiturk

  welcome...
  psiTurk version 2.1.1
  Type "help" for more information.
  [psiTurk server:off mode:sdbx #HITs:0]$

.. seealso:: :ref:`command-line-overview`


Step 5: Start the server
------------------------

The psiTurk server is the web server which responds to external requests. To
start or stop the server type ``server on``, ``server off``, or ``server restart``.

::

  $ [psiTurk server:off mode:sdbx #HITs:0]$ server on

  Experiment server launching...
  Now serving on http://localhost:22362
  [psiTurk server:on mode:sdbx #HITs:0]$


Step 6: Debug/view your experiment
----------------------------------

To debug or test the experiment, simply type debug. This will launch the default
web browser on your system and point it at your experiment in a method which is
helpful for testing.

Hint: If you are running on a remote server and want to disable launching the
browser type ``debug -p`` (print only) which will print the debugging URL but
not launch the browser.

Altering the experiment code is beyond the scope of the quick start, but see
:ref:`this guide <example-project-stroop>` for details on how to modify and extend the stroop example.

::

  $ [psiTurk server:on mode:sdbx #HITs:0]$ debug

  Launching browser pointed at your randomized debug link, feel free to request another.
    http://localhost:22362/ad?assignmentId=debugX12JJ8&hitId=debugA7NP2T&workerId=debugS9K039
  [psiTurk server:on mode:sdbx #HITs:0]$


Step 7: Create a sandboxed HIT/Ad
---------------------------------

In order to make the experiment available to workers on Amazon Mechanical Turk you need to:

1. Run your psiturk server on a machine that is publicly-accessible.
2. Post a HIT on AMT, which will point MTurkers to your psiturk server address.

The example below uses the Amazon Mechanical Turk "sandbox," which is a place
for testing your task without actually offering it live to real paid workers.

Your HIT should be visible on http://workersandbox.mturk.com if you search for
your requester account name or the HIT title word "Stroop" (set in config.txt).

.. warning::

    **Important!** Test to make sure that your Ad URL can be accessed from a
    place external to the network from which you created the HIT. If it cannot
    be accessed, then MTurkers won't be able to access your HIT!


Step 8: Check your data
-----------------------

By default psiTurk saves your data to a SQLite database participants.db in your
base project folder. You can check that everything is being recorded properly by
opening that file in a SQLite tool like Base.

.. seealso:: :ref:`databases-overview`


Step 9: Monitor progress
------------------------

One simple way to monitor how many people have actually accepted your HIT is with
the ``hit list --active`` or ``hit list --reviewable`` commands.

This shows the HITid for each task, how many have completed, and how many are pending.

.. seealso::
  See these FAQs:

  * :ref:`interpret-hit-status`
  * :ref:`why-no-hits-available`


Step 10: Approve workers
------------------------
psiTurk provides many tools for approving workers, assigning bonuses, etc.
Try ``help hit`` and ``help worker``.

One simple approach is to approve all the workers associated with a particular
HIT (once all the assignments are complete). To do this, use the
``worker approve --hit <HITID>`` command.

::

  $ [psiTurk server:on mode:sdbx #HITs:0]$ worker approve --hit 28K4SME3ZZ2MZI004SETTTXTTAG44LT

  Approving....

Step 11: Switch to "live" mode
------------------------------

In order to create public hits on the "live" AMT site, you need to switch modes
in the command shell using the mode command. To get back to the sandbox, just
type mode again.

To avoid mistakes, psiTurk defaults to sandbox mode (this behavior can be
changed in config.txt)

From here, everything is exactly the same as described for sandbox hits above.

::

  $ [psiTurk server:on mode:sdbx #HITs:1]$ mode

  Entered live mode
  [psiTurk server:on mode:live #HITs:0]$
