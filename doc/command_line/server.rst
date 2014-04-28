``server`` command + subcommands
==================================

.. contents::

Description
-----------

The ``server`` command is used with a variety of subcommands to control the
experiment server.

``server on``
-------------

Start the experiment server.

Example
~~~~~~~

::

   [psiTurk server:off mode:sdbx #HITs:0]$ server on
   Experiment server launching...
   Now serving on http://localhost:22362
   [psiTurk server:on mode:sdbx #HITs:0]$

``server off``
--------------
Shut down the experiment server.

Example
~~~~~~~

::

   [psiTurk server:on mode:sdbx #HITs:0]$ server off
   Shutting down experiment server at pid 32911...
   Please wait. This could take a few seconds.
   [psiTurk server:off mode:sdbx #HITs:0]$

``server restart``
------------------

Runs ``server off``, followed by ``server on``.

``server log``
------------------

Opens the server log in a separate window. Uses Console.app on Max OS X and
xterm on other systems.

