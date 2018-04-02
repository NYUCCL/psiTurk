HIT Configuration
=================

The HIT Configuration section contains details about
your Human Intelligence Task.  An example looks
like this:

::

    [HIT Configuration]
    title = Stroop task
    description = Judge the color of a series of words.
    amt_keywords = Perception, Psychology
    lifetime = 24
    us_only = true
    approve_requirement = 95
    number_hits_approved = 0
    require_master_workers = false
    contact_email_on_error = youremail@gmail.com
    ad_group = My research project
    psiturk_keywords = stroop
    organization_name = New Great University
    browser_exclude_rule = MSIE, mobile, tablet
    allow_repeats = false


`title` [string]
~~~~~~~~~~~~~~~~

The `title` is the title of the task that will appear on the AMT
worker site.  Workers often use these fields to
search for tasks.  Thus making them descriptive and
informative is helpful.


`description` [string]
~~~~~~~~~~~~~~~~~~~~~~

The `description` is the accompanying
text that appears on the AMT site. Workers often use these fields to
search for tasks.  Thus making them descriptive and
informative is helpful.


`keywords` [comma separated string]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`keywords` Workers often use these fields to
search for tasks.  Thus making them descriptive and
informative is helpful.


`lifetime` [integer]
~~~~~~~~~~~~~~~~~~~~

The `lifetime` is how long your HIT remains visible to workers (in
hours). After the lifetime of the HIT elapses, the HIT no longer
appears in HIT searches, even if not all of the assignments for the
HIT have been accepted.

This is in contrast to the HIT `duration`, which specifies how long
workers have to complete your task, and which you provide at HIT
creation time. See the documentation on `hit create <../command_line/hit.html#hit-create>`__ for more details.


`us_only` [true | false]
~~~~~~~~~~~~~~~~~~~~~~~~

`us_only` controls
if you want this HIT only to be available to US Workers.  This is
not a failsafe restriction but works fairly well in practice.


`approve_requirement` [integer]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`approve_requirement` sets a qualification for what type of workers
you want to allow to perform your task.  It is expressed as a
percentage of past HITs from a worker which were approved.  Thus
95 means 95% of past tasks were successfully approved.  You may want
to be careful with this as it tends to select more seasoned and
expert workers.  This is desirable to avoid bots and scammers, but also
may exclude new sign-ups to the system.


`number_hits_approved` [integer]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`number_hits_approved` is important to use in conjunction with `approved_requirement`, because
mturk will default `approve_requirement` to 100% until a worker has at least 100 HITs approved.
Override that behavior by setting `number_hits_approved` to something like 100.


`require_master_workers` [true | false]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`require_master_workers` will make it so that only workers with the "Master" qualification
can take your study. See `Who Are Amazon Mechanical Turk Masters? <https://requester.mturk.com/help/faq#what_are_masters>`__

Note: Master workers cost an extra 5%.

.. seealso::

   The following options help configure the psiturk.org Secure Ad Server.

   `Getting setup with psiturk.org <../psiturk_org_setup.html>`__
   	  How to get an account on psiturk.org.

   `psiturk.org Secure Ad Server <../secure_ad_server.html>`__
   	  An overview of the purpose and features of the Secure Ad Server.


`contact_email_on_error` [string - valid email address]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`contact_email_on_error`  is the email you would like to display to
workers in case there is an error in the task.  Workers will often try
to contact you to explain what when want and request partial or full
payment for their time.  Providing a email address that you monitor
regularly is important to being a good member of the AMT community.


`ad_group` [string]
~~~~~~~~~~~~~~~~~~~

`ad_group`  is a unique string that describes your experiment.
All HITs and Ads with the same ad_group string will be grouped together
in your psiturk.org dashboard.  To create a new group in your dashboard
simply create a new unique string.  The best practice is to group all
experiments from the same "project" with the same `ad_group` but assign
different `ad_group` identifiers to different project (e.g., if two
students in a lab were working on different things but shared a psiturk.org
account then they might use different `ad_group` identifiers to keep
things organized.)


`psiturk_keywords` [comma separated string]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`psiturk_keywords` [string, comma separated] are a list of key words
that describe your task.  The purpose of these keywords (distinct from
the `keywords` described above) is to help other researchers know
what your task involves.  For example, you might include the keyword
`deception` if your experiment involves deception.  If it involves a
common behavioral task like "trolly problems" you might include that
as well.  In the future we hope to allow researchers to query information
about particular workers and task to find out if your participants
are naive to particular types of manipulations.  You should be careful
not to include too general of terms here.  For example, a researcher
might want to exclude people who in the past had participated in a
psychology study involving deception.  They probably don't care to
exclude people who did a "decision making task".  Thus, being specific
and using important keywords that are likely to be recognized by the
research community is the best approach.   (Ask yourself, if I wanted
to exclude people who had done this study from a future study what
keywords would I search for.)


`organization_name` [string]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`organization_name` [string] is just an identifier of your academic
institution, business, or organization.  It is used internally
by psiturk.org.


`browser_exclude_rule` [comma separated string]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`browser_exclude_rule` is a set of rules you can apply to exclude
particular web browsers from performing your task.  When a users
contact the `Secure Ad Server <../secure_ad_server.html>`__ the server checks
to see if the User Agent reported by the browser matches any of the
terms in this string.  It if does the worker is shown a message
indicating that their browser is incompatible with the task.

Matching works as follows.  First the string is broken up
by the commas into sub-string.  Then a string matching rule is
applied such that it counts as a match anytime a sub-string
exactly matches in the UserAgent string.  For example, a user
agent string for Internet Explorer 10.0 on Mac OS X might looks like this:

::

  Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)

This browser could be excluded by including this full line (see `this website <http://www.useragentstring.com/pages/Browserlist/>`__ for a partial list of UserAgent strings).  Also
"MSIE" would match this string or "Mozilla/5.0" or "Mac OS X" or "Trident".
Thus you should be careful in applying these rules.

There are also a few special terms that apply to a cross section of browsers.
`mobile` will attempt to deny any browser for a mobile device (including
cell phone or tablet).  This matching is not perfect but can be more general
since it would exclude mobile version of Chrome and Safari for instance.
`tablet` denys tablet based computers (but not phones).  `touchcapable` would
try to exclude computers or browser with gesture or touch capabilities
(if this would be a problem for your experiment interface).  `pc` denies
standard computers (sort of the opposite to the `mobile` and `tablet` exclusions).
Finally `bot` tries to exclude web spiders and non-browser agents like
the Unix curl command.


`allow_repeats` [boolean]
~~~~~~~~~~~~~~~~~~~~~~~~~

`allow_repeats` specifies whether participants may complete the experiment more
than once. If it is set to `false` (the default), then participants will be
blocked from completing the experiment more than once. If it is set to `true`,
then participants will be able to complete the experiment any number of times.

Note that this option does not affect the behavior when a participant starts
the experiment but the quits or refreshes the page. In those cases, they will
still be locked out, regardless of the setting of `allow_repeats`.
