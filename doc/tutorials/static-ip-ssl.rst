.. _static-ip-https:

=================================
Hosting your own HTTPS Experiment
=================================

With support for the psiTurk Secure Ad server dropped from psiturk 3,
you may wonder how you will now serve ads securely in order to run your experiments on platforms such
as AWS Mturk which still require that your experiment "ads" be served over HTTPS.

If you have been hosting your own experiments on your own server using a static IP address,
one option is to buy a domain name, and to let a DNS provider such as cloudflare
proxy HTTPS for you. With this approach, Cloudflare sits in between your participants
and your psiturk server. Cloudflare provides a valid HTTPS certificate to participants' browsers,
enabling your ads to be served over HTTPS. Then, Cloudflare can connect to your psiturk
server either over HTTP (unencrypted), or over HTTPS (encrypted). For the latter, you would configure your psiturk
server to either use a self-signed certificate, or to use a certificate provided by free
by Cloudflare. Regardless, participants' browsers will view the connection as secure.

Regardless of whether a proxied connection between Cloudflare and your psiturk server
is HTTP or HTTPS, Cloudflare has plaintext access to all of the data being sent
between the participants' browsers and your psiturk server.

The first option -- ``Cloudflare <- HTTP -> Psiturk server`` -- is called `"Flexible"`__ encryption.
With this option, your psiturk server **must run on port 80**. This means that,
unless you are using a reverse proxy on your server such as nginx or apache in front of your
psiturk servers, you can only have one psiturk experiment running on a given server at a
time. The second -- ``Cloudflare <- HTTPS -> Psiturk server`` -- is called `"Full"`__ encryption.
Read `Cloudflare's page on proxied HTTPS`__ for more information.

__ https://support.cloudflare.com/hc/en-us/articles/200170416-End-to-end-HTTPS-with-Cloudflare-Part-3-SSL-options#h_4e0d1a7c-eb71-4204-9e22-9d3ef9ef7fef
__ https://support.cloudflare.com/hc/en-us/articles/200170416-End-to-end-HTTPS-with-Cloudflare-Part-3-SSL-options#h_845b3d60-9a03-4db0-8de6-20edc5b11057
__ https://support.cloudflare.com/hc/en-us/articles/200170416-End-to-end-HTTPS-with-Cloudflare-Part-3-SSL-options


.. note::
  It is good practice to configure a reverse proxy server such as nginx or apache
  on your servers to (1) handle serving static files, taking that load off of your psiturk
  server and letting it handle running python routes, and (2) to more easily serve multiple experiments on one server.

  For the latter, reverse proxy servers can route to different psiturk servers depending on the domain
  name requested. For running multiple psiturk servers off of the same static IP, you might choose to set
  several subdomains in your DNS settings,
  each pointing to your same single IP address, but each associated with a different
  psiturk experiment.

.. note::
  For any experiment that has used the psiturk secure ad server in the past without
  configuring SSL support for the the psiturk server (gunicorn),
  it has always been the case that participant network traffic travels between the psiturk server
  and participants' browsers over HTTP (in plaintext). Only the *ad* traffuc was ever encrypted,
  to satisfy AWS Mturk requirements.
  By design, the Psiturk Ad Server handed off participants to psiturk server's static
  ip addresses over HTTP when participants clicked "Begin the study."


----

Setting up Cloudflare Flexible encryption is done as follows. The example below uses
the imaginary domain name **example.com** and imaginary static IP address **192.0.2.1**.

Purchase a domain name from a domain name registrar
---------------------------------------------------

You must first buy a domain name. These are inexpensive -- usually less than $10 per year per domain.
Use a domain name registrar such as [namecheap](), and buy any domain you like.

.. image:: /images/cloudflare_namecheap.png
   :target: https://www.namecheap.com/

Note that you cannot purchase domains directly from Cloudflare, although you *can* transfer domain names
to Cloudflare after a waiting period.

Create an account on Cloudflare if necessary
--------------------------------------------

.. image:: /images/cloudflare_signup.png
   :target: https://dash.cloudflare.com/sign-up

Add a new "site" to your Cloudflare account with the name of your purchased domain name
---------------------------------------------------------------------------------------

.. image:: /images/cloudflare_add_site.png

Set Cloudflare to be your DNS provider
--------------------------------------

Cloudflare will tell you that to complete the process, you must visit the site of your domain name registrar and
set Cloudflare to be your DNS provider. Once you have done so, this transfer process may take a few hours to complete.
The change has to propagate throughout the DNS servers of the world.

Cloudflare generally recognizes who your domain name registrar is based on the DNS servers your registrar auto-
configured for your domain. Cloudflare will generally point you to registrar-specific instructions for how
to configure your domain to use their DNS servers. If they don't, try a general internet search
for "cloudflare [name of registrar] set dns"

Create a DNS A record
---------------------

On the Cloudflare page for your site, in the DNS tab, set an ``A`` record pointing your domain name to your static ip address.

.. image:: /images/cloudflare_add_A_record.png

Make sure that this record is cloudflare-proxied. (It should have an orange cloud, not a grey cloud.)

Enable Flexible SSL
-------------------

In cloudflare, enable `flexible SSL <https://support.cloudflare.com/hc/en-us/articles/200170416-End-to-end-HTTPS-with-Cloudflare-Part-3-SSL-options#h_4e0d1a7c-eb71-4204-9e22-9d3ef9ef7fef>`_
for your domain.

.. image:: /images/cloudflare_set_flexible_ssl.png

Start your psiTurk server
-------------------------

Set your psiturk server to run on ``host=0.0.0.0`` and ``port=80``. Then, turn on your psiturk server::

  /psiturk-experiment-directory$ psiturk server on
  Now serving on http://0.0.0.0:80

----

Visit your domain name in your browser, using your psiturk server's port. You should see a secure connection.

If posting a HIT to mturk using the above settings, the :ref:`hit_configuration_ad_url_ad_url_domain` would be set to ``example.com``,
and the defaults of :ref:`hit_configuration_ad_url_ad_url_port`, :ref:`hit_configuration_ad_url_ad_url_protocol`, and :ref:`hit_configuration_ad_url_ad_url_route`.
