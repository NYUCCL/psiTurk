Getting setup with Amazon Mechanical Turk
==========================================

**psiTurk** is a system for interfacing with Amazon
Mechanical Turk.  Thus, you need to create an account
on Amazon's website in order to use it.  There are a number
of steps involved here which have to do with signing up with Amazon.
Luckily they are a one-time process (possibly once for your
entire lab if everyone shares a single AWS account).

Creating an AWS account
----------------------------------

Start by going to the Amazon Web Services page `here <http://aws.amazon.com>`__. If you made a Mechanical Turk account prior to this, sign in to your account and may skip to the next paragraph. Otherwise, click the Sign Up button at the top.  

.. image:: images/docs_AWS_signup_button.png
	:align: center


You should be redirected to a form asking for your contact information. Fill out the form and continue to the next section. 

.. image:: images/docs_AWS_form_contact_info.png
	:align: center 

Next, you will need you credit card and your phone. The form should now ask for your credit card information. 

.. image:: images/docs_AWS_form_credit_card.png
	:align: center 

If you do not see the forms to fill in your credit card information, go to the Payment Methods page either by clicking the link on the toolbar to the left or `here <https://portal.aws.amazon.com/gp/aws/developer/account?ie=UTF8&action=payment-method>`__. Enter in your credit card information. (Amazon will only charge you, if you use their cloud services. Signing up for an account should not incur any charges.) 

On the next page, you will be asked to enter your phone number. Have your phone nearby. After you put in your phone number the webpage will display a 4-digit pin code and Amazon will call you. Enter the pin on your phone's keypad when prompted by the call.

.. image:: images/docs_AWS_form_phone.png
	:align: center


.. image:: images/docs_AWS_form_pin.png
	:align: center

Amazon will ask you to select a support plan. For the purposes of psiTurk, you only need the Basic(Free) plan. Click continue. 
 
Your Amazon Web Service account should be set up now. 

Obtaining AWS credentials
------------

An AWS key is required for posting new HITs to mechanical turk as well as monitoring existing HITs. You receive your key when you open an Amazon Web Services account. If you already have an AWS account, your key can be retrieved 
`here <http://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key>`__.
The values of these keys need to be placed in you ``~/.psiturkconfig`` file.

Creating an AMT Requester account
----------------------------------

To use your AWS keys to interface with Amazon Mechanical Turk, you need to create a requester account.
Please see `Amazon's instructions <http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html>`__ for this.  In particular, it appears important to actually login to the requester site at least once (`http://requester.mturk.com <http://requester.mturk.com>`__) so that you can agree to the terms of service.

Linking funds
----------------------------------


Additional instructions 
----------------------------------
