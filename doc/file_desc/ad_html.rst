ad.html
===============

This is a very important file.  It contains the 
text of your HTML ad.  This is the first thing
participants taking your experiment will see.
This file exists locally.  When you are `debugging <../command_line/debug.html>`__
in local mode, the local file will be used.
When you create an ad on the `Ad Server <../secure_ad_server.html>`__, a copy
of this file is uploaded to the **psiTurk** cloud 
server.


.. seealso::

   `psiturk.org Secure Ad Server <../secure_ad_server.html>`__
   	  You ad.html file is uploaded and stored on the
   	  Secure Ad Server when you create a hit.  

   `Command line tool for creating HITs <../command_line/hit.html>`__
   	  Info on how to create a HIT using the command line.

   	  

The structure of this file is very particular.
There are two ways your ad will be viewed.  
First, when a potential participants is simply browsing
the website, the will see one version of the ad.  
When the "Accept" the ad, the will see a second version
that may include addition information (such as
providing the link to launch your actual experiment).

These two types of adds are contained in the same file.
Which one is displayed is set by the `Jinja template <http://jinja.pocoo.org/docs/>`
The basic structure is:

::

	{% if assignmentid != "ASSIGNMENT_ID_NOT_AVAILABLE" %}

		HTML/CSS FOR AD AFTER ACCEPTING

	{% else %}

		HTML/CSS FOR AD BEFORE ACCEPTING
			
	{% endif %}

.. important::

	If you want to access your own style sheets you ad
	needs to reference them like this: href="{{ server_location }}/static/css/bootstrap.min.css"


For example, here is an example template that comes
with the default `stroop example <../stroop.html>`__.

::


	<!doctype html>
	<!-- 
		The ad.html has a very specific format.

		Really there are two "ads" contained within this file.

		The first ad displays to participants who are browsing
		the Amazon Mechanical Turk site but have not yet accepted
		your hit.  

		The second part of the ad display after the person selected
		"Accept HIT" on the Amazon website.  This will reload the
		ad and will display a button which, when clicked, will pop
		open a new browser window pointed at your local psiTurk
		server (assuming it is running and accessible to the Internet).

		See comments throughout for hints

	-->
	<html>
		<head>
			<title>Psychology Experiment</title>
			<link rel=stylesheet href="{{ server_location }}/static/css/bootstrap.min.css" type="text/css">
			<link rel=stylesheet href="{{ server_location }}/static/css/style.css" type="text/css">
		</head>
		<body>
			<div id="container-ad">

				<div id="ad">
					<div class="row">
						<div class="col-xs-2">
							<!-- REPLACE THE LOGO HERE WITH YOUR  UNIVERSITY, LAB, or COMPANY -->
							<img id="adlogo" src="{{ server_location }}/static/images/university.png" alt="Lab Logo" />
						</div>
						<div class="col-xs-10">

								<!-- 
									If assignmentid is not "ASSIGNMENT_ID_NOT_AVAILABLE"
									it means the participant has accepted your hit. 
									You should thus show them instructions to begin the 
									experiment ... usually a button to launch a new browser
									window pointed at your server.

									It is important you do not change the code for the
									openwindow() function below if you want you experiment
									to work.
								-->
								{% if assignmentid != "ASSIGNMENT_ID_NOT_AVAILABLE" %}

								    <h1>Thank you for accepting this HIT!</h1>
								    <p>
								    	By clicking the following URL link, you will be taken to the experiment,
								        including complete instructions and an informed consent agreement.
								    </p>
								    <script>
										function openwindow() {
								    		popup = window.open('{{ server_location }}/consent?hitId={{ hitid }}&assignmentId={{ assignmentid }}&workerId={{ workerid }}','Popup','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=no,width='+1024+',height='+768+'');
								    		popup.onunload = function() { location.reload(true) }
								  		}
								    </script>
								    <div class="alert alert-warning">
								    	<b>Warning</b>: Please disable pop-up blockers before continuing.
								    </div>
								    
							    	<button type="button" class="btn btn-primary btn-lg" onClick="openwindow();">
									  Begin Experiment
									</button>
								    

								{% else %}

								<!-- 
									OTHERWISE
									If assignmentid is "ASSIGNMENT_ID_NOT_AVAILABLE"
									it means the participant has NOT accepted your hit. 
									This should display the typical advertisement about
									your experiment: who can participate, what the
									payment is, the time, etc...
								-->

								    <h1>Call for participants</h1>
								    <p>
										The XXX Lab at XXXXX University is looking for online participants 
										for a brief psychology experiment. The only requirements 
										are that you are at least 18 years old and are a fluent English 
										speaker.  The task will that XXXXX minutes and will pay XXXXX.
								    </p>
								    <div class="alert alert-danger">
										<strong>This task can only be completed once.</strong> 
										If you have already completed this task before the system will not 
										allow you to run again. If this looks familiar please return the 
										HIT so someone else can participate.
								    </div>
								    <p>
									    Otherwise, please click the "Accept HIT" button on the Amazon site 
									    above to begin the task.
									</p>

								{% endif %}
								<!-- 
									endif
								-->
						</div>
				</div>
			</div>
		</body>
	</html>


