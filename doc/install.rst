Getting **psiTurk** Installed on Your Computer
===============================================

**psiTurk** can be installed on any modern computer which supports
Python (<= 2.7). However, currently **psiTurk** is *not* supported on
Windows (`see below <#windows>`__). It works well on most unix variants
including Mac OS X, BSD, and Linux. Installation is *usually* not
difficult.

When **psiTurk** is successfully installed, you will simply have a new
command line tool available called ``psiturk``. The ``psiturk`` command
provides a number of functions to you including launching the server
and interacting with the Mechanical Turk and Amazon Web Services (AWS)
systems.


Installation requirements
-------------------------

Installation of **psiTurk** requires:

1. **A python installation (<= v2.7).** We recommend the `Enthought
   python distribution <https://www.enthought.com/products/epd/free/>`__
   on Mac OS X.
2. **The ``pip`` package manager.** Directions on installing this are
   given below.
3. **Access to a command line tool.** (e.g., Terminal.app on Mac OS X)
4. **A web browser.** A WebKit compatible browser such as FireFox,
   Safari, or Chrome is recommended.

An additional requirement for actually using **psiTurk** to run experiments
is an Internet connected computer capable of receiving incoming requests.


Installation steps
------------------

To install the package there are two options currently. First, the
current stable release of **psiTurk** is hosted on the python package
index `pypi <https://pypi.python.org/pypi>`__. As a result, it can
easily be installed as a standard python package using the python
package manager tool ``pip``. Alternatively, you can install directly
from the development branch on
`github <https://github.com/NYUCCL/psiTurk>`__. The following
instructions describe the general process. In addition, system specific
notes are provided below.


Install stable version via pypi
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install **psiTurk** is via ``pip``. Linux users will
likely prefer to install pip as described `below <#linux>`__.
Otherwise, If you don't already have ``pip``, you can install it by
typing the following in a terminal:


::

    cd /tmp  # Just to put us in a directory that will be cleaned up periodically
    curl -O https://raw.githubusercontent.com/pypa/pip/develop/contrib/get-pip.py
    python get-pip.py  # If you get a permissions error, try typing sudo python get-pip.py

If you want a single system to run different versions of **psiTurk**
(or other python packages) on a per-experiment basis, follow the
Virtual Environment instructions `below <#Running inside a Virtual
Environment>`__.

Once ``pip`` is installed, type into a terminal:

::

    pip install psiturk

If this doesn't work, try

::

    sudo pip install psiturk

If the install was successful you will have a new command ``psiturk``
available on your command line. You can check the location of this
command by typing

::

    which psiturk


Install directly from github
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also install the bleeding-edge development version directly
from github using ``pip``. To install the latest stable branch follow
the instructions above to install ``pip`` and:

::

    sudo pip install git+git://github.com/NYUCCL/psiTurk.git@master

If the install was successful you will have a new command ``psiturk``
available on your command line. You can check the location of this command
by typing

::

    which psiturk


Updating from a previous version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To avoid compatibility issues, if you upgrade from a previous version it
can be useful to first uninstall then reinstall **psiTurk** using the
following sequence of commands:

::

    $ pip uninstall psiturk
    $ git clone git@github.com:NYUCCL/psiTurk.git
    $ cd psiTurk
    $ sudo python setup.py install


Running inside a Virtual Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It can desirable to keep each of your experiments' dependencies (python
and python package versions) isolated from each other. For example, if
you want to install the development version of psiTurk (as
described `above <#install-directly-from-github>`__) in one experiment,
but not all the others installed on your system, `Virtual Environments
<http://virtualenv.readthedocs.org/en/latest/>`__ provide a solution.

You can install via pip:

::

   sudo pip install virtualenv virtualenvwrapper

And then start a new shell session. This will install the virtualenv
tool as well as the supplementary virtualenvwrapper tools that make
working with virtualenvs easier. You create a virtual environment as
follows (if mkvirtualenv is not recognized follow the instructions
`here
<http://virtualenvwrapper.readthedocs.org/en/latest/install.html>`_) :

