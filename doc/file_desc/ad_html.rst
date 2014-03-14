ad.html
===============

This is a very important file.  It contains the 
text of your HTML ad.  This is the first thing
participants taking your experiment will see.
This file exists locally.  When you are `debugging <../command_line/debug.html>`__
in local mode, the local file on your will be used.
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

For example, here is an example template that comes
with the default `stroop example <../stroop.html>`__.

::

	<!doctype html>

	<html>
		<head>
			<title>Psychology Experiment</title>
		</head>
		<body>
	
			{% if assignmentid != "ASSIGNMENT_ID_NOT_AVAILABLE" %}
				<h1>Thank you for accepting this HIT!</h1>
				<p>By clicking the following URL link, you will be taken to the experiment,
						including complete instructions and an informed consent agreement.</p>
				
				<script>
					function openwindow() {
						popup = window.open('{{ server_location }}/consent?hitId={{ hitid }}&assignmentId={{ assignmentid }}&workerId={{ workerid }}','Popup','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=no,width='+screen.availWidth+',height='+screen.availHeight+'');
						popup.onunload = function() { location.reload(true) }
					}
				</script>
				<p>
				Please disable pop-up blockers before continuing.
				</p>
				<p><a href="#" onClick="openwindow()">Ok, I understand, I'm read to start.</a></p>

			{% else %}
				<h1> Call for participants</h1>
				<p>The Cognition and Computation Lab at New York University (NYU)
				is looking for online participants for a brief experiment on how
				people learn. The only requirements are that you are at least 18
				years old and are a fluent English speaker.
				</p>
				<p>Example example, herp derp.
				</p>
		                <p>This task can only be completed once. If you have already
		                completed this task before the system will not allow you to run
		                again. If this looks familiar please release the hit so someone
		                else can participate.</p>

				Otherwise, please click the "Accept Hit" button on the Amazon site above to begin the task.
			{% endif %}
		</body>
	</html>


