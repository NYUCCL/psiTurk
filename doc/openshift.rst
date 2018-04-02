Using psiTurk on OpenShift
==========================

.. note::

    Consider trying the `OpenShift PsiTurk cartridge <https://github.com/deargle/openshift-psiturk-cartridge>`__. It involves less configuration, and you automatically
    get an nginx server in front of psiturk.

Get an OpenShift account
------------------------

Setting up an OpenShift account is relatively easy. First, visit `openshift.com <https://www.openshift.com>`__ and sign up for a new account. After verifying your account, choose the first step in the quick start guide, which starts taking you through the process of setting up an application. You want do to the following:


1. When choosing the type of application, select Python 2.7.
2. In the configuration step, choose a name as your public url that you would be happy for external visitors (i.e. your participants) to see. You do not need to link your application to a Git repository.
3. Before getting started, OpenShift will also ask you for a public SSH key. `Here <https://help.github.com/articles/generating-ssh-keys>`__ are some good instructions on how to find out whether you already have one, and to create one otherwise.

And that's it, you should now have created a python cartridge that you can use to run **psiTurk** experiments!

To access your application, visit the application overview page on OpenShift, click on your newly created python application, and under "Remote Access", copy the ssh command and paste it into your local terminal (Note: Windows users probably want to use an SSH client like PuTTY instead. Instructions for using PuTTY can be found `here <https://www.openshift.com/developers/install-and-setup-putty-ssh-client-for-windows>`__.). This should start a new OpenShift session. The command should look like this:


::

    ssh SOMENUMBER@python-MYNAME.rhcloud.com


Using psiTurk on OpenShift
--------------------------

There are some idiosyncrasies involved in running psiTurk using OpenShift that you want to be aware of:

* You don't need to use 'sudo' to install psiTurk. Simply "pip install" from either pypi or github (see `Installation Steps <install.html#installation-steps>`__). "pip" is already included in your python application, so you don't need to install it.

* You do not have root access on OpenShift, so rather than placing the ".psiturkconfig" file in the root directory, psiTurk automatically stores it in "/app-root/data". So that's where you have to enter your AWS and psiTurk access keys. (Remember, the file gets created only after psiturk is run for the first time)

* Similarly, in order to make any changes or add files (e.g to start a new project), you need to cd into a directory where you have permission to do so. For example, you could use "/app-root/repo/".

* Note that on OpenShift, you can only edit text files (like ".psiturkconfig" or "config.txt") inside the terminal. If you don't know how to do that, one simple way is to use "nano", for example: ::

    nano config.txt # edit file, then exit with Ctr+X

* In your very first session, the port that you need to host your experiment (port "8080" - see below) will be blocked by another process, so you will have to kill it first. You can do so by first looking for the process, then grabbing its Process ID (the PID column) and killing it: ::

    $ lsof -i :8080
    $ kill INSERT_PID


Customize a new project
-----------------------

To run a psiTurk experiment (like the example Stroop task) you need to make two changes to the config.txt file, without which your experiment won't run on OpenShift:

1. The 'port' field needs to be set to '8080'
2. The 'host' field needs to hold your specific OpenShift ip address, which you can easily find like this:

::

    echo $OPENSHIFT_PYTHON_IP


Example of first session
------------------------

To put it all together, this is what your first OpenShift session could look like, in which you install psiturk and try out the Stroop task example.
::

    $ pip install git+git://github.com/NYUCCL/psiTurk.git@dev
    $ lsof -i :8080
    $ kill INSERT_PID
    $ cd app-root/repo/
    $ psiturk-setup-example
    $ cd psiturk-example
    $ echo $OPENSHIFT_PYTHON_IP
    $ nano config.txt # add IP and port number (8080) to config file and exit
    $ psiturk # Start psiturk

Before you can go live, remember to change the global config file ("/app-root/data/.psiturkconfig").
