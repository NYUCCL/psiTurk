Frequently Asked Questions
==========================

Why doesn't **psiTurk** work on Windows?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Windows has very limiting security restrictions which prevent
server processes from running.  As a result we cannot support
Windows.  Instead we support all system based on an underlying
Unix kernel which can run python.  This include Mac OS X and
Linux.


I need an experiment to do X, will **psiTurk** be able to do this?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generally any standard psychology experiment can be run using **psiTurk**.
This means experiments with multiple trials, trials which change
based on participant's past responses, experiments with multiple phases
or trial types, surveys, experiment recording reaction time, mouse
tracking experiments, decision making, etc...  The possibilities are actually not as much
a function of **psiTurk** as of the capabilities of programming an
experiment in Javascript.  Any web application or applet that runs
Javascript should play nicely with **psiTurk** with a little hacking.
**psiTurk** mostly just provides the server and data logging capabilities,
and it is up to you to define how your experiment actually looks and behaves.

There are examples in the `experiment exchange <https://psiturk.org/ee>`__
which provide a more concrete understanding of the scope of things
people have attempted with **psiTurk**.

One place where **psiTurk** currently hasn't been used is group or
multi-player experiments (although we've heard rumors of users who have
reported success with this).  In addition, we are not aware of people
using **psiTurk** yet for multi-day or multi-session experiments.  This is
not a technical limitation per-se but may require some hacking.  We'd
be happy if someone tried to do these types of experiments and reported
back about what we could add to the core **psiTurk** code to help with this.

My university will not give me a static IP address.  Can I still use **psiTurk**?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**psiTurk** requires an generally internet-addressable computer.  Some
universities prevent this for security purposes.  There are a couple of solutions
if this situation applies to you.  First you can run psiturk via an
`ssh` session on any remote computer or server for which you can launch
server processes.  Examples would be a lab server that has a static ip
address and allows users-lavel access to particular ports.  Alternative
there are a number of (free) services which will give you a unix
command line "in the cloud" including Red Hat's `OpenShift <https://www.openshift.com/>`__.


I'm trying to run **psiTurk** at home using a cable modem or other connection.  Will it work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In general this set up is definitely possible.  However, you may need to configure
the wireless router that came with your internet service to forward particular incoming
ports to your device (i.e., to you laptop instead of you phone or tablet).  There are
many excellent tutorials about this `online <http://www.howtogeek.com/66214/how-to-forward-ports-on-your-router/>`__.


Can you program my experiment for me?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Nope, sorry.  Please check the `experiment exchange <https://psiturk.org/ee>`__ for 
examples you might be able to draw insight from.

I'm having Javascript error when designing my experiment.  Can you help?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sorry, but probably not.  See the above about programming experiments.  There are many 
ways of `getting help <getting_help.rst>`__ with **psiTurk** specifically and many
excellent tutorials online for developing web applications using Javascript.  A good
example is `CodeAcademy's Javascript lessons <http://www.codecademy.com/tracks/javascript>`__.