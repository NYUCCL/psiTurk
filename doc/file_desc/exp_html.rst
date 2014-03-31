exp.html
===============

This is the main "experiment".  It is where the experiment
"begins" for the subject.

**Important** this file MUST include the following code
snippet

::

	<script src="static/lib/jquery-min.js" type="text/javascript"> </script>
	<script src="static/lib/underscore-min.js" type="text/javascript"> </script>
	<script src="static/lib/backbone-min.js" type="text/javascript"> </script>
	<script src="static/lib/d3.v3.min.js" type="text/javascript"> </script>
	
	<script type="text/javascript">
	// Subject info, including condition and counterbalance codes.
	var uniqueId = "{{ uniqueId }}";
	var condition = "{{ condition }}";
	var counterbalance = "{{ counterbalance }}";
	var adServerLoc = "{{ adServerLoc }}"
	</script>
			
	<script src="static/js/psiturk.js" type="text/javascript"> </script>

In the header of the file.  This sets up the necessary variables for
communication with the **psiTurk** experiment server.

The last function that should be called in this file is
`psiturk.completeHIT() <../api.html#psiturk-completehit>`__
which will finalize the task.

Here is a default example experiment::

	<!doctype html>
	<!-- 
	  The exp.html is the main form that
	  controls the experiment.

	  see comments throughout for advice
	-->
	<html>
	    <head>
	        <title>Psychology Experiment</title>
	        <meta charset="utf-8">
	        <link rel="Favicon" href="static/favicon.ico" />

	        <!-- libraries used in your experiment 
				psiturk specifically depends on underscore.js, backbone.js and jquery
	    	-->
			<script src="static/lib/jquery-min.js" type="text/javascript"> </script>
			<script src="static/lib/underscore-min.js" type="text/javascript"> </script>
			<script src="static/lib/backbone-min.js" type="text/javascript"> </script>
			<script src="static/lib/d3.v3.min.js" type="text/javascript"> </script>

			<script type="text/javascript">
				// These fields provided by the psiTurk Server
				var uniqueId = "{{ uniqueId }}";  // a unique string identifying the worker/task
				var condition = "{{ condition }}"; // the condition number
				var counterbalance = "{{ counterbalance }}"; // a number indexing counterbalancing conditions
				var adServerLoc = "{{ adServerLoc }}"; // the location of your ad (so you can send user back at end of experiment)
			</script>
					
			<!-- utils.js and psiturk.js provide the basic psiturk functionality -->
			<script src="static/js/utils.js" type="text/javascript"> </script>
			<script src="static/js/psiturk.js" type="text/javascript"> </script>

			<!-- task.js is where you experiment code actually lives 
				for most purposes this is where you want to focus debugging, development, etc...
			-->
			<script src="static/js/task.js" type="text/javascript"> </script>

	        <link rel=stylesheet href="static/css/bootstrap.min.css" type="text/css">
	        <link rel=stylesheet href="static/css/style.css" type="text/css">
	    </head>
	    <body>
		    <noscript>
				<h1>Warning: Javascript seems to be disabled</h1>
				<p>This website requires that Javascript be enabled on your browser.</p>
				<p>Instructions for enabling Javascript in your browser can be found 
				<a href="http://support.google.com/bin/answer.py?hl=en&answer=23852">here</a><p>
			</noscript>
	    </body>
	</html>


