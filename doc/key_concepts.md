# What is psiturk?

To begin with it can be helpful to lay out the problems `psiturk` 
does and does not solve to help you gauge whether it will be useful to you.

However, before getting started let's make sure we have some shared terminology.

## Web based experiments

Web based experiments present stimuli, videos, questionaires, and animations to people over the Internet using standard web browser technologies. Increasingly researchers use crowdwork websites to facilitate the recruitment to these tasks.  However, people use web based experiments for many types of designs even for in-person experiments, iPad/tablet based experiments in the field, fMRI designs, etc...
The critical issue is if you want to use the browser as your "task inferface."
`psiturk` can be used to help anytime you want to perform an experiment in a browser.

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
Amazon collects a 10% fee for each payment (which goes even higher when you post hits with many assignments).


## Where does psiturk come in?

The `psiturk` toolbox is designed to help you run fully-customized and dynamic web-experiments over the Internet. Specifically, it allows you to:

1. Run a web server for your experiment
2. Test and debug your experiment
3. Deploy your experiment to a secure, high availablity cloud server
4. Interact with sites like Amazon Mechanical Turk to recruit, post HITs, filter, and pay participants (AMT workers)
5. Manage databases and export data

`psiturk` also includes a powerful scripting interface for automating the types of tasks you typically perform when running a web-based experiment.  These scripts can also be used to avoid
around the extra fee Amazon charges for certain "large" HITs.

## Do I need to how to code to use psiturk?

Yes. `psiturk` experiments are run in web browsers. To develop a web browser
experiment, you need to have basic web programming skills with HTML, CSS, and
JavaScript.  You sometimes might also use Python to customize your experiment.

To get you started, `psiturk` provides a fully functioning example
experiment in the [Example project walkthrough](tutorials/example-project-stroop) section that
you can use as a template for your own study. `psiturk` also includes
a library of basic Javascript functions (see [psiturk.js API](api-overview)) that you can
insert into your code to handle page transitions, load images, and
record data.

However, for actually programming the interface of your task people often use other 
javascript tools like the outstanding [jsPsych](https://www.jspsych.org).

The good news is that many people have developed experiments using `psiturk` and you can use these examples to bootstrap your own efforts.


## Do I need to setup and manage a webserver?

No, because `psiturk` does this for you.

If you run an experiment on the web you need a way to send the content to the user.  This usually requires some type of http/https web server.  While you can do that from your personal computer (with some setup/configuration), currently the easiest way to do this is to deploy (i.e., run on a remote cloud server) your completed experiment to the web via the free-tier on Heroku.  When you are developing locally/testing your code `psiturk` provides you a small, simplified web server running on your computer that mimics the environment that is run when your experiment is officially "deployed."

**TL;DR**: Yes you need a websever.  `psiturk` provide a lightweight mini-webserver that you can use to develop your task locally on your desktop.  When you are ready to begin data collection you deploy to the cloud.  We have a smooth workflow for doing this for free on Heroku. 

## Do I need to setup and manage a database?

No, because `psiturk` does this for you (sound familiar?).  

Browsers do not allow you to write directly to the user's file system.  As a result data has to be stored someplace.  This often requires some type of **database**.  

There are [non-database solutions for some systems](https://www.jspsych.org/overview/mturk/) (e.g., Mechanical Turk) that store the data in a special field on the crowdworker site.  However, if you then want to use your experiment in the lab or with a different crowdworking platform you have to figure something new out.  Your IRB might have issues with saving subject data on Amazon's servers linked to the subject's Mechanical Turk account identity.  

`psiturk` helps you interface your experiment with a robust and secure database.  `psiturk` automatically handles anonymization of your subject's identity.  When you deploy a `psiturk` experiment it can create a free, robust Postgres database on Heroku that will be entirely deleted when you complete your experiment (after you download your anonymized files of course!).  

If you do have your own database though `psiturk` is happy to use it.

**TL;DR**: Yes you need a database, but there is no database software required for you to personally install or maintain.  `psiturk` will create free, managed databases for you.  

## My IRB is concerned about privacy.  Does psiturk store or view my subjects data?

No, all communication is directly between you and your participant.  There is no centralized data collection or monitoring.  `psiturk` data saving routines anonymize your databases so that no subject identity is associated with a datafile except with a special secret key that only you (the `psiturk` developer) know.  Everything is protected with passwords.

## Is psiturk only for use with Amazon Mechanical Turk?

No!  You can use psiturk anytime you need to deliver an experiment over the Internet.  Some researchers for instance have used `psiturk` to design iPad experiments that are run in person at schools or museums.  In these cases none of the Mechanical Turk specific features are needed.  `psiturk` original was designed (and named) based on its connection to Mechanical Turk but as time goes on it has become more general.  We still like the name and logo though.

That said, if you *do* recruit people from a crowdworking site it can be a hassle to figure out what their bonus payment was and to remember to properly compensate people.  `psiturk` provides a simple, scriptable API to interfacing with common payment tasks, especially with Amazon Mechanical Turk.  Non-`psiturk` solutions involve using the clumsy tools and web interfaces provided by the crowdlabor sites.  Ick!

