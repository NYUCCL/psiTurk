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

	{% if assignmentid == "ASSIGNMENT_ID_NOT_AVAILABLE" %}

		HTML/CSS FOR AD BEFORE ACCEPTING

	{% else %}

		HTML/CSS FOR AD AFTER ACCEPTING
			
	{% endif %}

.. important::

	You cannot directly reference addition CSS or JS files
	in the ad since the ad server will host the ad
	using https://.  As a result you need to include all
	CSS styles you want applied to your ad directly in the
	file.  boostrap.min.css is provided for free by
	the ad server.

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
			<link rel=stylesheet href="/static/css/bootstrap.min.css" type="text/css">
			<style>
				/* these tyles need to be defined locally */
				body {
				    padding:0px;
				    margin: 0px;
				    background-color: white;
				    color: black;
				    font-weight: 300; 
				    font-size: 13pt;
				}

				/* ad.html  - the ad that people view first */
				#adlogo {
				    float: right;
				    width: 140px;
				    padding: 2px;
				    border: 1px solid #ccc;
				}

				#container-ad {
				    position: absolute;
				    top: 0px; /* Header Height */
				    bottom: 0px; /* Footer Height */
				    left: 0px;
				    right: 0px;
				    padding: 100px;
				    padding-top: 5%;
				    border: 18px solid #f3f3f3;
				    background: white;
				}
			</style>
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
									If assignmentid is "ASSIGNMENT_ID_NOT_AVAILABLE"
									it means the participant has NOT accepted your hit. 
									This should display the typical advertisement about
									your experiment: who can participate, what the
									payment is, the time, etc...

								-->
								{% if assignmentid == "ASSIGNMENT_ID_NOT_AVAILABLE" %}

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
								    

								{% else %}

									<!-- 
										OTHERWISE
										If assignmentid is NOT "ASSIGNMENT_ID_NOT_AVAILABLE"
										it means the participant has accepted your hit. 
										You should thus show them instructions to begin the 
										experiment ... usually a button to launch a new browser
										window pointed at your server.

										It is important you do not change the code for the
										openwindow() function below if you want you experiment
										to work.
									-->
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


								{% endif %}
								<!-- 
									endif
								-->
						</div>
				</div>
			</div>
		</body>
	</html>

