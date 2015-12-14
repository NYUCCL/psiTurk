``hit`` command + subcommands
=============================

.. contents::

Description
-----------

The ``hit`` command is used to create, view, delete, and modify Human Intelligence Tasks ("HITs") on Amazon Mechanical Turk.

``hit create``
--------------

Usage
~~~~~~

::

   hit create [<numWorkers> <reward> < duration>]

Create a HIT with the specified number of assignments, reward amount, and
duration. Will be posted either live to AMT or to the Worker Sandbox depending
upon your current mode. ``hit create`` can also be run interactively by
entering the command without parameters.

The ``duration`` specifies how long a worker can "hold on" to your HIT (in hours or hours:minutes). This should be long enough for workers to actually
complete your HIT, but sometimes workers will "accept" a HIT which is
worth a lot of money but come back and do the work later in the
day. You can specify a shorter duration if you want workers to
complete your HIT immediately.

Example
~~~~~~~~

Creating a HIT in the sandbox with three assignments that pays $2.00 and has a
1.5 hour time limit::

   [psiTurk server:on mode:sdbx #HITs:0]$ hit create 3 2.00 1:30
   *****************************
     Creating sandbox HIT
       HITid:  2XE40SPW1INMXUF9OJUNDB6BT8W2F4
       Max workers: 3
       Reward: $2.00
       Duration: 1:30 hours
       Fee: $0.60
       ________________________
       Total: $6.60
     Ad for this HIT now hosted at: https://ad.psiturk.org/view/Q3HWnfqzg3MP9VDbu3kFyn?assignmentId=debugJCI80S&hitId=debug9AWC90
   [psiTurk server:on mode:sdbx #HITs:1]$


``hit extend``
--------------

Usage
~~~~~

::

  hit extend <HITid> [--assignments <number>] [--expiration <time>]

Extend an existing HIT by increasing the amount of time before the HIT expires
(and and is no longer available to workers) or by increasing the number of
workers who can complete the HIT.

Example
~~~~~~~
Adding both time and assignments to a HIT::

  psiTurk server:on mode:sdbx #HITs:1]$ hit list --active
  Stroop task
	Status: Assignable
	HITid: 2776AUC26DG6NRIGNVRFN0COYO0B4R
	max:3/pending:0/complete:0/remain:3
	Created:2014-03-07T21:36:33Z
	Expires:2014-03-08T21:36:33Z

  [psiTurk server:on mode:sdbx #HITs:1]$ hit extend 2776AUC26DG6NRIGNVRFN0COYO0B4R --assignments 10 --expiration 12
  HIT extended.
  [psiTurk server:on mode:sdbx #HITs:1]$ hit list --active
  Stroop task
	Status: Assignable
	HITid: 2776AUC26DG6NRIGNVRFN0COYO0B4R
	max:13/pending:0/complete:0/remain:13
	Created:2014-03-07T21:36:33Z
	Expires:2014-03-08T21:48:33Z

Note that both the remaining number of assignments and the expiration time of
the HIT have increased. One can also increase the number of assignments or the
expiration independently.

``hit expire``
--------------

Usage
~~~~~

::

  hit expire (--all | <HITid> ...)

Expire one or more existing HITs, or expire all HITs using the ``--all``
flag.

Example
~~~~~~~
1. Expiring two HITs at once::

     [psiTurk server:on mode:sdbx #HITs:4]$ hit expire 2Y0T3HVWAVKIMG42A2S75Z9943NNFG 2RVZXR24SMEZFG314ME9X8P9CPPH0X
     expiring sandbox HIT 2Y0T3HVWAVKIMG42A2S75Z9943NNFG
     expiring sandbox HIT 2RVZXR24SMEZFG314ME9X8P9CPPH0X
     [psiTurk server:on mode:sdbx #HITs:2]$

2. Expiring all active HITs::

     [psiTurk server:on mode:sdbx #HITs:2]$ hit expire --all
     expiring sandbox HIT 2776AUC26DG6NRIGNVRFN0COYO0B4R
     expiring sandbox HIT 2VUWA6X3YOCCVET8PKOPWINIWJFPO0
     [psiTurk server:on mode:sdbx #HITs:0]$

``hit dispose``
---------------

Usage
~~~~~

::

   hit dispose (--all | <HITid>)

Dispose of one ore more HITs, or dispose of all HITs using the ``--all`` flag.

.. note::
   To dispose of a HIT, it must not be active or have any unreviewed
   assignments

Example
~~~~~~~

::

   [psiTurk server:off mode:sdbx #HITs:0]$ hit dispose 241KM05BMJTUXCDL0TG9UA7SJI3JEQ
   deleting sandbox HIT 241KM05BMJTUXCDL0TG9UA7SJI3JEQ
   [psiTurk server:off mode:sdbx #HITs:0]$

``hit list``
------------

Usage
~~~~~

::

  hit list [--active | --reviewable]

List all HITs, or list all active or reviewable HITs using the provided flags.

Examples
~~~~~~~~

1. List all active HITs::

     [psiTurk server:on mode:sdbx #HITs:1]$ hit list --active
     Stroop task
        Status: Assignable
	HITid: 2ZFKO2L92HECCONGNYFCFF0C3R2FG1
	max:1/pending:0/complete:0/remain:1
	Created:2014-03-07T22:10:01Z
	Expires:2014-03-08T22:10:01Z

     [psiTurk server:on mode:sdbx #HITs:1]$

2. List all HITs::

     [psiTurk server:on mode:sdbx #HITs:1]$ hit list
     Face Discrimination (5 - 10 minutes, up to $1.0 bonus!!)
	Status: Reviewable
	HITid: 2ZRNZW6HEZ6OUI7FRTZ6CGUMGIQPZ0
	max:1/pending:0/complete:0/remain:0
	Created:2014-03-03T23:53:08Z
	Expires:2014-03-04T23:53:08Z

     Stroop task
	Status: Assignable
	HITid: 2ZFKO2L92HECCONGNYFCFF0C3R2FG1
	max:1/pending:0/complete:0/remain:1
	Created:2014-03-07T22:10:01Z
	Expires:2014-03-08T22:10:01Z

     [psiTurk server:on mode:sdbx #HITs:1]$
