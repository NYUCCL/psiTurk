Getting setup with psiturk.org
==========================================

**psiturk.org** is a cloud-based system which provides
users with information about their hits (who has accepted
the hit, where they are located, etc...) and which 
provides a SSL-signed secure Ad server (ensuring that
the majority of Workers can access your task).

Creating a psiturk.org account
----------------------------------

The first step in using psiturk.org is to sign up.
A free account can be created at `https://psiturk.org/register <https://psiturk.org/register>`__.

Obtaining psiturk.org API credentials
--------------------------------------

To previous your email and password from being
passed repeatedly over the Internet when using
psiturk.org, you access the psiturk.org API services
uses a API key. To obtain your personal API keys
login to psiturk.org (`https://psiturk.org/login <https://psiturk.org/login>`__).
On the main dashbaord page, select the blue dropdown
menu on the top right hand side of the page and select
"API Keys".  Copy these keys into your ``~/.psiturkconfig`` file.

At any time you can regenerate these keys on the same page.
At that point any old keys will no longer work, and you will
need to update you ``~\.psiturkconfig`` file again.