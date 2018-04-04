``quit`` command
=================


Usage
-----

::

   quit

The ``quit`` command quits the psiTurk shell. If you have a server running,
psiTurk will confirm that you want to quit before exiting, since quitting
psiTurk turns off the server.


Example
-------

Quitting psiTurk with the server running::

   [psiTurk server:on mode:sdbx #HITs:0]$ quit
   Quitting shell will shut down experiment server. Really quit? y or n: y
   Shutting down experiment server at pid 40182...
   Please wait. This could take a few seconds.
   $
