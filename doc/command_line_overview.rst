.. _command-line-overview:

Command-line Overview
===============================

The **psiTurk shell** is a command line interface which
allows users to communicate with their experiment server, and also
with Amazon Mechanical Turk.

The ``psiturk`` command has several invocations.

Options
~~~~~~~

``psiturk [options]``

* ``-v, --version``

  Print the currently installed version of psiTurk and exit.

* ``-s, --script <filename>``

  Run a list of commands from a text file, then exit. Each line in the file is
  treated as a command.


Command invocation
~~~~~~~~~~~~~~~~~~

``psiturk command [argument]...``

Any single shell command can be run without launching the interactive
shell, by invoking ``psiturk`` with the command as an argument. For example,
to launch the psiturk server::

  $ psiturk server on

Launch an interactive shell
~~~~~~~~~~~~~~~~~~~~~~~~~~~

``psiturk``

Alternatively, an interactive shell can be launched by running the command ``psiturk`` in any
psiturk experiment server. A ``config.txt`` file will be loaded from the directory
in which the shell is launched.

.. warning::
    The interactive shell *cannot* be launched without valid AWS credentials
    having been set! This is because the prompt is intrinsically tied to AMT --
    its prompt displays the current mturk "mode" and the "number of hits".

    However, non-AWS psiturk commands can still be run via the ``psiturk <command>``
    interface.


The psiTurk shell prompt looks something like this::

  [psiTurk server:off mode:sdbx #HITs:0]$

and contains several pieces of useful information:

* **Server field** -- will generally be set to ``on`` or ``off`` and denotes
  whether the experiment server is running. If the ``server`` field says
  ``unknown``, this likely means that a server process is running from an
  improperly closed previous psiTurk shell session. In this case, you may need to
  manually kill the processes in the terminal or restart your terminal session.
* **Mode field** -- displays the current mode of the shell. In the full psiturk
  shell, the mode will be either ``sdbx`` (sandbox) or ``live``. While in
  cabin mode, the mode will be listed as ``cabin``. More about the psiturk shell
  mode can be found `here <./mode.html>`__.
* **#HITs field** -- displays the number of HITs currently active, either in the
  worker sandbox when in sandbox mode or on the live AMT site when in live
  mode.

Create an Example Project
~~~~~~~~~~~~~~~~~~~~~~~~~

To create a sample project, run the following::

    psiturk-setup-example