::

   $ mkvirtualenv my-experiment

   Running virtualenv with interpreter /usr/bin/python2
   New python executable in my-experiment/bin/python2
   Also creating executable in my-experiment/bin/python
   Installing setuptools, pip...done.

Then, at any point in the future, to activate the virtual environment use the workon command

::

   $ workon my-experiment
   (my-experiment) $ which python python pip easy_install

   ~/.virtualenvs/my-experiment/bin/python
   ~/.virtualenvs/my-experiment/bin/pip
   ~/.virtualenvs/my-experiment/bin/easy_install

As you can see, when the environment is active, running python or pip
will run copies specific to your project. Any packages installed with
pip or easy_install will be installed inside your my-experiment
virtualenv rather than system-wide. Use the `deactivate` command to
leave the virtualenv.


System-specific notes
---------------------


Mac OS X
~~~~~~~~

Apple users will need to install a C compiler via XCode; to do so,
install XCode from the App store. Once you have downloaded it, install
the command line tools from the preferences menu as instructed
`here <http://stackoverflow.com/a/9353468/62179>`__. For earlier
versions of Mac OS X (e.g., Snow Leopard) you may need to install XCode
using the installation disc that came with your computer. The command
line tools are an option during the installation process for these
systems.


Linux
~~~~~

**psiTurk** is relatively painless to install on most Linux systems
since all four of the requirements listed above come installed by
default in most distributions.

If you encounter install problems when installing using pip as above, a
likely cause is that you are missing the package from your distribution
that contains a needed header file.  In this case, one way to troubleshoot
the problem is to do a web search for the name of your distribution and
the name of the missing header file (which often appears in the error text
produced by a failed pip install).  That search will likely turn up the name of
the package for your distribution that supplies the needed header file.

As an example, before installing psiTurk on a minimal Debian 7 server
(such as the one provided by many server hosting companies) you will need
to install some additional packages, as illustrated by the following
example command:

::

    aptitude install python-pip python-dev libncurses-dev

If you would like to use mysql as your backend database (which is optional, and can
be done at any time), further packages are needed.  On a Debian system, they are:

::

    aptitude install python-mysqldb python-mysqldb-dbg python-sqlalchemy libmysqlclient-dev

If you have additional specific issues, or if you can report the steps
needed to install psiTurk on a particular Linux distribution, please help
us update the documentation!


Windows
~~~~~~~

**psiTurk** is currently not supported on Windows. This is due to a
technical limitation in the ability to run server processes on Windows.
We currently recommend that Windows users try a cloud-based install such
as `openshift <https://www.openshift.com>`__.


Cloud-based install (experimental)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your local computer does not support **psiTurk** is it still possible
to use the package by using a free hosting solution such as
`openshift <https://www.openshift.com/>`__. Begin by creating an account
at http://openshift.redhat.com/ and download the command line tools at
https://www.openshift.com/developers/rhc-client-tools-install

Create a python-2.7 application and add a PostgreSQL cartridge to the
app

::

    rhc app create psiturk python-2.7 postgresql-8.4 --from-code git://github.com/jbmartin/psiturk-on-openshift.git

or you can do this to watch the build

::

    rhc app create -a psiturk -t python-2.7
    rhc cartridge add -a psiturk20 postgresql-8.4

Add this upstream psiturk repo

::

    cd psiturk
    git remote add upstream -m master https://github.com/jbmartin/psiturk-on-openshift.git
    git pull -s recursive -X theirs upstream master

Then push the repo upstream

::

    git push

That's it, you can now checkout your application at

::

    http://psiturk-$YOURNAMESPACE.rhcloud.com

To access the your openshift hosted database run

::

    rhc port forward -a psiturk

Connect to the database using your favorite SQL app, the PostgreSQL
Local specs, and your credentials.
