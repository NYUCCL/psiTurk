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

Carefully follow `AWS's guide`_ for setting up the necessary accounts for using
Amazon Mechanical Turk. Before doing so, note the following:

.. _AWS's guide: https://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html#setup-aws-account

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
While earlier versions of psiturk had users specify AWS credentials in a
global ``.psiturkconfig`` file, psiturk > v3.x has no such config file. Rather,
psiTurk users should store AWS credentials `in a way that Boto expects <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html>`__.
Specifically, *credentials* should be set via one of the following methods,
listed in order of Boto3 preference:

#. Environment variables
#. Shared credential file (``~/.aws/credentials``)
#. AWS config file (``~/.aws/config``)
#. Boto2 config file (``/etc/boto.cfg`` and ``~/.boto``)

At a minimum, the following credentials must be set for psiTurk to work:

* ``AWS_ACCESS_KEY_ID``
* ``AWS_SECRET_ACCESSS_KEY``

Boto3 *configuration* settings can be set in any of the above *except* for the
shared credential file location. The following configuration *must* be set
in order for psiTurk to be able to interface with AWS:

* ``AWS_DEFAULT_REGION`` (For example, ``us-west-1`` or ``us-east-1``)

For example, if a user's AWS_ACCESS_KEY_ID were 'foo', their AWS_SECRET_ACCESS_KEY
'bar', and their preferred AWS_DEFAULT_REGION was 'us-east-1', they might set the
following in their ``~/.aws/config`` file::

  AWS_ACCESS_KEY_ID=foo
  AWS_SECRET_ACCESSS_KEY=bar
  AWS_DEFAULT_REGION=us-east-1

Note that Boto3 respects certain environment variables that alter which files are
searched for credentials and configuration settings. See
`here <https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html>`__
for more information.
