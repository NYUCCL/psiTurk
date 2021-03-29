# Key Concepts

Read this if you want to find out more about Amazon Mechanical Turk
(AMT) and how psiturk can help you run web-based experiments on AMT
painlessly and quickly. This section will also tell you what problems
psiturk does and does not solve to help you gauge whether it will be
useful to you.


## What is Mechanical Turk?

Amazon Mechanical Turk (AMT) is an online platform that lets you post a
wide variety of tasks to a large pool of participants. Instead of
spending weeks to run experiments in the lab, it lets you collect data
of a large number of people within a couple of hours.

Some key terminology for understanding the AMT model:

-  **HIT (Human Intelligence Task)** - A unit of work (e.g. a psychology experiment)
-  **Requester** - The person or entity that posts HITs (e.g. a researcher or lab)
-  **Worker** - The person that completes HITs (i.e. a participant in your study)

Workers get paid a fixed amount for each HIT which is determined by the
requester. Requesters can also make bonus payments to specific workers.
Amazon collects a 10% fee for each payment.


## Why psiturk?

AMT provides some very basic templates that you can use to design HITs
(particularly questionnaires), but these will most likely not serve your
purposes as an experimenter. The psiturk toolbox is designed to help
you run fully-customized and dynamic web-experiments on AMT.
Specifically, it allows you to:

1. Run a web server for your experiment
2. Test your experiment
3. Interact with AMT to recruit, post HITs, filter, and pay participants
   (AMT workers)
4. Manage databases and export data

psiturk also includes a powerful interactive command interface that
lets you manage most of your AMT activity.


## Basic Requirement: A publicly-accessible server

Be aware that you will need to host your experiment on a server to which
your participants have access.  Currently the easiest way to do this is through the
free-tier on Heroku.  See the main docs for more information about this.


## Do I have to learn how to code?

Yes. psiturk experiments are run in web browsers. To develop a web browser
experiment, you need to have basic web programming skills with HTML, CSS, and
JavaScript.

To get you started, psiturk provides a fully functioning example
experiment in the [Example project walkthrough](tutorials/example-project-stroop) section that
you can use as a template for your own study. psiturk also includes
a library of basic Javascript functions (see [psiturk.js API](api-overview)) that you can
insert into your code to handle page transitions, load images, and
record data.

However, for actually programming the interface of your task people often use other 
javascript tools like the outstanding [jsPsych](https://www.jspsych.org).
