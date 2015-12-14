Configuring Databases
======================

Databases provide a critical aspect of psiTurk as they store data from experiments and help to prevent the same user from completing your experiment more than once.   Databases provide an important function for web-based experiments.  Because multiple
people can complete your experiment at the same time, you need a system which can simultaneously write/read data. 
Databases are optimized for this type of environment and are thus very useful for experiments.

Databases can be configured via the command line or by editing the configuration files directly.
See the `db command documentation <command_line/db.html>`__ for a full list of database commands available in the **psiTurk** shell.  You can also view your current
database settings by typing::

	[psiTurk server:off mode:sdbx #HITs:0]$ db get_config

in the command line shell.


.. seealso::

   `Database parameters <config/database_parameters.html>`__
      For details on how to configure databases in `config.txt`.

   `Local configuration file <configuration.html#local-configuration-file>`__
      For details on the local configuration file `config.txt`.


Using SQLite
--------------

Perhaps the simplest solution is to use SQLite.  This is a simple, easy to use database solution that is written to a local file on the same computer as is running the psiTurk shell/server.  By default **psiTurk** will use a local `SQLite <http://www.sqlite.org/>`__ database.

To use a SQLite data base, simply set the `database_url` field in your `local configuration file <configuration.html#local-configuration-file>`__ (`config.txt`)::

	database_url = sqlite:///FILENAME.db

where FILENAME is of your choosing.  By default, **psiTurk** sets this like this::

	database_url = sqlite:///participants.db

This will make a SQLite database file in the top-level folder of your project.  If you change the `database_url`
and restart **psiTurk** a new database corresponding to the new filename will be created.  If you set it to an
existing file name, **psiTurk** will attempt to connect to this database.

You can also change this setting using the `command line <command_line_overview.html>`__::

	[psiTurk server:off mode:sdbx #HITs:0]$ db use_local_file FILENAME.db

and verify the changes using::

	[psiTurk server:off mode:sdbx #HITs:0]$ db get_config


It is best to do this while the server is not running (note in this example the "server" status says "off").
If you change this while the server is running you will need to type::

	[psiTurk server:on mode:sdbx #HITs:0]$ server restart

While great for debugging, SQLite has a number of important downsides for deploying experiments. In particular SQLite does not allow concurrent access to the database, so if the locks work properly, simultaneous access (say, from multiple users submitting their data at the same time) could destabilize your database. In the worst scenario, the database could become corrupted, resulting in data loss.

As a result, we recommend using a more robust database solution when actually running your experiment. Luckily, **psiTurk** can help you set up such a database (usually for free).

However, SQLite is a good solution particularly for initial testing.  It is also possible to try to "throttle" the
rate of signups on Mechanical Turk (by only posting one assignment slot at a time) so that database errors are
less likely using SQLite.

.. note::

	SQLite database are fine for local testing but more robust databases like MySQL are recommended especially
	if you plan to run many participants simultaneously.

Using a self-hosted MySQL database (recommended)
-------------------------------------------------

A more robust solution is to set up a `MySQL <http://www.mysql.com/>`__ database.  **psiTurk** relies on `SQLAlchemy <http://www.sqlalchemy.org/>`__ for interfacing with database which means it is easy to switch between MySQL, PostgreSQL, or SQLite.  We recommend
MySQL because we have tested it, but other relational database engines may works as well.

To use an existing MySQL database::

	database_url = mysql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE

where USERNAME and PASSWORD are your access credentials for
the database, HOSTNAME and is the DNS entry or IP address for the
database, PORT is the port number (standard is 3306) and DATABASE
is the name of the database on the server.  

It is wise to test that you can connect to this url with a MySQL client prior to 
launching.  `Sequel Pro <http://www.sequelpro.com/>`__ is a nice GUI database
client for MySQL for Mac OS X.

Here's an example of setting up a minimal MySQL database for use with
**psiTurk**:

::

   $ mysql -uroot -p
   mysql> CREATE USER 'your_username'@'localhost' IDENTIFIED BY 'your_password';
   Query OK, 0 rows affected (0.03 sec)

   mysql> CREATE DATABASE your_database;
   Query OK, 1 row affected (0.01 sec)

   mysql> GRANT ALL PRIVILEGES ON your_database.* TO 'your_username'@'localhost';
   Query OK, 0 rows affected (0.00 sec)

where `your_username`, `your_password` and `your_database` match the `USERNAME`,
`PASSWORD` and `DATABASE` specified in config.txt's `database_url` variable.

The table specified in config.txt, `turkdemo` by default

::

   table_name = turkdemo

will be created automatically when running the psiturk shell.
MySQL is (fairly) easy to install and free.  However, a variety of web hosting
services offer managed MySQL databases.  Some are even 
`free <https://www.google.com/search?q=free+mysql+hosting>`__.  Your university
may be able to provide this as well.  MySQL is a very ubiquitous piece of software.

Obtaining a low-cost (or free) MySQL database on Amazon's Web Services Cloud
---------------------------------------------------------------------------

While not terribly difficult, installing and mangaging a MySQL database can be 
an extra hassle.  Interestingly, when you sign up with Amazon Mechanical Turk
as a requester, you also are signing up for Amazon's Web Services a very powerful
cloud-based computing platform that is used by many large web companies.  One of
the services Amazon provides is a fully hosted `relational database server (RDS) <http://aws.amazon.com/rds/>`__.

According to Amazon, "Amazon Relational Database Service (Amazon RDS) is a web 
service that makes it easy to set up, operate, and scale a relational database in 
the cloud. It provides cost-efficient and resizable capacity while managing 
time-consuming database administration tasks, freeing you up to focus on your 
applications and business."

.. danger::

	If you use Amazon's RDS to host your MySQL database you may incur additional
	charges.  At the present time a small RDS instance is free if you have
	recently signed up for Amazon Web Services.  However, older account have to
	pay according to the `current rates <http://aws.amazon.com/rds/pricing/>`__.
	This does **NOT** use the pre-paid mechanism that is used on Amazon
	Mechanical Turk.  Thus launching a database server on the cloud and leaving
	it running run up monthly charges.  You are responsible for launching
	and shutting down your own database instances if you use this approach.
	**PROCEED WITH CAUTION.**

The **psiTurk** `command line <command_line_overview.html>`__ provides a way to
create a small MySQL database on Amazon's cloud using the RDS service.
The command for this are available under the `db` command.  Type::

	[psiTurk server:off mode:sdbx #HITs:0]$ db help

for a list of sub-commands.  The commands that begin with `aws_` directly
interface with the Amazon cloud.

.. note::

	Of course, you must have valid AWS credentials to use this system.  See
	`Getting setup with Amazon Mechanical Turk <amt_setup.html>`__ and
	`Global configuration file <configuration.html#global-configuration-file>`__.


AWS Regions
~~~~~~~~~~~

AWS divides their cloud into different "regions" based on the location of the
data center.  To see a list of available regions type::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_regions

This command will also show which region you are currently using.  The
region is also set in your `~/.psiturkconfig` `Global configuration file <configuration.html#global-configuration-file>`__.
You can also get the current region by typing::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_get_region

To change your region simply type::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_set_region [<region_name>]

where `region_name` is one of the options listed by `db aws_list_regions`.

Why is this important?  If you start an instance in one region, then switch regions,
it will not show up in your list anymore.  The regions are sort of independent from
one another.  Thus it is important to remember **which region** your instance was
started on (i.e., which data center).

.. note::

	It is probably fine to just keep the region set to a single value
	perhaps geographically closer to your location.  This functionality is just
	provided in case the default region isn't working for you.


Creating an RDS Instance
~~~~~~~~~~~~~~~~~~~~~~~~~

After you have decided on a region, it is fairly easy to create a database instance.
Type::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances

to see all available instances associated with your account **in the current region**.
If you haven't created any instances in this region yet you should get a message like::

	There are no DB instances associated with your AWS account in region  us-east-1

To create a new instance use the `db aws_create_instance` command::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_create_instance [<instance_id> <size> <username> <password> <dbname>]

The optional arguments allow you to create the database in one command.  If you 
prefer you can use an interactive mode by just typing::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_create_instance

This will print the following message describing the various options you need
to specify for your database instance::

	*************************************************
	Ok, here are the rules on creating instances:

	instance id:
	  Each instance needs an identifier.  This is the name
	  of the virtual machine created for you on AWS.
	  Rules are 1-63 alphanumeric characters, first must
	  be a letter, must be unique to this AWS account.

	size:
	  The maximum size of you database in GB.  Enter an
	  integer between 5-1024

	master username:
	  The username you will use to connect.  Rules are
	  1-16 alphanumeric characters, first must be a letter,
	  cannot be a reserved MySQL word/phrase

	master password:
	  Rules are 8-41 alphanumeric characters

	database name:
	  The name for the first database on this instance.  Rules are
	  1-64 alphanumeric characters, cannot be a reserved MySQL word
	*************************************************

Then you will be prompted to specify values for these fields.
If you follow the rules correctly your command will execute successfully::

	enter an identifier for the instance (see rules above): mydb
	size of db in GB (5-1024): 5
	master username (see rules above): UsernameXXXXX
	master password (see rules above): PasswordXXXXX
	name for first database on this instance (see rules): myexp
	*****************************
	  Creating AWS RDS MySQL Instance
	    id:  mydb
	    size:  5  GB
	    username:  UsernameXXXXX
	    password:  PasswordXXXXX
	    dbname:  myexp
	    type: MySQL/db.t1.micro
	    ________________________
	 Be sure to store this information in a safe place.
	 Please wait 5-10 minutes while your database is created in the cloud.
	 You can run 'db aws_list_instances' to verify it was created (status
	 will say 'available' when it is ready

The instructions mention that it can take a few minutes for you database to
"spin up".  If you run `db aws_list_instances` after a few minutes you should
now see your database in the cloud::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances
	Here are the current DB instances associated with your AWS account in region  us-east-1
		--------------------
		Instance ID: mydb
		Status: creating

Notice the status is "creating" (this means the database is not available yet).  Just
wait a bit longer.  It really can take 10-15 minutes!  Other possible status messages
for an instance include `backing-up` (AWS automatically backs up your database in case 
of data loss.  At this time **psiTurk** does not help you access those backups, you'll 
have to do that from the AWS web console.)

When your database is ready the message from `db aws_list_instances` should look like::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances
	Here are the current DB instances associated with your AWS account in region  us-east-1
		--------------------
		Instance ID: mydb
		Status: available

If you have multiple instances they will also appear in this list. 

.. danger::

	Multiple instances increase the possible charges you'll incur to Amazon since you are charged
	per-instance.

Once your instance is created and "available" if you type `db get_config` you'll
notice that your experiment is still configured to use whatever setting you had
previously::

	[psiTurk server:off mode:sdbx #HITs:0]$ db get_config 
	Current database setting (database_url): 
		sqlite:///participants.db

To actually **use** your instance you need to tell **psiTurk** which instance::

	[psiTurk server:off mode:sdbx #HITs:0]$ db use_aws_instance mydb
	Switching your DB settings to use this instance.  Are you sure you want to do this? y
	enter the master password for this instance: PasswordXXXXX
	AWS RDS database instance mydb selected.
	Here are the available database tables
		myexp
	Enter the name of the database you want to use or a new name to create a new one: myexp
	Successfully set your current database (database_url) to 
		mysql://UsernameXXXXX:PasswordXXXXX@mydb.cdukgn44bkrv.us-east-1.rds.amazonaws.com:3306/myexp

And now your experiment will save data to this MySQL database in the Amazon cloud!
Notice that Amazon has assigned your computer a random looking hostname/ip (mydb.cdukgn44bkrv.us-east-1.rds.amazonaws.com).
You can connect using any standard MySQL client (e.g., `Sequel Pro <http://www.sequelpro.com/>`__) 
which is running on the same computer as you **psiTurk** process

.. note::

	**psiTurk** automatically makes instances so that only the current computer's ip address 
	can access the database for security reasons.  To modify that you can use the Amazon Web 
	Services control panel or simple delete and spin up a new database instance.


To switch back to a local SQLite file::

	[psiTurk server:off mode:sdbx #HITs:0]$ db use_local_file FILENAME.db
	Updated database setting (database_url): 
		sqlite:///FILENAME.db

It is **important** that you delete your instance when you are finished using it.
Otherwise you will be charged (usually fractions of a penny per hour).  Assuming
I wanted to delete my new `mydb` instance here is an example session::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances 
	Here are the current DB instances associated with your AWS account in region  us-east-1
		--------------------
		Instance ID: mydb
		Status: available
	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_delete_instance 
	Here are the available instances you can delete:
		  mydb ( available )
	Enter the instance identity you would like to delete: mydb
	Deleting an instance will erase all your data associated with the database in that instance. Really quit? y or n: y
	DBInstance:mydb
	AWS RDS database instance mydb deleted.  Run `db aws_list_instances` for current status.	
	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances 
	Here are the current DB instances associated with your AWS account in region  us-east-1
		--------------------
		Instance ID: mydb
		Status: deleting		

After waiting a bit verify that you instance actually has been deleted::

	[psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances 
	There are no DB instances associated with your AWS account in region  us-east-1

Overall we think this is pretty cool and nicely leverages the fact that you already
got a Amazon Web Services account when you signed up to use Amazon Mechanical Turk!
However, remember, this **can incur hosting charges**.  We have set things up so that this
process creates very small, very simple RDS instances (which are the cheapest kind).
However, leaving an instance running -- or multiple instances -- for a really long
time can incur service charges which will be billed to your account by Amazon at the
end of the month (you may not realize the charges until later).  

The point is that using a free MySQL database hosted by your university or another
provider may be better, but this solution is available for researchers who can 
afford to pay the hosting fee and would like everything in one place.
