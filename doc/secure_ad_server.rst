**psiturk.org** Secure Ad Server
================================

Participants recruited via Mechanical Turk first interact with your task via **ads**.
Ads are simply the digital version of hanging a poster or flyer around your university
building in order to recruit participants.
Technically, **ads** are snippets of HTML code that describe what your task is about
and what you're offering for compensation.  As a result, they are the front line for any
subject recruitment online.  It's easy to overlook the importance of a good ad, and making
that ad visible to as many participants as possible.


.. seealso::

   `Getting setup with psiturk.org <psiturk_org_setup.html>`__
   	  Use of the Secure Ad Server requires an account on psiturk.org.


Ads, Amazon Mechanical Turk, and the External HIT type
------------------------------------------------------

Any task (or HIT) which you deploy on your own server is listed using the
"external HIT" type (a special name that Amazon uses for tasks which are hosted on
external webservers).  For these types of tasks, ads show up in users' browsers as a
HTML document.  Due to recent changes in browser security, if your HTML is not encrypted and signed using
an "official" SSL certificate (e.g., **https**://myschool.edu/myad.html works
and the certificate signing authority is official) then the ad won't display to potential
participants at all!

There's a good discussion of this issue `here <http://wiki.bcs.rochester.edu/HlpLab/MTurkExperiments>`__,
`here <http://stackoverflow.com/questions/19801682/why-does-the-mturk-sandbox-only-display-my-hits-in-internet-explorer>`__,
and on Amazon's own `website <https://www.mturk.com/mturk/help?helpPage=worker#when_mixed_mode>`__.


This is **crazy**!

What's worse is that many universities are not able to provide individuals with a signed SSL certificate.
If that is the case, you can't really use the external HIT mechanism without getting an account on some web hosting site.

However, the psiturk Secure Ad Server **solves this problem for all researchers**.

.. image:: https://psiturk.org/static/images/server_animation/server_animation_frame5.png
	:align: left


Rather than getting your own signed certificate (a technically challenging process), when you use
**psiTurk**, you can host your ad with us via `https://ad.psiturk.org <http://ad.psiturk.org/>`__
via a custom and unique URL made especially for you.
We have already gone through the steps of getting an official, signed SSL certificate so you don't
have to!  **psiTurk** posts your custom ad text with us, and then participants access your task
by first interacting with our secure server.  We show them the ad, then forward them to you.
No hassle, more potential participants!

A full "visual explanation" of the Secure Ad Server is provided `here <http://psiturk.org/ad_server>`__.
Basically, you post the HTML of you "ad" to the psiturk.org cloud.  Workers view the ad on the
cloud server and decide if they want to accpet.  If so they are forwarded to your local server or
computer to complete the task.


Why use the **psiturk.org** Secure Ad Server?
---------------------------------------------

As should be obvious, **psiTurk** already gets around a major technical hurdle for many scientists.
However, the **psiTurk** Secure Ad Server not only serves up your SSL-signed Ad, but also
provides you with some valuable data about people who view your HIT, people who accept it, and
what other task they have completed on the **psiTurk** meta-platform.
This can be very useful data.  For example, when you use the **psiTurk** Ad server you can find
out if your participants have done a version of your experiment before!

The public API for this data is coming soon, but just know that when you host your Amazon Mechanical
Turk ads with us you are helping to build a valuable resource about which participants have done
which types of experiments. This can be used to help filter your data or prevent certain participants
from doing experiments for which they have already possibly been exposed to the important manipulation.


Sound great, how do I use it?
-----------------------------

When you create a HIT from the command line in **psiTurk** your ad is posted to our servers.
We begin forwarding people to your website instantly.
You ad is never deleted (unless you want to delete it).
Soon, you will be able to access statistics about who view, accepted, and returned your HIT and what other tasks they have completed on **psiTurk**.  We also have plans to enable alternative ways of
posting Ads to **psiTurk** including through a simple web interface.  This would then
allow researchers using survey-type (via Google Forms or Qualtrics) to take
advantage of the features of the Secure Ad Server as well.
