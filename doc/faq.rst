Frequently Asked Questions
==========================

How do I host a psiTurk experiment?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

psiTurk experiments can be hosted on almost anything that has an
internet connection and a public port, such as an office computer or
laptop. You'll need a static IP to prevent your experiment's URL from
changing. Users without one (e.g., most home users) can use a `dynamic
DNS <http://en.wikipedia.org/wiki/Dynamic_DNS>`__ service to forward a
URL to their dynamic IP. Here's a list of `free DDNS
providers <http://dnslookup.me/dynamic-dns/>`__.  You also may need
to `forward a port <http://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/>`__
from your home routers to you personal computer.


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
server processes from running.  As a result we cannot support
Windows.  Instead we support all system based on an underlying
Unix kernel which can run python.  This include Mac OS X and
Linux.


I need an experiment to do X, will psiTurk be able to do this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally any standard psychology experiment can be run using psiTurk.
This means experiments with multiple trials, trials which change
based on participant's past responses, experiments with multiple phases
or trial types, surveys, experiment recording reaction time, mouse
tracking experiments, decision making, etc...  The possibilities are actually not as much
a function of psiTurk as of the capabilities of programming an
experiment in Javascript.  Any web application or applet that runs
Javascript should play nicely with psiTurk with a little hacking.
psiTurk mostly just provides the server and data logging capabilities,
and it is up to you to define how your experiment actually looks and behaves.

There are examples in the `experiment exchange <https://psiturk.org/ee>`__
which provide a more concrete understanding of the scope of things
people have attempted with psiTurk.

One place where psiTurk currently hasn't been used is group or
multi-player experiments (although we've heard rumors of users who have
reported success with this).  In addition, we are not aware of people
using psiTurk yet for multi-day or multi-session experiments.  This is
not a technical limitation per-se but may require some hacking.  We'd
be happy if someone tried to do these types of experiments and reported
back about what we could add to the core psiTurk code to help with this.


My university will not give me a static IP address.  Can I still use psiTurk?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

psiTurk requires an generally internet-addressable computer.  Some
universities prevent this for security purposes.  There are a couple of solutions
if this situation applies to you.  First you can run psiturk via an
`ssh` session on any remote computer or server for which you can launch
server processes.  Examples would be a lab server that has a static ip
address and allows users-lavel access to particular ports.  Alternative
there are a number of (free) services which will give you a unix
command line "in the cloud" including Red Hat's `OpenShift <https://www.openshift.com/>`__.
Detailed instruction on how to do this are available `here <openshift.html>`__.


I'm trying to run psiTurk at home using a cable modem or other connection. Will it work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general this set up is definitely possible.  However, you may need to configure
the wireless router that came with your internet service to forward particular incoming
ports to your device (i.e., to you laptop instead of you phone or tablet).  There are
many excellent tutorials about this `online <http://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/>`__.


I'm having trouble with my AWS/AMT credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to use your credentials you must create a requester account
on Amazon Web Services.  This usually involves providing a credit card
number as well as a phone verification step.  Finally, some users report
having to log into `http://requester.mturk.com <http://requester.mturk.com>`__
at least once to agree to the software terms.


What do I need to know about running psiTurk on a remote server?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The psiTurk command line process and server generally works great over a `ssh` connection.
Perhaps the only thing to be aware of are that you set the `host` field
of your project's local configuration file to the ip address of the remote machine
if you want to be able to easily access it.  In addition, while the standard
`debug` command automatically launches your web-browser, you usually don't
want this behavior on the remove machine.  Instead use `debug -p` to simply
print the correct URL and copy/paste it into a browser on your local computer.


Can you program my experiment for me?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nope, sorry.  Please check the `experiment exchange <https://psiturk.org/ee>`__ for
examples you might be able to draw insight from.


I'm having Javascript errors when designing my experiment.  Can you help?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sorry, but probably not.  See the above about programming experiments.  There are many
ways of `getting help <getting_help.html>`__ with psiTurk specifically and many
excellent tutorials online for developing web applications using Javascript.


Where is the **/static/js/psiturk.js** file?  It doesn't appear in any of the experiments I have downloaded!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

psiturk.js doesn’t actually “exists” as a file in the static folder of any project.
Instead, the psiturk server/command line tool automatically generates this file.
The best way to view it is by “view source” in your browser while debugging your experiment.
While somewhat unintuitive, this ensures that changes to psiturk.js are linked
to new versions of the overall psiturk command line tool (since they are tightly
interdependent).


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
