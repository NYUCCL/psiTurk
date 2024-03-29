.. _forward:

=======
Forward
=======

Read this if you want to find out more about Amazon Mechanical Turk
(AMT) and how psiTurk can help you run web-based experiments on AMT
painlessly and quickly. This section will also tell you what problems
psiTurk does and does not solve to help you gauge whether it will be
useful to you.


Understanding the psiTurk design philosophy: An analogy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Back before music was entirely digital people got their music on
cassette tapes. To play the cassette you needed a player device (e.g.,
walkman or boombox). People would trade tapes, make copies of tapes,
make mixtapes of their favorite songs. It was awesome.

psiTurk is like a player but instead of playing music, it plays
(i.e., runs) experiments. You download and install the psiTurk application
to your computer. This installs a command line tool ``psiturk`` which serves as a
multi-function "player." It can (figuratively speaking) run, pause,
eject, and configure a given experiment.

To make it useful though psiTurk needs something to play. You can download
from our :ref:`experiment-exchange` library an archive
which contains all the files specific to a given experiment. You basically
“play” the downloaded experiment using the ``psiturk`` command. You can easily
switch experiments by downloading another experiment archive and “playing” it.
Even better, you can make your own experiments by remixing others (borrowing
code from projects in the experiment exchange) or building your own from scratch.

The goal of psiturk was to build the “player” so you can spend more of
your time on the important part of your research… the experiment (i.e.,
mix tape)!

Oh, and in case you missed it, "playing" someone else's experiment
posted to the :ref:`experiment-exchange` basically
means independently replicating it!


What is Mechanical Turk?
~~~~~~~~~~~~~~~~~~~~~~~~

Amazon Mechanical Turk (AMT) is an online platform that lets you post a
wide variety of tasks to a large pool of participants. Instead of
spending weeks to run experiments in the lab, it lets you collect data
of a large number of people within a couple of hours.

Some key terminology for understanding the AMT model:

-  **HIT (Human Intelligence Task)** - A unit of work (e.g. a psychology experiment)
-  **Requester** - The person or entity that posts HITs (e.g. a researcher or lab)
-  **Worker** - The person that completes HITs (i.e. a participant in your study)

Workers get paid a fixed amount for each HIT which is determined by the
requester. Requesters can also make bonus payments to specific workers.
Amazon collects a 10% fee for each payment.


Why psiTurk?
~~~~~~~~~~~~

AMT provides some very basic templates that you can use to design HITs
(particularly questionnaires), but these will most likely not serve your
purposes as an experimenter. The psiTurk toolbox is designed to help
you run fully-customized and dynamic web-experiments on AMT.
Specifically, it allows you to:

1. Run a web server for your experiment
2. Test your experiment
3. Interact with AMT to recruit, post HITs, filter, and pay participants
   (AMT workers)
4. Manage databases and export data

psiTurk also includes a powerful interactive command interface that
lets you manage most of your AMT activity.


Basic Requirement: A publicly-accessible server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Be aware that you will need to host your experiment on a server to which
your participants have access.  Currently the easiest way to do this is through the
free-tier on Heroku.  See the main docs for more information about this.


Do I have to learn how to code?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes. psiTurk experiments are run in web browsers. To develop a web browser
experiment, you need to have basic web programming skills with HTML, CSS, and
JavaScript.

To get you started, psiTurk provides a fully functioning example
experiment in the :ref:`example-project-stroop` section that
you can use as a template for your own study. psiTurk also includes
a library of basic Javascript functions (see :ref:`api-overview`) that you can
insert into your code to handle page transitions, load images, and
record data.

However, for actually programming the interface of your task people often use other 
javascript tools like the outstanding [jsPsych](https://www.jspsych.org).
