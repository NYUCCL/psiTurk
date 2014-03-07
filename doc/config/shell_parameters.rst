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
to always launch in sandbox mode.  This is to avoid
errors where the user "forgets" that they are "live".
This means you interact with the live AMT site you
must manually switch the mode each time.  Otherwise
psiturk will use the setting of the `using_sandbox`
described `here <hit_configuration.html#using-sandbox-true-false>`__.