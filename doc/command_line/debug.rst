``debug`` command
=================

Usage
-----

::

   debug [options]

``debug`` makes it possible to locally test your experiment without contacting Mechanical Turk servers. Type ``debug`` to automatically launch your experiment in a browser window. The server must be `running <server.html#server-on>`__ to debug your experiment. When debugging, the server feature that prevents participants from reloading the experiment is disabled, allowing you to make changes to the experiment on the fly and reload the debugging window to see the results.


Options
_______

::

   -p, --print-only

Use the ``-p`` flag to print a URL to use for debugging the experiment, without attempting to automatically launch a browser. This is particularly useful if your experiment server is running remotely.


Example
_______

Using the ``-p`` flag to request a debug link::

   [psiTurk server:on mode:sdbx #HITs:0]$ debug -p
   Here's your randomized debug link, feel free to request another:
   http://localhost:22362/ad?assignmentId=debugDKSAAE&hitId=debug2YW8RI&workerId=debugM1QUH4
   [psiTurk server:on mode:sdbx #HITs:0]$
