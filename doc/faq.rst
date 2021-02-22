.. _faq:

Frequently Asked Questions
==========================

.. contents::
   :local:
   :depth: 1


.. _how-host-mturk-experiment:

How do I host a psiTurk experiment for MTurkers?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need to host your server on any computer that is reachable from the public
internet. Consider hosting your server on a cloud provider such as Heroku,
AWS, DigitalOcean, etc.

.. seealso:: :ref:`heroku-guide`


I'm trying to run psiTurk at home using a cable modem or other connection. Will it work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general this set up is possible via port fowarding, if you have access to
and are comfortable configuring your home's router. However, it is not recommended.
Consider instead :ref:`deploying your psiturk study on Heroku <deploy-on-heroku>` or another
cloud provider.


My university will not give me a static IP address. Can I still use psiTurk?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can still use psiTurk if you have access to a computer with a public IP address,
or that can receive public traffic. See :ref:`how-host-mturk-experiment`.


I insist on running my experiment from my home, despite the insanity of doing the same.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

psiTurk experiments can be hosted on almost anything that has an
internet connection and a public port, such as an office computer or
laptop. You'll need a static IP to prevent your experiment's URL from
changing. Users without one (e.g., most home users) can use a `dynamic
DNS <http://en.wikipedia.org/wiki/Dynamic_DNS>`__ service to forward a
URL to their dynamic IP. Here's a list of `free DDNS
providers <http://dnslookup.me/dynamic-dns/>`__. You also may need
to `forward a port <http://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/>`__
from your home routers to you personal computer.

Can I use psiTurk for non-MTurk studies?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes! psiTurk launches a server that MTurk merely points to. For each accepted HIT,
MTurk appends information about the ``workerId``, ``assignmentId``, and ``hitId``
that psiTurk uses to create a record for the participant in the psiturk database.
psiTurk also reads a ``mode`` parameter from the url, which, for AMT studies, is
either ``sandbox`` or ``live``.

If you want to recruit participants via not-AMT, then you only must somehow
generate URLs for your participants including the above keys.

.. todo::

    * also describe changing the ``complete.html`` template
    * point to a google-group discussion of someone doing the above


There was an error in my experiment and I need to pay participants, but I can't because they weren't able to complete my HIT. How can I pay them?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You need *Whoops y'all*.

Whoops y'all is a psiTurk compatible experiment for paying people when an
experiment goes badly for some reason. You enter the worker IDs of people who
you owe money to and can reject all others. Payment is handled quickly and
easily via psiTurk's command line features. When you make a whoops, use
"whoops y'all"!

See `Whoops y'all <https://github.com/NYUCCL/whoops_yall>`__ on GitHub.


Why doesn't psiTurk work on Windows?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Windows has very limiting security restrictions which prevent
server processes from running. As a result we cannot support
Windows. Instead we support all system based on an underlying
Unix kernel which can run python. This include Mac OS X and
Linux.


I need an experiment to do X, will psiTurk be able to do this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally, any standard psychology experiment can be run using psiTurk.
This means experiments with multiple trials, trials which change
based on participant's past responses, experiments with multiple phases
or trial types, surveys, experiment recording reaction time, mouse
tracking experiments, decision making, etc. The possibilities are actually not as much
a function of psiTurk as of the capabilities of programming an
experiment in Javascript. Any web application or applet that runs
Javascript should play nicely with psiTurk with a little hacking.
psiTurk mostly just provides the server and data logging capabilities,
and it is up to you to define how your experiment actually looks and behaves.

There are examples in the :ref:`experiment exchange <experiment-exchange>`
which provide a more concrete understanding of the scope of things
people have attempted with psiTurk.

One place where psiTurk currently hasn't been used is group or
multi-player experiments (although we've heard rumors of users who have
reported success with this). In addition, we are not aware of people
using psiTurk yet for multi-day or multi-session experiments. This is
not a technical limitation per-se but may require some hacking. We'd
be happy if someone tried to do these types of experiments and reported
back about what we could add to the core psiTurk code to help with this.


I'm having trouble with my AWS/AMT credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to use your credentials you must create a requester account
on Amazon Web Services. This usually involves providing a credit card
number as well as a phone verification step. Finally, some users report
having to log into `http://requester.mturk.com <http://requester.mturk.com>`__
at least once to agree to the software terms. Read the :ref:`amt-setup` guide
carefully.


Can you program my experiment for me?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nope, sorry. Please check the :ref:`experiment-exchange` for
examples you might be able to draw insight from.


I'm having Javascript errors when designing my experiment. Can you help?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sorry, but probably not. See the above about programming experiments. There are many
ways of `getting help <getting_help.html>`__ with psiTurk specifically and many
excellent tutorials online for developing web applications using Javascript.


Where is the **/static/js/psiturk.js** file? It doesn't appear in any of the experiments I have downloaded!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*psiturk.js* doesn’t actually “exists” as a file in the static folder of any project.
Instead, the psiturk server/command line tool automatically generates this file.
The best way to view it is by “view source” in your browser while debugging your experiment.
While somewhat unintuitive, this ensures that changes to psiturk.js are linked
to new versions of the overall psiturk command line tool (since they are tightly
interdependent). Alternatively,
`view the source of the file on GitHub <https://github.com/NYUCCL/psiTurk/blob/master/psiturk/psiturk_js/psiturk.js>`__.


.. _interpret-hit-status:

How do I interpret the ``hit list`` counts of "Pending," "Complete," and "Remain"?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* MTurk defines "Completed" as submissions that you have either Approved or Rejected.

* MTurk defines "Pending" as submissions that have been "accepted" by a worker
  or that are being "viewed" by a worker. A worker has the "hit duration" to
  complete the hit. Many users use tools that automatically accept HITs for them
  and put them in a queue. Workers may not begin working on your hit until it is
  close to the duration expiry.

* Outstanding submissions that need to be either approved or rejected before the hit can be deleted.


.. _why-no-hits-available:

Immediately after I post my HIT on the "live" mode of AMT, I cannot find it via an mturk dashboard search?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many MTurkers use tools that automatically accept HITs for them
and put them in a queue. If all of your HITs get gobbled up before the MTurk GUI
refreshes, then your HIT will *never* appear via a search on the MTurk GUI.

.. _why-crashing:

Why does my server keep crashing when I try to start it via `psiturk server on`?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check your :ref:`settings-logfile` -- it should have the python error that caused the crash.
