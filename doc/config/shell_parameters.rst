Shell Parameters
================

The Shell Parameters section contains details about
the psiturk shell.

::

	[Shell Parameters]
	always_launch_in_sandbox = true

`always_launch_in_sandbox` [ true | false]
-----------------------------------------

If set to `true` this option will cause the psiturk shell
to always launch in sandbox mode, automatically changing the `using_sandbox <hit_configuration.html#using-sandbox-true-false>`__  option to true. 
This is to avoid errors where the user "forgets" that they are "live".
This means to interact with the live AMT site you
must manually switch the mode after launching the shell.
If set to `false`, the shell will launch in whatever mode
was last set.


.. seealso::

   `Overview of the command-line interface <../command_line_overview.html>`__
   	  The basic features of the **psiTurk** command line.
