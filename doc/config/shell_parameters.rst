Shell Parameters
================

The Shell Parameters section contains details about
the psiturk shell.

::

	[Shell Parameters]
	launch_in_sandbox_mode = true
	bonus_message = "Thanks for participating!"
	use_psiturk_ad_server = true
	ad_location = false


`launch_in_sandbox_mode` [true | false]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If set to `true`, the psiturk shell will launch in sandbox mode. if set to
`false`, the shell will launch in live mode. We recommend leaving this option
to `true` to lessen the chance of accidentally posting a live HIT to mTurk.

.. seealso::

   `Overview of the command-line interface <../command_line_overview.html>`__
   	  The basic features of the **psiTurk** command line.


`bonus_message` [string]
~~~~~~~~~~~~~~~~~~~~~~~~

If set to a string, automatically uses this string as the message to
participants when bonusing them for an assignment. If not set, you will be
prompted to type in a message each time you bonus participants. (This message is
required by AMT.)

`use_psiturk_ad_server` [true | false]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Non-use of the psiturk ad server is an experimental feature.

If set to `true`, then the **psiTurk** secure ad server functionality will be enabled,
and your ad will be hosted on psiturk.org when creating hits on AMT.

If you want to host your own ad, then set this to `false`. You are responsible for obtaining
your own cert and key and for configuring your own proxy server in front
of psiturk/gunicorn. It is not necessary to also include the cert and key
in the [Server Parameters] section -- you can have a proxy server
such as nginx in front of psiturk/gunicorn which handles SSL connections.
Although if you don't have your SSL certs in both places, then traffic between
your proxy server and psiturk/gunicorn will not be encrypted. Perhaps that
doesn't matter to you though if you configure your proxy server to pass traffic
to your gunicorn/psiturk server via localhost.

If set to `false` then you must also specify your custom `ad_location` (see below).

.. seealso::

    See the `[Server Parameters] certfile and keyfile configs <server_parameters.html>`__
    for ssl-enabling the psiturk server (although this is not required to use your
    own ad location).

.. seealso::

    See `this gist`_ for an example nginx psiturk SSL configuration


`ad_location` [false | string]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. warning::

    Non-use of the psiturk ad server is an experimental feature.

`ad_location` is only used if `use_psiturk_ad_server` is `false`.
Set to whatever you set up your proxy server to listen on. This will be sent directly
to AMT when creating your HITs to tell AMT where to look for your ad.

Format is as follows::

    https://<host>:<port>/ad

Some gotcha's:

* don't forget the `/ad` at the end. And don't append a trailing backslash.
* you must use `https://` or AMT will explode.
* the `<port>` should be the port your *proxy server* (such as nginx) is running on, *not* the **psiturk** port. See the `gist`_ for a full example.

.. seealso::

    See the information for the `use_psiturk_ad_server` configuration above as well.

.. _this gist: gist_
.. _gist: https://gist.github.com/deargle/5d8c01660a77b8090a2cd24efcda2c59
