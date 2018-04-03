The psiTurk shell prompt
==========================

The psiTurk shell prompt looks something like this::

  [psiTurk server:off mode:sdbx #HITs:0]$

and contains several pieces of useful information.


Server field
------------

The ``server`` field will generally be set to ``on`` or ``off`` and denotes
whether the experiment server is running. If the ``server`` field says
``unknown``, this likely means that a server process is running from an
improperly closed previous psiTurk shell session. In this case, you may need to
manually kill the processes in the terminal or restart your terminal session.


Mode field
----------

The ``mode`` field displays the current mode of the shell. In the full psiturk
shell, the mode will be either ``sdbx`` (sandbox) or ``live``. While in
cabin mode, the mode will be listed as ``cabin``. More about the psiturk shell
mode can be found `here <./mode.html>`__.


#HITs field
-----------

The ``#HITs`` field displays the number of HITs currently active, either in the
worker sandbox when in sandbox mode or on the live AMT site when in live
mode. The ``#HITs`` field is not displayed in cabin mode.
