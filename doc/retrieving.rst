Retrieving Datasets
===================

There are several ways to retrieve experiment data from the database:

Retrieving using ``download_datafiles``
-----------------------------------------

The simplest way to retrieve data is using the `download_datafiles
command <./command_line/download_datafiles.html>`__. This creates
three csv files containing the three kinds of data: `trial data
<./recording.html#recording-trial-data>`__, `question data
<./recording.html#recording-unstructured-data>`__, and `event data <./recording.html#browser-event-data>`__.

Retrieving programmatically
----------------------------

While the ``download_datafiles`` shell command is the simplest way to retrieve
experiment data, a more powerful and flexible solution is to retrieve the data
programmatically. Many languages offer libraries for interfacing with mysql and
sqlite databases - below is an example using python and the sqlalchemy package
to retrieve data from a mysql database. By including code such as this at the
beginning of your analysis script, you can be sure the the data you're analyzing is
always complete and up-to-date.

.. code-block:: python

   from sqlalchemy import create_engine, MetaData, Table
   import json
   import pandas as pd

   db_url = "mysql://username:password@host.org/database_name"
   table_name = 'my_experiment_table'
   data_column_name = 'datastring'
   # boilerplace sqlalchemy setup
   engine = create_engine(db_url)
   metadata = MetaData()
   metadata.bind = engine
   table = Table(table_name, metadata, autoload=True)
   # make a query and loop through
   s = table.select()
   rows = s.execute()

   data = []
   #status codes of subjects who completed experiment
   statuses = [3,4,5,7]
   # if you have workers you wish to exclude, add them here
   exclude = []
   for row in rows:
       # only use subjects who completed experiment and aren't excluded
       if row['status'] in statuses and row['uniqueid'] not in exclude:
           data.append(row[data_column_name])

   # Now we have all participant datastrings in a list.
   # Let's make it a bit easier to work with:

   # parse each participant's datastring as json object
   # and take the 'data' sub-object
   data = [json.loads(part)['data'] for part in data]

   # insert uniqueid field into trialdata in case it wasn't added
   # in experiment:
   for part in data:
       for record in part:
           record['trialdata']['uniqueid'] = record['uniqueid']

   # flatten nested list so we just have a list of the trialdata recorded
   # each time psiturk.recordTrialData(trialdata) was called.
   data = [record['trialdata'] for part in data for record in part]

   # Put all subjects' trial data into a dataframe object from the
   # 'pandas' python library: one option among many for analysis
   data_frame = pd.DataFrame(data)

How the datastring is structured
---------------------------------
The main data from an experiment participant is held in a
string of text in the `datastring` field of the data table. Understanding how this string
is structured is important to be able to parse the string into a useful format
for your analyses.

The `datastring` is structured as a `json object <http://w3schools.com/json/>`__. In the description that
follows, sub-objects are indicated by names wrapped in angle brackets (< >).

Top Level
~~~~~~~~~~

The top level of the datastring contains summary information about the worker,
as well as the datastring sub-objects:

.. code-block:: javascript

   {"condition": condition,
    "counterbalance": counterbalance,
    "assignmentId": assignmentId,
    "workerId": workerId,
    "hitId": hitId,
    "currenttrial": trial_number_when_data_was_saved,
    "useragent": useragent,
    "data": <data>,
    "questiondata": <questiondata>,
    "eventdata": <eventdata>}

data
~~~~~

The data sub-object contains a list of the data recorded each time
`psiturk.recordTrialData() <./api.html#psiturk-recordtrialdata-datalist>`__ is
called in the experiment:

.. code-block:: javascript

  [{"uniqueid": uniqueid,
    "current_trial": current_trial_based_on_#_of_calls_to_recordTrialData,
    "dataTime": current_time_in_system_time,
    "trialdata": <datalist>},
    ...
   ]

Here, ``<datalist>`` is whatever is passed to ``psiturk.recordTrialData()`` in the
experiment. This could be in any format, such as a string or list, but we
recommend saving data in a json format so that all data is stored in a clear,
easy-to-parse "field-value" format.

questiondata
~~~~~~~~~~~~~

The questiondata sub-object contains all items recorded using
`psiturk.recordUnstructuredlData()
<./api.html#psiturk-recordunstructureddata-field-value>`__.

.. code-block:: javascript

   {"field1": value1,
    "field2": value2,
    ...
   }

eventdata
~~~~~~~~~~

The eventdata sub-object contains a list of events (such as window resizing)
that occurred during the experiments:

.. code-block:: javascript

   [{"eventtype": eventtype,
     "value": value,
     "timestamp": current_time_in_system_time,
     "interval": interval},
     ...
    ]
