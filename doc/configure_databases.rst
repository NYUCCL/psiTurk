Configuring Databases
======================

Databases provide a critical aspect of psiTurk as they store data from experiments and help to prevent the same user from completing your experiment more than once.

By default **psiTurk** will use a local `SQLLite <http://www.sqlite.org/>`__ database. This is a simple, easy to use database solution that is written to a local file on the same computer as is running the psiTurk shell/server.

While completely OK for debugging, SQLLite has a number of important downsides for deploying experiments. In particular SQLite does not allow concurrent access to the database, so if the locks work properly, simultaneous access (say, from multiple users submitting their data at the same time) could destabilize your database. In the worst scenario, the database could become corrupted, resulting in data loss.

As a result, we recommend using a more robust database solution when actually running your experiment. Luckily, **psiTurk** can help you set up such a database (usually for free).

Using SQLLite
--------------

Using a self-hosted MySQL database (recommended)
-------------------------------------------------

Obtaining a free or low-cost MySQL database on Amazon's Web Services Cloud
---------------------------------------------------------------------------