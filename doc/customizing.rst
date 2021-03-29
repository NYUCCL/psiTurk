.. _customizing-psiturk:

Server-side computations
===================

Sometimes you might like to add additional urls or "routes" to your project.
For instance you could make a password protected dashboard to visualize your
data as it comes in, add additional functionality to your psiturk experiment, or
add more complex server-side computations (e.g., fitting a computational model
to the subject in real time and using that to adapt the stimuli people view).

This can be achieved by using `Flask Blueprints <https://exploreflask.com/en/latest/blueprints.html>`__.
psiTurk will look for a file called ``custom.py`` in the project directory, and
import any blueprint from that module named ``custom_code``. See below for examples.

.. _customizing-compute-bonus:

Example: Automatically computing performance bonus
--------------------------------------------------

It is hard to use the main task to directly modify the database. However, you may use ``custom.py`` file with a function called ``compute_bonus`` to put the correct amount of bonus in the database. You could do this in Javascript perhaps but the problem is that participants can modify the javascript in their browser and increase their bonus. Instead it is better if bonuses are computed on the server side. The ``custom.py`` script may look like the following:

.. code-block:: python

  from flask import Blueprint, request, render_template, jsonify, abort, current_app
  # dealing with error
  from psiturk.experiment_errors import ExperimentError

  # Database setup
  from psiturk.db import db_session, init_db
  from psiturk.models import Participant
  # dealing with json like reading from database
  from json import dumps, loads

  # explore the Blueprint
  custom_code = Blueprint('custom_code', __name__, template_folder='templates', static_folder='static')

  #----------------------------------------------
  # example computing bonus
  #----------------------------------------------

  @custom_code.route('/compute_bonus', methods=['GET'])
  def compute_bonus():
      # check that user provided the correct keys
      # errors will not be that gracefull here if being
      # accessed by the Javascrip client
      if not 'uniqueId' in request.args:
          # i don't like returning HTML to JSON requests... maybe should change this
          raise ExperimentError('improper_inputs')
      uniqueId = request.args['uniqueId']

      try:
          # lookup user in database
          user = Participant.query.\
              filter(Participant.uniqueid == uniqueId).\
              one()
          user_data = loads(user.datastring)  # load datastring from JSON
          bonus = 0

          for record in user_data['data']:  # for line in data file
              trial = record['trialdata']
              if trial['phase'] == 'TEST':
                  if trial['hit'] == True:
                      bonus += 0.02
          user.bonus = bonus
          db_session.add(user)
          db_session.commit()
          resp = {"bonusComputed": "success"}
          return jsonify(**resp)
      except:
          abort(404)  # again, bad to display HTML, but...

Accordingly, in the main task file ``task.js``, you would call this function with the ``computeBonus`` function. Add a piece of the code at the end of your experiment:

.. code-block:: js

  psiTurk.computeBonus("compute_bonus", function () {
      psiTurk.completeHIT(); // when finished saving compute bonus, the quit
  });


Now let's walk through some key points of this process.

.. code-block:: python

  from flask import Blueprint, request, render_template, jsonify, abort, current_app

The key player in customizing is the `flask <https://palletsprojects.com/p/flask/>`_ package. It helps you run a webserver (HTTP server) .


.. code-block:: python

  custom_code = Blueprint('custom_code', __name__, template_folder='templates', static_folder='static')

Here we create a Blueprint object. Blueprint is an organizing tool. Here what's important for us is to specify the location template folder and static folder which may be used, for example, when you wanna display a HTML file.


.. code-block:: python

  @custom_code.route('/compute_bonus', methods=['GET'])

The first argument in ``route`` is the URL that when is called will run the
function right below it. For example, if you are running your task locally on
port 5000, then type in ``http://localhost:5000/compute_bonus``, which will call
the function ``compute_bonus`` defined right below. The `methods` argument is
defining the information flow communicating with this function -- it will "get"
information from outside.

