Recording data
==============

To record data in your task you make calls to the `psiturk.js Javascript API <api.html>`__.
There are three kinds of data that **psiTurk** will help you produce:

1. `Trial-by-trial log file <recording.html#recording-trial-data>`__

2. `Unstructured (field, value) pairs <recording.html#recording-unstructured-data>`__

3. `Browser events <recording.html#browser-event-data>`__

Recording trial data
~~~~~~~~~~~~~~~~~~~~

The first dataset that will be produced by your experiment will be a
simple log file, which you add to a single line at a time. In order to
add a line of data to the log, use ``psiturk.recordTrialData``:

.. code:: javascript

    psiturk.recordTrialData(['this', 'is', 1, 'line'])

The list of values that you supply to ``recordTrialData`` will then be
appended to the log. It is up to you how to structure those lists; you
will have to parse them as part of your analysis.


Recording unstructured data
~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to trial by trial data, there is often a need to record
information about a participant in the form of (field, value) pairs, for
which you can use ``psiturk.recordUnstructuredData``:

.. code:: javascript

    psiturk.recordUnstructuredData('age', 24)
    psiturk.recordUnstructuredData('response', 'yes')

Like the trial-by-trial data, it is up to you to decide whether or not
to use this function. For some kinds of experiments (like simple
surveys), this might be the only function you need.

Saving the data
~~~~~~~~~~~~~~~

It's important to remember that ``psiturk.recordTrialData`` and
``psiturk.recordUnstructuredData`` only modify the ``psiturk`` object on
the client side. If you want to save the data that has been accumulated
to the server, you must call ``psiturk.saveData()``.

It's up to you how often ``psiturk.saveData()`` syncs the task data to
the server (e.g., after every block, or once at the end of the
experiment). Using ``saveData`` frequently will limit the loss of data
if the participant runs into an error, but keep in mind that it involves
a new request to the server each time it is called.

Browser event data
~~~~~~~~~~~~~~~~~~

The third dataset is generated automatically without any input from the
experiment, and is used to track special kinds of events that occur as a
worker is interacting with the page. Currently, this includes:

1. "resize" events: when the worker changes the size of their browser
   window (the first value recorded is the initial size of the window)

2. "focus" events: when the worker switches to and from a different
   browser window or application. If the worker leaves the experiment
   window, a "focus off" event is recorded; when they return a "focus
   on" event is recorded.

.. note::
   Information about how to retrieve recorded data sets can be found
   `here <./retrieving.html>`__.
