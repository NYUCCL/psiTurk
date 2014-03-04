<img src="https://www.psiturk.org/static/images/psiturk_logo.jpg">


#### An open platform for science on Amazon's Mechanical Turk.

It is intended to provide most of the backend machinery necessary to run dynamic
and interactive behavioral experiments on Amazon Mechanical Turk (AMT). As long 
as you can turn your experiment into a dynamic webpage, you can run it with 
**psiTurk**!

*Some Features*

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
  - Develop and test without an Internet connection (airplanes, etc...)

Please visit [psiturk.org](https://psiturk.org) for more information.

Install
=======

The easiest way to install **psiTurk** is via `pip`.
Simply type into a terminal:

    pip install psiturk 

If this doesn't work, you might try `sudo pip install psiturk`.  Directions
on how to install `pip` if you don't have it on your system are available in 
our [documentation](http://psiturk.readthedocs.org/en/latest/).



Copyright
=========
You are welcome to use this code for personal or academic uses. If you fork,
or use this in an academic paper please cite as follows:

McDonnell, J.V., Martin, J.B., Markant, D.B., Coenen, A., Rich, A.S., and Gureckis, T.M. 
(2012). psiTurk (Version 1.02) [Software]. New York, NY: New York University. 
Available from https://github.com/NYUCCL/psiTurk



