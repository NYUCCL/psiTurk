.. _migrating:

Migrating from psiturk 2 to 3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
