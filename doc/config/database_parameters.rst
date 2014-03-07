Database Parameters
===================

The Database Parameter section contains details about
your database.  An example looks like this:

::

	[Database Parameters]
	database_url = sqlite:///participants.db
	table_name = turkdemo

.. seealso::

   `Configuring Databases <../configure_databases.html>`__
      For details on how to set up different databases and
      get your data back out.

   `Recording Data <../recording.html>`__
   	  For details on how to put data into your database.


`database_url` [url string]
-------------------------
`database_url` containes the location and access credentials
for your database (i.e., where you want the data from your
experiment to be saved).  

To use a SQLLite data base, simply type the name of the
file::

	database_url = sqlite:///participants.db

This example would write to a database file with the name
"participants.db" in the top-level directory of your experiment.

To use an existing MySQL database::

	database_url = mysql://USERNAME:PASSWORD@HOSTNAME:PORT/DATABASE

where USERNAME and PASSWORD are your access credentials for
the database, HOSTNAME and is the DNS entry or IP address for the
database, PORT is the port number (standard is 3306) and DATABASE
is the name of the database on the server.  It is wise to test
that you can connect to this url with a MySQL client prior to 
launching.

`table_name` [string]
--------------------
`table_name` specifies the table of the database you would like
to write to.  **IMPORTANT**: psiTurk prevents the same worker
from performing as task by checking to see if the worker
appears in the current database table already.  Thus, for a
single experiment (or sequence of related experiments) you want
to keep the `table_name` value the same.  If you start a new
design where it not longer matters that someone has done a 
previous version of the task, you can change the `table_name`
value and begin sorting the data into a new table.
