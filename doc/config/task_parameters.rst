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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Often you might run a couple different versions
of an experiment during a research project (e.g.,
Experiment 1 and 2 of a paper).
`experiment_code_version` is a string which is written into
the database along with your data helping you remember which
version of the code each participant was given.

This variable is used by the server along with `num_conds` and `num_counters` to ensure an equal number of workers per condition for the current `experiment_code_version`. In other words, changing the experiment_code_version resets the number of workers per condition to [0 0].


`num_conds`  [ integer ]
~~~~~~~~~~~~~~~~~~~~~~~~

**psiTurk** includes a primitive system for counterbalancing
participants to conditions.  If you specify a number of
condition greater than 1, then **psiTurk** will attempt to
assign new participants to conditions to keep them all
with equal N.  It also takes into account the time delay
between a person being assigned to a condition and completing
a condition (or possibly withdrawing).  Thus, you can be
fairly assured that after running 100 subjects in two conditions
each condition will have 50+/- completed participants.

.. note::

    If you want to reset the random assignment when changing `num_conds`, update the `experiment_code_version`.


`num_counters`  [ integer ]
~~~~~~~~~~~~~~~~~~~~~~~~~~~

`num_counters` is identical to `num_cond` but provides
an additional counterbalancing factor beyond condition.
If `num_counters` is greater than 1 then **psiTurk**
behaves as if there are `num_cond*num_counters` conditions
and assigns subjects randomly to the the expanded design.
See `Issue #53 <https://github.com/NYUCCL/psiTurk/issues/53>`__
for more info.
