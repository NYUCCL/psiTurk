.. _amt-setup:

============================================
Setting Up an Amazon Mechanical Turk Account
============================================

psiTurk can interface with Amazon Mechanical Turk (although it doesn't have to!).
To do so, you need to create an account on Amazon's website in order to use it.
There are a number of steps involved here which have to do with signing up with
Amazon and creating several accounts. Luckily they are a one-time process for a given AWS account.

Accounts Creation and Linking
----------------------------

Carefully follow `AWS's guide`__ for setting up the necessary accounts for using
Amazon Mechanical Turk. Before doing so, note the following:

__ https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html#setup-aws-account

* **Step 5** discusses setting up the Developer Sandbox. Carefully follow all steps
  in this section, including the steps in the note for linking your aws account
  *specifically to the sandbox.*

* **Step 6** in the guide is "Set up an AWS SDK". You may skip this step -- psiTurk
  uses the `Python/Boto <https://aws.amazon.com/sdk-for-python/>`__ (Boto3) SDK
  under the hood.

* **Step 7** in the guide suggests the option of enabling AWS Billing for your account.
  However, at least one psiTurk user has reported difficulties doing so, needing
  to contact AWS customer support before being able to post hits.

.. _amt-credentials:

AWS Credentials
---------------

psiTurk uses the `Python/Boto <https://aws.amazon.com/sdk-for-python/>`__ (Boto3)
SDK to communicate with the AWS API. In order to do so, boto must have access to
the user's AWS credentials, generated in section :ref:`amt-setup`.

There are two approaches for setting the keys: (1) in a file called
``.psiturkconfig``, and (2) in any of the ways that Boto expects.

.. _amt-creds-psiturkconfig-approach:

.psiturkconfig approach
^^^^^^^^^^^^^^^^^^^^^^^

If set here, the keys should be lowercased, and under an 'AWS Access' section
key, as follows::

  [AWS Access]
  aws_access_key_id = foo
  aws_secret_access_key = bar


Boto approach
^^^^^^^^^^^^^

If AWS credentials are not found via the :ref:`amt-creds-psiturkconfig-approach`,
then Boto will search for them via its typical methods. That is,
psiTurk users can store AWS credentials `in a way that Boto expects`__.
Specifically, the credentials variables ``AWS_ACCESS_KEY_ID`` and
``AWS_SECRET_ACCESSS_KEY`` can be set via one of the following methods,
listed in order of preference:

__ https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

#. Environment variables (can optionally be set in ``.env``)
#. Shared credential file (``~/.aws/credentials``)
#. AWS config file (``~/.aws/config``)
#. Boto2 config file (``/etc/boto.cfg`` and ``~/.boto``)

.. note::
    psiTurk sets the ``AWS_DEFAULT_REGION`` to 'us-east-1', and this cannot be
    overridden.

For example, if a user's ``AWS_ACCESS_KEY_ID`` were 'foo', their
``AWS_SECRET_ACCESS_KEY`` were 'bar', they might set the following in
their ``~/.aws/credentials`` file::

  AWS_ACCESS_KEY_ID=foo
  AWS_SECRET_ACCESSS_KEY=bar

Note that Boto3 respects certain environment variables that alter which files are
searched for credentials and configuration settings. See
`here <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html>`__
for more information.
