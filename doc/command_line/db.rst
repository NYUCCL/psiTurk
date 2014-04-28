``db`` command + subcommands
============================

.. contents::


The ``db`` command is used with a number of subcommands to create and configure database
instances. More information about database configuration can be found
on the `Configuring Databases <../configure_databases.html>`__ page.

.. note::
   The ``aws_`` subcommands are used to interact with the Amazon Web
   Services Relational Database Server (RDS) cloud service.

``db get_config``
-------------------

Usage
~~~~~~~

::

   db get_config

Display the current setting of the database (`database_url
<../config/database_parameters.html#database-url-url-string>`__).

Example
~~~~~~~~

::

   [psiTurk server:off mode:sdbx #HITs:1]$ db get_config
   Current database setting (database_url):
       sqlite:///participants.db

``db use_local_file``
----------------------

Usage
~~~~~~~

::

   db use_local_file [<filename>]

Switch the current database to a local SQLite file with name `<filename>`
(default is `participants.db`), or enter without filename and provide
name when prompted.

Example
~~~~~~~~

Setting database to a local SQLite file:

::

   [psiTurk server:off mode:sdbx #HITs:1]$ db use_local_file
   Enter the filename of the local SQLLite database you would like to use [default=participants.db]: example.db
   Updated database setting (database_url):
	sqlite:///example.db
   [psiTurk server:off mode:sdbx #HITs:1]$


``db use_aws_instance``
------------------------

Usage
~~~~~~

::

   db use_aws_instance [<instance_id>]

Switch the current database to a given instance `<instance_id>` on AWS
RDS. Enter without an argument to display a list of instances from
which to choose.

Example
~~~~~~~~

Using an RDS database instance::

  [psiTurk server:off mode:sdbx #HITs:0]$ db use_aws_instance mydb
  Switching your DB settings to use this instance.  Are you sure you want to do this? y
  enter the master password for this instance: PasswordXXXXX
  AWS RDS database instance mydb selected.
  Here are the available database tables
          myexp
  Enter the name of the database you want to use or a new name to create a new one: myexp
  Successfully set your current database (database_url) to
          mysql://UsernameXXXXX:PasswordXXXXX@mydb.cdukgn44bkrv.us-east-1.rds.amazonaws.com:3306/myexp


``db aws_list_regions``
------------------------

Usage
~~~~~~

::

   db aws_list_regions

Lists available AWS regions.

Example
~~~~~~~~

::

   psiTurk server:off mode:sdbx #HITs:1]$ db aws_list_regions
   Avaliable AWS regions:
	us-east-1 (currently selected)
	us-gov-west-1
	eu-west-1
	us-west-1
	us-west-2
	sa-east-1
	ap-northeast-1
	ap-southeast-1
	ap-southeast-2


``db aws_get_region``
----------------------

Usage
~~~~~~~~

::

   db aws_get_region

Displays the current AWS region you are communicating with.

Example
~~~~~~~~

::

   [psiTurk server:off mode:sdbx #HITs:1]$ db aws_get_region
   us-east-1

``db aws_set_region``
----------------------

Usage
~~~~~~

::

   db aws_set_region [<region_name>]

Sets the AWS region you are currently using to `<region-name>`. Enter
without an argument to display a list of regions from which to choose.

Example
~~~~~~~

Setting region to `us-west-1`::

   [psiTurk server:off mode:sdbx #HITs:1]$ db aws_set_region us-west-1
   Region updated to  us-west-1

``db aws_list_instances``
---------------------------

Usage
~~~~~~

::

   db aws_list_instances

List instances and statuses in the current region/AWS account.

Example
~~~~~~~~

1. Listing instances when there are none active in your region::

     [psiTurk server:off mode:sdbx #HITs:1]$ db aws_list_instances
     There are no DB instances associated with your AWS account in region  us-east-1

2. Listing instances when there is an active instance in your region::

     [psiTurk server:off mode:sdbx #HITs:0]$ db aws_list_instances
     Here are the current DB instances associated with your AWS account in region  us-east-1
            --------------------
            Instance ID: mydb
            Status: available
 

``db aws_create_instance``
---------------------------

Usage
~~~~~~

::

   db aws_create_instance [<instance_id> <size> <username> <password>
   <dbname>]

Create an RDS instance using MySQL on the AWS cloud, with the given
instance id, size, username, password, and database name. ``db
aws_create_instance`` can also be run interactively by running the
command without parameters.

Example
~~~~~~~~

Interactively creating a database instance::

  [psiTurk server:off mode:sdbx #HITs:1]$ db aws_create_instance
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
  [psiTurk server:off mode:sdbx #HITs:1]$

``db aws_delete_instance``
---------------------------

Usage
~~~~~

::

     db aws_delete_instance [<instance_id>]

Delete the RDS instance with id `<instance_id>`. Enter without an
argument to display a list of instances from which to choose.

Example
~~~~~~~~

Deleting an AWS database instance::

  [psiTurk server:off mode:sdbx #HITs:0]$ db aws_delete_instance
  Here are the available instances you can delete:
              mydb ( available )
  Enter the instance identity you would like to delete: mydb
  Deleting an instance will erase all your data associated with the 
  database in that instance. Really quit? y or n: y
  DBInstance:mydb
  AWS RDS database instance mydb deleted.  Run `db aws_list_instances` for current status.
