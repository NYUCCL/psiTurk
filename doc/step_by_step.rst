Step-by-step Tutorials
==========================================

**psiTurk** is a system for interfacing with Amazon
Mechanical Turk.  Thus, you need to create an account
on Amazon's website in order to use it.

Overview of the command line interface
---------------------------------------

An AWS key is required for posting new HITs to mechanical turk as well as monitoring existing HITs. You receive your key when you open an Amazon Web Services account. If you already have an AWS account, your key can be retrieved 
`here <http://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key?`__.

Configuring databases
----------------------------------
Databases provide a critical aspect of psiTurk as they store data from experiments and help to prevent the same user from completing your experiment more than once.

By default psiTurk will use a local SQLLite database. This is a simple, easy to use database solution that is written to a local file on the same computer as is running the psiTurk shell/server.

While completely OK for debugging, SQLLite has a number of important downsides for deploying experiments. In particular SQLite does not allow concurrent access to the database, so if the locks work properly, simultaneous access (say, from multiple users submitting their data at the same time) could destabilize your database. In the worst scenario, the database could become corrupted, resulting in data loss.

As a result, we recommend using a more robust database solution when actually running your experiment. Luckily, psiTurk can help you set up such a database (usually for free).


Getting up and running with the basic Stroop task
----------------------------------

Decomposing the Stroop task
----------------------------------
