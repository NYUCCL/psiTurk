``download_datafiles`` command
==============================

Usage
-----

::

   download_datafiles

The ``download_datafiles`` command accesses the current experiment
database table (defined in `config.txt
<../config/database_parameters.html>`__) and creates a copy of the
experiment data in a csv format.  ``download_datafiles`` creates three
files in your current folder:


`eventdata.csv`
~~~~~~~~~~~~~~~

`eventdata.csv` contains events such as window-resizing, and is
formatted as follows:

===============   ===========   ==========  ==========    =========
column 1          column 2      column 3    column 4      column 5
===============   ===========   ==========  ==========    =========
unique user ID    event type    interval    value         time
===============   ===========   ==========  ==========    =========


`questiondata.csv`
~~~~~~~~~~~~~~~~~~

`questiondata.csv` contains data recorded with
`psiturk.recordUnstructuredData()
<../api.html#psiturk-recordunstructureddata-field-value>`__, and is
formatted as follows:

===============   ==============   ==========
column 1          column 2         column 3
===============   ==============   ==========
unique user ID    question name    response
===============   ==============   ==========


`trialdata.csv`
~~~~~~~~~~~~~~~

`trialdata.csv` contains data recorded with `psiturk.recordTrialData()
<../api.html#psiturk-recordtrialdata-datalist>`__, and is formatted as follows:

===============   ===========   ==========  ===========
column 1          column 2      column 3    column 4
===============   ===========   ==========  ===========
unique user ID    trial #       time        trial data
===============   ===========   ==========  ===========

.. note::
   More information about how to record different types of data in an
   experiment can be found `<here <../recording.html>`__.
