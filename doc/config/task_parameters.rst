Task Parameters
===============

The Task Parameters section contains details about
your task.  An example looks like this:

::

	[Task Parameters]
	experiment_code_version = 1.0
	num_conds = 1
	num_counters = 1

`experiment_code_version`  [ string ]
-----------------------------------
Often you might run a couple different versions
of an experiment during a research project (e.g.,
Experiment 1 and 2 of a papper).  
`experiment_code_version` is a string which is written into
the database along with your data helping you remember which
version of the code each participant was given. 
This variable determines which participants in the database are used for counterbalancing, so if there are 2 conditions, the server ensure an equal number of workers per condition, so long as all the workers were run with the same code version. In other words, changing the experiment_code_version resets the number of workers per condition to [0 0].  


`num_conds`  [ integer ]
---------------------
**psiTurk** includes a primitive system for counterbalancing
participants to conditions.  If you specify a number of
condition greater than 1, then **psiTurk** will attempt to
assign new participants to conditions to keep them all
with equal N.  It also takes into account the time delay
between a person being assigned to a condition and completing
a condition (or possibly withdrawing).  Thus, you can be
fairly assured that after running 100 subjects in two conditions
each condition will have 50+/- completed participants. 
Note: It is very important to change the experiment_code_version when changing the num_conds variable in config.txt, because PsiTurk will consider all the workers run *with the same code version* when deciding which condition to assign a new worker. In other words, if num_conds changes from 4 to 2 without changing experiment_code_version, PsiTurk will still assign 4 conditions instead of 2 because there will be 4 conditions present in participants.db that were run with the same code version.

`num_counters`  [ integer ]
-------------------------
`num_counters` is identical to `num_cond` but provides
an additional counterbalancing factor beyond condition.
If `num_counters` is greater than 1 then **psiTurk**
behaves as if there are `num_cond*num_counters` conditions
and assigns subjects randomly to the the expanded design.
See `Issue #53 <https://github.com/NYUCCL/psiTurk/issues/53>`__
for more info.
