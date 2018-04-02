``worker`` command + subcommands
================================

.. contents::


Description
-----------

The ``worker`` command is used to list, approve and reject, and bonus worker
assignments on Amazon mechanical Turk.


``worker approve``
------------------


Usage
~~~~~

::

   worker approve (--hit <hit_id> | <assignment_id> ...)

Approve worker assignments for one or more assignment ID's, or use the
``--hit`` flag to approve all workers for a specific HIT.


Example
~~~~~~~

1. Approve a single assignment::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker approve 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     approved 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7

2. Approve all assignments for a given hit::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker approve --hit 2QKHECWA6X3Y4QTYKCG5NXPTWYGMLF
     approving workers for HIT 2QKHECWA6X3Y4QTYKCG5NXPTWYGMLF
     approved 2MB011K274J7PY7FQ1ZN76UXH0ECED
     approved 2UO4ZMAZHHRR1T7J8NEVUH1KJCAKBY


``worker reject``
-----------------


Usage
~~~~~

::

  worker reject (--hit <hit_id> | <assignment_id> ...)

Reject worker assignments for one or more assignment ID's, or use the ``--hit``
flag to reject all workers for a specific HIT.


Example
~~~~~~~

Reject a single assignment::

  [psiTurk server:on mode:sdbx #HITs:0]$ worker reject 2Y9OVR14IXKOIZQL1E3WD6X30CD98U
  rejected 2Y9OVR14IXKOIZQL1E3WD6X30CD98U


``worker unreject``
-------------------


Usage
~~~~~

::

     worker unreject (--hit <hit_id> | <assignment_id> ...)

Unreject worker assignments for one or more assignment ID's, or use the
``--hit`` flag to unreject all workers for a specific HIT.

.. note::
   Unrejecting an assignment automatically approves that assignment.


Example
~~~~~~~

Unreject a single assignment::

  [psiTurk server:on mode:sdbx #HITs:0]$ worker unreject 2Y9OVR14IXKOIZQL1E3WD6X30CD98U
  unrejected 2Y9OVR14IXKOIZQL1E3WD6X30CD98U


``worker bonus``
----------------


Usage
~~~~~

::

  worker bonus  (--amount <amount> | --auto) (--hit <hit_id> | <assignment_id> ...)

Grant bonuses to workers for one or more assignment ID's, or use the ``--hit``
flag to bonus all workers for a specific HIT.

Enter the bonus ``--amount <amount>`` in an X.XX format, or use the ``--auto``
flag to bonus each worker according to the 'bonus' field of hte database
(requires a `custom bonus route <../customizing.html>`__ in the experiment's
`custom.py` file).

Upon running ``worker bonus``, you will be asked to input a reason for the
bonus. This message will be displayed to workers who receive the bonus.

.. note::
   You must approve the worker assignment *before* you grant a bonus.

.. warning::
   While it isn't possible to approve an assignment more than once, it is
   possible to grant a bonus repeatedly. When running ``worker bonus`` with the
   ``--hit`` flag, only workers who have not yet received a bonus for the
   assignment will be bonused. However, when running ``worker bonus`` on
   individual assignments the worker will be bonused regardless of whether they
   have already received one.


Examples
~~~~~~~~

1. Bonusing an individual assignment. The bonus can be granted repeatedly,
   making this risky::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --amount 2.00 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     Type the reason for the bonus. Workers will see this message: Here's a bonus!
     gave bonus of $2.00 to 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --amount 2.00 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7
     Type the reason for the bonus. Workers will see this message: Here's another one!
     gave bonus of $2.00 to 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7

2. Say there are approved assignments for a HIT, one already bonused, one not yet
   bonused. Bonusing by HIT prevents repeated bonuses::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --amount 2.00 --hit 2ECYT3DHJHP4RRU304P8USX9BCXU1O
     Type the reason for the bonus. Workers will see this message: you haven't been bonused yet. Here's a bonus!
     bonusing workers for HIT 2ECYT3DHJHP4RRU304P8USX9BCXU1O
     gave a bonus of $2.00 to 2MB011K274J7PY7FQ1ZN76UXH0ECED
     bonus already awarded to 21A8IUB2YU98ZV9C5BUL3FBJB5B8K7

3. If a compute-bonus route exists in the experiment `custom.py`, we can also
   use the ``--auto`` flag to automatically give each worker the correct
   bonus::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker bonus --auto --hit 2ECYT3DHJHP4RRU304P8USX9BCXU1O
     Type the reason for the bonus. Workers will see this message: Thanks for moving science forward!
     bonusing workers for HIT 2ZQIUB2YU98JX6A4V3C0IBJ9W0HL9P
     gave a bonus of $3.00 to 27UQ45UUKQOYW1ZFLNJ8RG012VYDVP
     gave a bonus of $2.50 to 24IIHPCGJ2D2H2KFPX80MPPSKQM933

.. note::
   Unlike the commands to approve, reject, or unreject workers, the ``worker
   bonus`` command requires the psiturk shell to be launched in the same
   project as the HIT for which workers are being bonused, since the
   information about which workers have been bonused is stored in the
   experiment database.


``worker list``
----------------


Usage
~~~~~

::

   worker list [--submitted | --approved | --rejected] [--hit <hit_id>]

List all worker assignments, or list worker assignments fitting a
given condition using the provided flags. Use the ``--hit`` flag to
list workers for a specific HIT.


Examples
~~~~~~~~

1. Listing all submitted workers::

     [psiTurk server:on mode:sdbx #HITs:0]$ worker list --submitted
     [
         {
             "status": "Submitted",
             "assignmentId": "2VQHVI44OS2K18PW7EQSEAP5DPV5ZY",
             "workerId": "A2O6BB9HXEUXX1",
             "submit_time": "2014-03-04T16:14:32Z",
             "hitId": "2ZRNZW6HEZ6OUI7FRTZ6CGUMGIQPZ0",
             "accept_time": "2014-03-04T16:14:05Z"
         },
         {
             "status": "Submitted",
             "assignmentId": "2XB92NJKM05B2XAD1YN2JTP9TYXAFG",
             "workerId": "A2O6BB9HXEUXX1",
             "submit_time": "2014-03-03T23:35:17Z",
             "hitId": "2RWSCWY2AOO2W03X0OFGTSCMKZZ22I",
             "accept_time": "2014-03-03T23:34:19Z"
         }
     ]

2. Listing approved workers for a specific HIT::

    [psiTurk server:on mode:sdbx #HITs:0]$ worker list --approved  --hit 2ECYT3DHJHP4RRU304P8USX9BCXU1O
    listing workers for HIT 2ECYT3DHJHP4RRU304P8USX9BCXU1O
    [
        {
            "status": "Approved",
            "assignmentId": "21A8IUB2YU98ZV9C5BUL3FBJB5B8K7",
            "workerId": "A2O6BB9HXEUXX1",
            "submit_time": "2014-02-26T03:26:55Z",
            "hitId": "2ECYT3DHJHP4RRU304P8USX9BCXU1O",
            "accept_time": "2014-02-26T03:26:36Z"
        }
    ]
