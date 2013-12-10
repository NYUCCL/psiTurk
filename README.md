What is this?
============

**psiTurk** is an open platform for science on Amazon's Mechanical Turk. 

It is intended to provide most of the backend machinery necessary to run dynamic
and interactive behavioral experiments on Amazon Mechanical Turk (AMT). As long 
as you can turn your experiment into a dynamic webpage, you can run it with 
**psiTurk**!

*Features*

1. Provide access to your experiments online directly from your desktop computer
  - No need to install complex webserver software (e.g., Apache, MySQL)
  - Minimizes security issues since server only runs while you want to collect data
  - Secure Ad server ensures your HITs are visible to all AMT workers
  - Ensures that conditions of your experiment fill in randomly but evenly
  - Prevent the same workers from completing your expermient more than once
  - Highly customizable for wide variety of experiment designs
  - Backup and store data seamlessly in the cloud (using Amazon Web Services)
1. Javacript API helps you get going with experiment programming faster
  - Record if participants switch between windows during task, etc...
  - Save data incrementally to minimize data loss
  - Prevent users from quiting then restarting experiment
1. Powerful command line interface
  - Simplifies paying participants quickly
  - Assign bonuses with ease
  - Debug and test your experiment
  - Create and manage robust cloud-based databases for your data

Please visit [psiturk.org](https://psiturk.org) for more information.

Install
=======

The easiest way to install **psiTurk** is via `pip`.
Simply type into a terminal:

    pip install psiturk 

If this doesn't work, you might try `sudo pip install psiturk`.  Directions
on how to install `pip` if you don't have it on your system are available in 
our [documentation](https://github.com/NYUCCL/psiTurk/wiki/Getting-psiTurk-installed-on-your-computer#installation-steps).


Quick Start
===========

After installing, explore **psiTurk** with seven easy steps:

  1. Sign up with Amazon [here](http://aws.amazon.com/).
  2. Sign up for a Mechanical Turk requester account, available [here](https://requester.mturk.com/).
  3. To use our demo, create a directory, open it e.g., `mkdir psiTurkDemo; cd psiTurkDemo`, and then issue the command `psiturk-setup-example`.
  4. Edit the config.txt file in this directory to include you Amazon credentials and change the `server` option to the ip/hostname of your local computer (more info [here](https://github.com/NYUCCL/psiTurk/wiki/Config.txt)).
  5. Start `psiturk` to launch the interactive command shell (full list of command savailable by typing `help` at the interactive prompt).
  6. Type `start_server` at the prompt to start the webserver.
  7. Type `debug` at the prompt to launch the **psiTurk** demo experiment in a new browser window.


Getting Help
============

Extensive documentation is made available on the [wiki](https://github.com/NYUCCL/psiTurk/wiki/).

You can also direct questions to our [Q&A Google group](https://groups.google.com/d/forum/psiturk).
Slides from our CogSci2013 workshop in Berlin are posted [here](http://gureckislab.org/cogsci_workshop/)
(use arrow keys to navigate).  


Example experiment
=================

**psiTurk** ships with an example "Stroop" which could form the basis of your
own experiment. The task logic is programmed in Javascript, which will run in
your participant's browser. To take a look at the example, type 
`psiturk-setup-example` in an empty directory.  Detailed instructions
stepping you through the examples are provided [here](https://github.com/NYUCCL/psiTurk/wiki/Getting-up-and-running-with-the-basic-Stroop-task)
.


FAQ
===

 * **I can't seem to get pip working**.  If you are having trouble setting up
   Python, we suggest installing the [Enthought Python
   Distribution](https://www.enthought.com/products/epd/), which is licensed
   for free to academics [at this
   link](https://www.enthought.com/products/canopy/academic/). It provides a
   kitchen-sink-included version of Python which includes `pip`.

Copyright
=========
You are welcome to use this code for personal or academic uses. If you fork,
or use this in an academic paper please cite as follows:

McDonnell, J.V., Martin, J.B., Markant, D.B., Coenen, A., Rich, A.S., and Gureckis, T.M. 
(2012). psiTurk (Version 1.02) [Software]. New York, NY: New York University. 
Available from https://github.com/NYUCCL/psiTurk



