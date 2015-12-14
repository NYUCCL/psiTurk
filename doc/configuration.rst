Configuration Files
===================

There are two types of configuration files for **psiTurk**.
Configuration files contain information needed to run an experiment
as well as options which control how **psiTurk** behaves.

The first file is a "global" configuration file and resides
in your home folder (`~/.psiturkconfig`).  The second file is
a "local" configuration file and resides in the folder of
each experiment.

In general the "global" configuration file sets project-wide
configuration options (i.e., those you want set the same
for all the experiments or projects you are working on).
The "local" configuration file contains the unique settings for
individual experiments.


.. note::

   In general, changes to either the local and global file
   require restarting the server process as it may change
   the behavior.  Generally it is best to edit these files while
   psiturk is not running, and then restart the command shell.



Global configuration file
--------------------------

The global configuration file resides in your
home folder in a "dot" file (`/.psiturkconfig`).  This
file is created automatically either the first time you
run the `psiturk` command line tool or the first time
you run `psiturk-setup-example`.  The default file looks
like this:

::

	[AWS Access]
	aws_access_key_id = YourAccessKeyId
	aws_secret_access_key = YourSecretAccessKey
	aws_region = us-east-1

	[psiTurk Access]
	psiturk_access_key_id = YourAccessKeyId
	psiturk_secret_access_id = YourSecretAccessKey


Other options can be added if you would like those
to be global to all your projects.  The default options
include your access credentials/API keys for
`Amazon Web Services <amt_setup.html>`__ (and Mechanical Turk)
as well as `psiturk.org <psiturk_org_setup.html>`__.
You can learn how to obtain proper values for these
settings by following those links.

You can customize the location of this file to something
other than the ~ folder by setting the `PSITURK_GLOBAL_CONFIG_LOCATION` 
in your shell environment.

Local configuration file
--------------------------

The local configuration file is specific to each
project and resides in a file called `config.txt` in the
top level of the project.  Here is what `config.txt`
looks like for the default **psiTurk** `stroop <stroop.html>`__
project:

::

	[HIT Configuration]
	title = Stroop task
	description = Judge the color of a series of words.
	amt_keywords = Perception, Psychology
	lifetime = 24
	us_only = true
	approve_requirement = 95
	contact_email_on_error = youremail@gmail.com
	ad_group = My research project
	psiturk_keywords = stroop
	organization_name = New Great University
	browser_exclude_rule = MSIE, mobile, tablet

	[Database Parameters]
	database_url = sqlite:///participants.db
	table_name = turkdemo

	[Server Parameters]
	host = 0.0.0.0
	port = 22362
	cutoff_time = 30
	logfile = server.log
	loglevel = 2
	debug = true
	login_username = examplename
	login_pw = examplepassword
	threads = auto

	[Task Parameters]
	experiment_code_version = 1.0
	num_conds = 1
	num_counters = 1

	[Shell Parameters]
	launch_in_sandbox_mode = true

This file is divided into a few sections which are
described in detail.  Each field is described by
name and includes in brackets the type of data it
expects.

.. note:: Any configuration option can actually be placed in either
   the global or local configuration file. For example, if you
   wanted to run different project from different AWS accounts, you
   could add an ``[AWS access]`` section to move the local `config.txt` files and
   have different values in different folders. Likewise, if you wanted
   to have the same `organization_name` in all your experiments, you
   could add a ``[HIT Configuration]`` section with an
   `organization_name` field to your `~/.psiturkconfig` file. Keep in
   mind that **settings in the local `config.txt` file always override
   settings in the global `~/.psiturkconfig` file**.

.. toctree::

	config/hit_configuration.rst
	config/database_parameters.rst
	config/server_parameters.rst
	config/task_parameters.rst
	config/shell_parameters.rst
