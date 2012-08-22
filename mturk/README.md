Interacting with the Mechanical Turk API
========================================

These python scripts allow you to interact with the Mechanical Turk API. They
require [boto][boto], a python package for interacting with [Amazon Web Services][aws].

checkBalance.py
--------------

Checks your mturk balance.

createHIT.py
------------

Creates an external-question HIT based on your specifications. Modify the script to suite it to your needs.

assessHITsApp.py
------------

Tools for seeing the status of your existing HITs and crediting outstanding assignments.

getAllAssignments.py
------------

Script for use in Python interactive sessions to retrieve information about HITs and assignments in Amazon's database.

Acknowledgment
--------------

These scripts were based on the advice provided by Mauro Rocco on [his blog][Mauro Rocco].


[boto]: http://code.google.com/p/boto/ "Boto's Google Code page."
[aws]: http://aws.amazon.com/ "Amazon Web Services."
[Mauro Rocco]: http://www.toforge.com/tag/mturk/  "Rocco's posts tagged with mturk."

