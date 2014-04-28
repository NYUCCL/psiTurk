``mode`` command
=============

Usage
-----

::

   mode
   mode <which>

The ``mode`` command controls the current mode of the psiTurk shell. Type
``mode live`` or ``mode sandbox`` to switch to either mode, or simply ``mode``
to switch to the opposite mode. The current mode affects almost every psiturk
shell command. For example, running ``hit create`` while in sandbox mode will
create a HIT in the sandbox, while running it in live mode will create a HIT on
the live AMT site. Similarly, commands like ``worker list all`` or ``hit list
all`` will list assignments and HITs from either the live site or the sandbox,
depending on your mode.

.. note::

   Switching the psiturk shell mode while the server is running requires the
   server to restart, since at the end of the experiment participants need to
   be correctly redirected back to either the live AMT site or the
   sandbox. Therefore, **you should not change modes while you are serving a
   live HIT to workers**.

Examples
--------

1. Switching mode, with and without ``<which>`` specifier::

     [psiTurk server:off mode:sdbx #HITs:0]$ mode
     Entered live mode
     [psiTurk server:off mode:live #HITs:0]$ mode sandbox
     Entered sandbox mode
     [psiTurk server:off mode:sdbx #HITs:0]$

2. Switching mode with the server running::

     [psiTurk server:on mode:sdbx #HITs:0]$ mode
     Switching modes requires the server to restart. Really switch modes? y or n: y
     Entered live mode
     Shutting down experiment server at pid 33447...
     Please wait. This could take a few seconds.
     Experiment server launching...
     Now serving on http://localhost:22362
     [psiTurk server:on mode:live #HITs:0]$

   Type ``n`` instead to abort the mode switch harmlessly.
