.. _migrating:

Migrating from psiTurk 2.0 to 3.0
=================================

Announcing psiTurk 3.0
~~~~~~~~~~~~~~~~~~~~~~

*A message from project founder Todd Gureckis.*

psiTurk 2.0 launched on April 28, 2014 and there has been (according to github) 786
commits since then to the project from a wide variety of contributors.  The evolution and
longevity of the project really has exceeded anything the original authors thought
would be possible.  In the seven years since 2.0 was first tagged so many things have changed
about web experimentation, web application development, the Amazon turk API, and even the 
Python ecosystem.

One part of psiTurk that has always been both a blessing and a curse is the reliance on 
several services provided by xxx.psiturk.org.  This includes the "Ad server" and several other 
api elements that were envisioned to distribute timely information to users of the system.
Generally this seemed like a good engineering solution to a problem, but centralization is generally
bad because if something happened to psiturk.org (annual SSL certs renew on time) then the system
goes down for everyone.  Every year during conference deadlines the original project creator
would lose sleep.

As a result, a major change in psiTurk 3.0 is to make the system decoupled from the services on
psiturk.org.  It is possible now to easily get a SSL signed connection to a cloud-based server (e.g., 
heroku) and to run the server in a "headless" mode. This gets around the need for the psiturk.org
"Ad server" which was written in 2014 and has basically never been updated since.  In a way this 
means psiTurk acts more like a traditional Flask "web application" rather than an interactive
command line tool, although the command line interface remains for interacting with Amazon and 
for development.

In addition to the hard decoupling work (led really by Dave Eargle), version 3.0 offers several new features
including a "campaign mode" which allows you to run a certain number of subject (say 100) by repeatedly
posting lower cost 9 assignment HITs, and a dashboard for managing hits.  In addition, a major change 
since 2.0 is support for Python 3.0 and the changes that entailed to work with more recent
versions of boto Mturk python api.

There may be some growing pains as people adjust to the new workflow so a goal is to update the
documentation to reflect the new changes as soon as possible.  As always, assitance from the psiturk
community to make this documentation is always appreciated!


Migration technical considerations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Below are some notable technical differences between psiTurk 2 and psiTurk 3.

No More Secure Ad Server
------------------------

Psiturk 3 drops all psiturk.org-hosted services, including most notably the Secure Ad Server.
MTurk still requires that ads be hosted over https, but in the years since the secure ad server was launched,
it has become easier to obtain an SSL certificate. psiTurk supports hosting ads
on `Heroku <https://www.heroku.com/>`_. Hosting an experiment on heroku provides free SSL.
See :ref:`deploy-on-heroku` for more information.

If your lab has a static IP address and somewhat technical prowess, you might also choose to obtain your
own certificate for free by first buying a domain name and then using `letsencrypt <https://letsencrypt.org/>`_.

Because the secure ad server has gone away, you will need to specify your ``ad_url``
in your config file. This setting is passed to mturk when you run ``hit_create``.
See the :ref:`hit_configuration_ad_url` section of the documentation.

More flexible configuration approach
------------------------------------

psiTurk 3 also is more flexible in how it handles configuration variables, respecting
environment variables over psiturk defaults. This enables
having different config settings locally versus on hosted platforms such as Heorku.
See the :ref:`configuration-overview` page for more information.

Note that the location of a few config variables has changed -- specifically,
``contact_email_on_error`` and ``cutoff_time`` have moved under the ``Task Parameters`` section.

.. note::
  If you are migrating a current experiment, it is recommended that you copy
  `the example config file from github <example-config-file_>`_
  and fill in your experiment's values.

.. _example-config-file: https://github.com/NYUCCL/psiTurk/blob/master/psiturk/example/config.txt.sample

No More Python 2
----------------

psiTurk 3 drops support for python 2, for various reasons. See the changelog_ for
more details.

Detailed changelog
------------------

For a more detailed listing of changes between psiturk 2 and 3, see the
`changelog on github <changelog_>`_.

.. _changelog: https://github.com/NYUCCL/psiTurk/blob/master/CHANGELOG.md
