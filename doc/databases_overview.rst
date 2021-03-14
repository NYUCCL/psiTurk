.. _databases-overview:

==================
Databases Overview
==================

Databases provide a critical aspect of psiTurk, as they store data from
experiments and help to prevent the same user from completing your experiment
more than once. Databases provide an important function for web-based experiments --
Because multiple people can complete your experiment at the same time, you need
a system which can simultaneously write/read data. Databases are optimized for
this type of environment and are thus very useful for experiments.

psiTurk can integrate with any database that is compatible with `SQLAlchemy`_.

.. _SQLAlchemy: https://www.sqlalchemy.org/

.. seealso::

   :ref:`settings-database-url` -- For details on how to configure databases in `config.txt`

.. contents:: Contents
  :local:
  :depth: 1

Using SQLite
~~~~~~~~~~~~

Perhaps the simplest quickstart solution is to use SQLite. This database solution
writes to a local file on the same computer as is running the psiTurk server.

To use a SQLite data base, simply set the `database_url` field in your
`local configuration file <configuration.html#local-configuration-file>`__ (`config.txt`)::

	database_url = sqlite:///FILENAME.db

where FILENAME is of your choosing. By default, psiTurk sets this like this::

	database_url = sqlite:///participants.db

This will make a SQLite database file in the top-level folder of your project.
If you change the `database_url` and restart psiTurk, a new database corresponding
to the new filename will be created. If you set it to an
existing file name, psiTurk will attempt to connect to this database.

It is best to do this while the server is not running (note in this example the "server" status says "off").
If you change this while the server is running you will need to type::

	[psiTurk server:on mode:sdbx #HITs:0]$ server restart

While great for development and debugging, SQLite has a number of important downsides for
deploying experiments. In particular, SQLite does not allow concurrent access to
the database, so if the locks work properly, simultaneous access (say, from
multiple users submitting their data at the same time) could destabilize your
database. In the worst scenario, the database could become corrupted,
resulting in data loss.

As a result, we recommend using a more robust database solution when actually
running your experiment.

However, SQLite is a good solution particularly for initial testing.
It is also possible to try to "throttle" the rate of signups on Mechanical Turk
(by only posting one assignment slot at a time) so that database errors are
less likely using SQLite.

.. note::

	SQLite database are fine for local testing but more robust databases like
	MySQL are recommended especially if you plan to run many participants simultaneously.
	Again, any server compatible with `SQLAlchemy`_ can be used.


Using a postgresql database on Heroku
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Heroku free tier includes access to a postgresql database.
See :ref:`deploy-on-heroku`.


Using a SQL database server
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A more robust solution is to set up a `MySQL <http://www.mysql.com/>`__ database.
psiTurk's reliance on `SQLAlchemy`_ for interfacing
with database which means it is easy to switch between MySQL, PostgreSQL, or SQLite.

For example, to use an existing MySQL database::

	database_url = mysql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE

where USERNAME and PASSWORD are your access credentials for the database,
HOSTNAME is the DNS entry or IP address for the database, PORT is the port
number (default is 3306) and DATABASE is the name of the database on the
server.

Use 127.0.0.1 as the HOSTNAME for a database running locally to the psiTurk
server rather than 'localhost'. Mysql treats the HOSTNAME 'localhost' `as a
special case in Unix-based systems
<https://dev.mysql.com/doc/refman/8.0/en/connecting.html>`__
and will cause the psiTurk server to fail to boot.

It is wise to test that you can connect to this url with a MySQL client prior to
launching, such as `MySQL Workbench <https://www.mysql.com/products/workbench/>`__
`Sequel Pro <http://www.sequelpro.com/>`__.

Here's an example of setting up a minimal MySQL database for use with
psiTurk:

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

The table specified in config.txt::

   table_name = turkdemo

...will be created automatically when running the psiturk shell.
MySQL is (fairly) easy to install and free. However, a variety of web hosting
services offer managed MySQL databases. Some are even
`free <https://www.google.com/search?q=free+mysql+hosting>`__.

