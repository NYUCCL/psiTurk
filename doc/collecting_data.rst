.. _collecting-data:

Collecting data
==========

Once you have your task completely developed (see :ref:`quickstart`) then you 
may be ready to collect data.  There are several ways you might recruit subjects 
including studies :ref:`conducted in the lab <tutorials/alternative-recruitment-channels>` but in this section 
we focus on the common use case of recruiting on Amazon Mechanical Turk.

.. contents:: Overview
  :local:


Step 1: Enter credentials
-------------------------

In order to get access to the Amazon Mechanical Turk features of psiturk, you
need obtain and enter credentials for accessing Amazon Web Services. These 
can be added to ``~/.psiturkconfig``. You can leave the ``aws_region`` at
the default value.

::

  ➜ cat ~/.psiturkconfig

  [AWS Access]
  AWS_ACCESS_KEY_ID = YourAccessKeyId
  AWS_SECRET_ACCESS_KEY = YourSecretAccessKey
  aws_region = us-east-1

.. seealso:: :ref:`amt-setup`

Step 2: Create a sandboxed HIT/Ad
---------------------------------

In order to make the experiment available to workers on Amazon Mechanical Turk you need to:

1. Run your psiturk server on a machine that is publicly-accessible.
2. Post a HIT on AMT, which will point MTurkers to your psiturk server address.

Use the :ref:`ad_url <hit_configuration_ad_url>` settings to point to the location of your publicy-accessible experiment.

See the :ref:`deploy-on-heroku` guide for an example of running your experiment on the
webserver of a platform-as-a-service cloud provider.

The example below uses the Amazon Mechanical Turk "sandbox," which is a place
for testing your task without actually offering it live to real paid workers.

Run the following to post a HIT, and answer all prompts::

::

  ➜ [psiTurk server:on mode:sdbx #HITs:0]$ hit create


Your HIT should now be visible on http://workersandbox.mturk.com if you search for
your requester account name or the HIT title word "Stroop" (set in config.txt).

.. warning::

    **Important!** Test to make sure that your Ad URL can be accessed from a
    place external to the network from which you created the HIT. If it cannot
    be accessed, then MTurkers won't be able to access your HIT!


Step 3: Check your data
-----------------------

By default psiTurk saves your data to a SQLite database participants.db in your
base project folder. You can check that everything is being recorded properly by
opening that file in a SQLite tool like Base.

.. seealso:: :ref:`databases-overview`


Step 4: Monitor progress
------------------------

One simple way to monitor how many people have actually accepted your HIT is with
the ``hit list --active`` or ``hit list --reviewable`` commands.

This shows the HITid for each task, how many have completed, and how many are pending.

.. seealso::
  See these FAQs:

  * :ref:`interpret-hit-status`
  * :ref:`why-no-hits-available`


Step 5: Approve workers
------------------------
psiTurk provides many tools for approving workers, assigning bonuses, etc.
Try ``help hit`` and ``help worker``.

One simple approach is to approve all the workers associated with a particular
HIT (once all the assignments are complete). To do this, use the
``worker approve --hit <HITID>`` command.

::

  ➜ [psiTurk server:on mode:sdbx #HITs:0]$ worker approve --hit 28K4SME3ZZ2MZI004SETTTXTTAG44LT

  Approving....

Step 6: Switch to "live" mode
------------------------------

In order to create public hits on the "live" AMT site, you need to switch modes
in the command shell using the mode command. To get back to the sandbox, just
type mode again.

To avoid mistakes, psiTurk defaults to sandbox mode (this behavior can be
changed in config.txt)

From here, everything is exactly the same as described for sandbox hits above.

::

  ➜ [psiTurk server:on mode:sdbx #HITs:1]$ mode

  Entered live mode
  [psiTurk server:on mode:live #HITs:0]$
