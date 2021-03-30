.. _install:

============
Installation guide
============

psiTurk is supported for python >= v3.6 on any `Unix-Like`_ operating system
(i.e., :ref:`not Windows <install-on-windows>`).

.. _Unix-Like: https://en.wikipedia.org/wiki/Unix-like

When psiTurk is successfully installed, you will have a new
command line tool available called ``psiturk``. The ``psiturk`` command
provides a number of functions to you including launching the server
and interacting with the Mechanical Turk and Amazon Web Services (AWS)
systems.


Requirements:

* ``python`` (>= v3.6)
* ``pip`` (to install, see `here <https://pip.pypa.io/en/stable/installing/>`__.)

To install the latest released version of psiTurk::

    pip install psiturk

To upgrade psiturk::

    pip install -U psiturk


From Source
===========

You can install the bleeding edge version of psiTurk from source just as you
would install any other Python package::

    pip install git+https://github.com/NYUCCL/psiturk.git

To update from source::

    pip install -U git+https://github.com/NYUCCL/psiturk.git


Running inside a Virtual Environment
====================================

It can desirable to keep each of your experiments' dependencies (python
and python package versions) isolated from each other. For example, if
you want to install the development version of psiTurk (as
described `above <#install-directly-from-github>`__) in one experiment,
but not all the others installed on your system, `Virtual Environments
<http://virtualenv.readthedocs.org/en/latest/>`__ provide a solution.

You can install via pip::

   sudo pip install virtualenv virtualenvwrapper

This will install the virtualenv tool as well as the supplementary
virtualenvwrapper tools that make working with virtualenvs easier. You create a
virtual environment as follows::

   $ mkvirtualenv my-experiment

   Running virtualenv with interpreter /usr/bin/python2
   New python executable in my-experiment/bin/python2
   Also creating executable in my-experiment/bin/python
   Installing setuptools, pip...done.

(if ``mkvirtualenv`` is not recognized, follow the instructions
`here
<http://virtualenvwrapper.readthedocs.org/en/latest/install.html>`_)

Then, at any point in the future, to activate the virtual environment, use the
workon command::

   $ workon my-experiment
   (my-experiment) $ which python python pip easy_install

   ~/.virtualenvs/my-experiment/bin/python
   ~/.virtualenvs/my-experiment/bin/pip
   ~/.virtualenvs/my-experiment/bin/easy_install


As you can see, when the environment is active, running python or pip
will run copies specific to your project. Any packages installed with
``pip`` or ``easy_install`` will be installed inside your my-experiment
virtualenv rather than system-wide.

Install psiTurk as above into the _virtual_ environment-- i.e., with the virtual
environment activated.::

(my-experiment) $ pip install psiturk

You can use the ``deactivate`` command to leave the virtualenv.


System-specific notes
=====================

Mac OS X
--------

Apple users will need to install a C compiler via XCode; to do so,
install XCode from the App store. Once you have downloaded it, install
the command line tools from the preferences menu as instructed
`here <http://stackoverflow.com/a/9353468/62179>`__. For earlier
versions of Mac OS X (e.g., Snow Leopard) you may need to install XCode
using the installation disc that came with your computer. The command
line tools are an option during the installation process for these
systems.


.. _install-linux:

Linux
-----

psiTurk is relatively painless to install on most Linux systems
since the installation requirements come installed by
default in most distributions.

If you encounter install problems when installing using pip as above, a
likely cause is that you are missing the package from your distribution
that contains a needed header file. In this case, one way to troubleshoot
the problem is to do a web search for the name of your distribution and
the name of the missing header file (which often appears in the error text
produced by a failed pip install). That search will likely turn up the name of
the package for your distribution that supplies the needed header file.

As an example, before installing psiTurk on a minimal Debian server
(such as the one provided by many server hosting companies) you will need
to install some additional packages, as illustrated by the following
example command::

    apt install python-pip python-dev libncurses-dev

If you would like to use mysql as your backend database (which is optional, and can
be done at any time), further packages are needed. On a Debian system, they are::

    apt install python-pymysql python-sqlalchemy libmysqlclient-dev

If you have additional specific issues, or if you can report the steps
needed to install psiTurk on a particular Linux distribution, please help
us update the documentation!


.. _install-on-windows:

Windows
-------

psiTurk is currently not supported on Windows. This is due to a
technical limitation in the ability to run server processes on Windows.
However, there are a number of options to get around this (see below for details
on each option):

- `Windows Subsystem for Linux (WSL)`_ on Windows 10. **Recommended**.
- Virtualization through `VirtualBox <https://www.virtualbox.org/>`_ or similar software.

.. _Windows Subsystem For Linux (WSL): https://docs.microsoft.com/en-us/windows/wsl/install-win10


Windows Subsystem for Linux (WSL)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Windows now has the option to run a Linux translation layer inside Windows
(WSL 1) or even a full Linux kernel (WSL 2). Either will allow you to run psiturk
within the Linux subsystem.
See https://docs.microsoft.com/en-us/windows/wsl/install-win10 for instructions
on how to activate WSL on your system.

After you activate WSL and install a Linux distribution of choice, install psiturk
within a WSL-connected command prompt as above for :ref:`install-linux`.


Virtualization
^^^^^^^^^^^^^^

.. warning::
    WSL may not be compatible with concurrent usage of other hypervisors.

You can install a program like `VirtualBox`_ on your pc. Programs like
these are called hypervisors and emulate a computer within your computer. Your physical machine is called
a host and the virtual machine is called a guest. This technique allows you to install a Linux guest
regardless of what OS the host is running.

Virtualization requires some computing power from the host so this option is
not recommended if your psiturk experiment requires a lot of computing power as well or if it's is expected
to have a lot of participants active at once. However, it is a good option to develop and test your psiturk
experiments on Windows systems prior to Windows 10. If you are running Windows 10 or higher see below for
the WSL option, which is much easier on your system than virtualization.

After you install the virtual machine software you need an installation image for a Linux based OS. You can
choose any Linux distribution you like but `Ubuntu <https://ubuntu.com/download/desktop>`__ is a good choice
if you don't know which one to pick. You can usually obtain an \*.iso file for the Linux distribution you like.
These are virtual cd-roms. You can load them into your virtual machine and begin installing the guest OS.
Once that is complete you boot your virtual machine into Linux and follow the installation steps for Linux.
