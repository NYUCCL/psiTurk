What is this?
============

**psiTurk** is an open platform for conducting custom behavioral experiments on
Amazon's Mechanical Turk. 

It is intended to provide most of the backend machinery necessary to run your
experiment. It uses AMT's _External Question_ HIT type, meaning that you can
collect data using any website. As long as you can turn your experiment into a
website, you can run it with **psiTurk**!

Install
=======

The easiest way to install **psiTurk** is via `pip`.
Simply type into a terminal:

    pip install psiturk 

If this doesn't work, you might try `sudo pip install psiturk`.  Directions
on how to install `pip` if you don't have it on your system are available in 
our [documentation](https://github.com/NYUCCL/psiTurk/wiki/Getting-psiTurk-installed-on-your-computer#installation-steps).

Mac users will need to install a C compiler via XCode first (available from the Mac App Store).
Once it is installed, the command line compiler tools are made available from the preferences 
menu as described [here](http://stackoverflow.com/a/9353468/62179).  On OS X Mavericks the
command line tools are installed in a [new way](http://stackoverflow.com/questions/18216865/how-to-install-command-line-tools-on-osx-mavericks).



Quick Start
===========

Explore **psiTurk** with eight easy steps:

  1. Sign up for an AWS account, available [here](http://aws.amazon.com/).
  2. Sign up for a Mechanical Turk requester account, available [here](https://requester.mturk.com/).
  3. In a terminal, install **psiTurk** by typing `sudo pip install psiturk` (see [installation instructions](https://github.com/NYUCCL/psiTurk/wiki/Getting-psiTurk-installed-on-your-computer) for details).
  4. To use our demo, create a directory, open it e.g., `mkdir psiTurkDemo; cd psiTurkDemo`, and then issue the command `psiturk-setup-example`.
  5. Start the dashboard by typing `psiturk` on the commandline. The **psiTurk** dashboard will pop up in a new browser window. 
  6. Provide the dashboard with your AWS credentials. Skip this step if you just want to test an experiment locally by pressing "proceed without login". 
  7. To launch the experiment server, click the "turn on?" button in the upper right-hand corner. Once the experiment server is running, a green light will appear. 
  8. Click the "test" button to launch the **psiTurk** demo experiment in a new browser window.  


Getting Help
============

Extensive documentation is made available on the [wiki](https://github.com/NYUCCL/psiTurk/wiki/).

You can also direct questions to our [Q&A Google group](https://groups.google.com/d/forum/psiturk).
Slides from our CogSci2013 workshop in Berlin are posted [here](http://gureckislab.org/cogsci_workshop/)
(use arrow keys to navigate).  


Experiment design
=================

We have provided an example stroop experiment that could form the basis of your
own experiment. The task logic is programmed in Javascript, which will run in
your participant's browser. Most of the code can be found in
`static/js/task.js`.  It works by dynamically changing the html document served
to participants in `templates/exp.html` and communicating with the server code
which can be found in `psiturk/psiturk.py`. **psiTurk** assigns a condition and
counterbalance to each participant. PsiTurk actively manages the condition and
counterbalance subjects are assigned to, helping you fill them in evenly. These
are fed into Javascript via code in `static/js/psiturk.js`. You can tell
**psiTurk** how many conditions and counterbalance identities there are in the
dashboard's "Expt Info" tab.

Deployment
==========

Configuration
------------
To make your experiment available on the internet, make the following changes:

 - Under the `Server` tab change `Host` to `0.0.0.0`. 
 - Under the `HIT Config` tab change `Ad URL` to
   `http://yoururl:yourport/mturk`, replacing `yoururl` with the url to your
   server, and `yourport` with the port you have configured in `config.txt` (by
   default, 22362).

Database
--------

We recommend using a deployment-robust database solution such as
[MySQL](http://www.mysql.org) or [PostgreSQL](http://www.postgresql.org).
SQLite does not allow concurrent access to the database, so if the locks work
properly, simultaneous access (say, from multiple users submitting their data
at the same time) could destabilize your database. In the worst (unlikely)
scenario, the database could become corrupted, resulting in data loss.

Instructions for setting up a MySQL server on a Mac can be found 
[in the wiki](https://github.com/NYUCCL/psiTurk/wiki/Macintosh-Configuration).
Other platforms, check out instructions at
[mysql.org](http://dev.mysql.com/doc/refman/5.5/en//installing.html).

FAQ
---

 * **I can't seem to get pip working**.  If you are having trouble setting up
   Python, we suggest installing the [Enthought Python
   Distribution](https://www.enthought.com/products/epd/), which is licensed
   for free to academics [at this
   link](https://www.enthought.com/products/canopy/academic/). It provides a
   kitchen-sink-included version of Python which includes `pip`.

Copyright
=========
You are welcome to use this code for personal or academic uses. If you fork,
please cite us.

If you use this in an academic paper please cite as follows:

McDonnell, J.V., Martin, J.B., Markant, D.B., Coenen, A., Rich, A.S., and Gureckis, T.M. 
(2012). psiTurk (Version 1.02) [Software]. New York, NY: New York University. 
Available from https://github.com/NYUCCL/psiTurk

Import into BibTeX:

```latex
@manual{Mcdonnell12,
	Address = {New York, NY},
	Author = {McDonnell, J.V. AND Martin, J.B. AND Markant, D.B. AND Coenen, A. AND Rich, A.S. AND Gureckis, T.M.},
	Organization = {New York University},
	Title = {psiTurk (Version 1.02) [Software]},
	Url = {https://github.com/NYUCCL/psiTurk},
	Year = {2012}
}
```