BTW, in case you are wondering, the ``@`` in front of this line is called
"decorator". It uses the current line (in our case, the ``route`` function) to
"decorate" the function right below it. A helpful tutorial that further explains
this concept is `here <https://www.artima.com/weblogs/viewpost.jsp?thread=240808>`_.


.. code-block:: python

  def compute_bonus():
      if not 'uniqueId' in request.args:
          # i don't like returning HTML to JSON requests... maybe should change this
          raise ExperimentError('improper_inputs')
      uniqueId = request.args['uniqueId']

Here we use ``request`` to receive the information sent from javascript. In our case it's taken care by the ``computeBonus`` function. Looking into ``computeBonus`` to see where that "uniqueID" comes from:

.. code-block:: javascript

  self.computeBonus = function(url, callback) {
  $.ajax(url, {
                  type: "GET",
                  data: {uniqueId: self.taskdata.id},
                  success: callback
              });
  };

As mentioned before, the url is the route name; the data is a dictionary with
one key named "uniqueID", which is being looked for in the python
``compute_bonus`` function.

Now let's coming back to the ``compute_bonus`` function:

.. code-block:: python

  try:
        # lookup user in database
        user = Participant.query.\
            filter(Participant.uniqueid == uniqueId).\
            one()
        user_data = loads(user.datastring)  # load datastring from JSON

Now the database kicks in. We've created a `user` object which we will be able
to read all data about this user that has been saved in the database, as well as
write something.

.. code-block:: python

  bonus = 0
    for record in user_data['data']:  # for line in data file
        trial = record['trialdata']
        if trial['phase'] == 'TEST':
            if trial['hit'] == True:
                bonus += 0.02

Now we calculate bonus by checking how many trials are correct.

.. code-block:: python

  user.bonus = bonus
    db_session.add(user)
    db_session.commit()

We assign value for the "bonus" column of this user and commit to the database.
This will enable psiturk to give bonus.


.. code-block:: python

    resp = {"bonusComputed": "success"}
    return jsonify(**resp)

Finally, we give this call-back message to the original query source, which is
our ``psiTurk.computeBonus`` function. Trip is done, hurray!!


The basic logic of using ``custom.py``
--------------------------------------

When is ``custom.py?`` called?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is loaded as a module when the psiturk server starts (called by ``psiturk/experiment.py``). That is to say, you'd need to restart psiTurk whenever you've made some change of this script!


What is a route and why we need it?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A route is a URL served on the server. We need it because it is impossible for
javascript to run python script (or any local files) directly. But you don't
have to call from javascript -- equally, just access the address like
`http://localhost:5000/my_route` in your browser!

(Note if ``my_route`` is expecting to receive arguments, like the participant ID,
then the url becomes like `http://localhost:5000/my_route?id=12345`.)

Call the route from javascript directly without the psiturk function?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the example above, we used the built-in function of ``computeBonus`` to call
the custom route. Of course you can customize your own call for your favorite
route, especially specifying the data sent to it. The key helper is
`ajax <https://api.jquery.com/jQuery.ajax/>`_ which is a jquery API. Add a call
in your ``task.js`` that looks like this:

.. code-block:: javascript

  $.ajax("my_route",{
                type: "GET",
                data: {id: myid, data:mydata},
                success: function (response) {
                    console.log(response)
                }
            });

Note the ``type`` argument should be consistent with what your route function
wants (usually either "GET" or "POST"). The ``data`` argument is usually a
dictionary.


Tips about debugging your custom route
--------------------------------------

Debugging custom.py is tricky since the error message won't just appear in your
browser console. You will most likely see an "5000 internal error" which just
means there is bug when calling your route. You may, however, try the following:

* Find your error message at `server.log`, which is automatically generated in
  your current psiturk folder and will record the error messages. This is usually
  the most informative tool.
* Print messages within your python function, which will appear in the psiturk
  shell.
* If you are not sure the route is being called, return some error message that
  will show in your browser (go to your browser with
  `http://localhost:5000/my_route`)
