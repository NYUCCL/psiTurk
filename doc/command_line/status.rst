``status`` command
==================

Usage
-----

::

   status

The ``status`` command updates and displays the server status and
number of HITs available on AMT or in the worker sandbox.

.. note::
   This information is also displayed in the psiTurk shell prompt, but
   `#HITs` is not updated after every command (as every update
   requires contacting the AMT server). ``status`` provides a
   way to make sure the prompt is up-to-date.


Example
-------

Using the ``status`` command in sandbox mode::

  [psiTurk server:off mode:sdbx #HITs:1]$ status
  Server: currently offline
  AMT worker site - sandbox: 1 HITs available
