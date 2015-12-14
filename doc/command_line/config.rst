``config`` command + subcommands
==================================

.. contents::

Description
-----------

The ``config`` command is used with a variety of subcommands to control the
current configuration context

``config print``
-------------

Prints the current configuration context (both local and global config options).

.. seealso::

   `Configuration files <configuration.html>`__
   	  More info about the global and local configuration files.


Example
~~~~~~~

::

   [psiTurk server:off mode:sdbx #HITs:0]$ config print
	[AWS Access]
	aws_region=us-east-1
	aws_access_key_id=XXXXXX
	aws_secret_access_key=XXXX
	...
	[Shell Parameters]
	launch_in_sandbox_mode=true
   [psiTurk server:on mode:sdbx #HITs:0]$

``config reload``
--------------
Reloads the current config context (both local and global files).  This will
cause the server to restart.

Example
~~~~~~~

::

   [psiTurk server:on mode:sdbx #HITs:0]$ config reload
	Reloading configuration requires the server to restart. Really reload? y or n: y
	Shutting down experiment server at pid 82701...
	Please wait. This could take a few seconds.
	Experiment server launching...
	Now serving on http://localhost:22362
   [psiTurk server:off mode:sdbx #HITs:0]$


``config help``
------------------

Display a help message concerning the config subcommand.

