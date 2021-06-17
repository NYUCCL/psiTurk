.. _dashboard-overview:

==================
Dashboard Overview
==================

A dashboard is available at route ``/dashboard``. The dashboard can be enabled
by setting :ref:`settings-enable-dashboard` to ``True``, and by setting a
:ref:`settings-login-username`, :ref:`settings-login-pw`, and :ref:`settings-secret-key`.



The dashboard has many features, including a dynamic filtered table, batch actions,
managing campaigns.

.. contents:: Contents
  :local:
  :depth: 1

Dynamic Filtered Table
~~~~~~~~~~~~~~~~~~~~~~

View current status of participants, queried from the psiTurk database.

* Filter by:

  * mode
  * experimental condition
  * current code version
  * whether the participant has a status of 'complete'

* Group by:

  * condition

Batch Actions
~~~~~~~~~~~~~

Functionality to manually trigger the following actions:

* Workers:

  - Approve all HITs
  - Bonus all submissions via the "auto" method (based on the value set in the
    "bonus" column in the database).

* HITS:

  - Expire all
  - Approve all workers for all hits
  - Delete all

.. _campaigns-overview:

Campaigns
~~~~~~~~~

Campaigns are scheduled as :ref:`tasks <tasks-overview>`. Campaigns have the
following features:

* Set a target "goal" for number of workers for a given task
  :ref:`code version <settings-experiment-code-version>`.
* Stagger the posting of HITs by a specified interval.
* Post HITs in batches of 9 assignments. This keeps the MTurk commission at 20%,
  instead of 40%.
* Monitors the number of available HITs, and continues posting rounds of HITs
  until the campaign goal has been met.
* Manually cancel a campaign.

The "Campaigns" tab also displays past campaigns.

.. _tasks-overview:

Tasks
~~~~~

psiTurk "tasks" are stored in their own table in the database specified by the
:ref:`settings-database-url`. To enable a specific psiturk server to run
tasks, set :ref:`settings-do-scheduler` to ``true``.

The "tasks" tab allows for scheduling an "Approve All workers" task which will be
run at a set interval. Will "approve" all submissions currently marked as
"Submitted" in the psiTurk database.

The tab will also display any currently running campaigns. To edit a campaign,
visit the "Campaigns" tab.

.. warning::
   The *managing* of tasks and the *running* of tasks is handled separately!

   This is because psiTurk uses `APScheduler <https://apscheduler.readthedocs.io/en/stable/>`_
   for tasks, which does not currently handle interprocess synchronization (see
   `this APScheduler FAQ <https://apscheduler.readthedocs.io/en/stable/faq.html#how-do-i-share-a-single-job-store-among-one-or-more-worker-processes>`__
   ).

   This means that any dashboard can view, create, delete, and update tasks,
   while a single separate psiTurk server instance can be set up with only one
   thread for task-running.

   **Note!**: if :ref:`settings-do-scheduler` is set to True, and :ref:`settings-threads` is greater
   than 1, psiTurk will refuse to start! This is a safeguard, because, again,
   APScheduler cannot handle interprocess task-running synchronization.




Configuration
~~~~~~~~~~~~~
* Set dashboard ``mode``.
* View AMT balance.
