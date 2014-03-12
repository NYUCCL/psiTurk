Getting setup with Amazon Mechanical Turk
==========================================

**psiTurk** is a system for interfacing with Amazon
Mechanical Turk.  Thus, you need to create an account
on Amazon's website in order to use it.

Creating an AWS account
----------------------------------

Start by going to the Amazon Web Services page `here <http://aws.amazon.com>`__. If you made a Mechanical Turk account prior to this, sign in to your account and may skip to the next paragraph. Otherwise, click the Sign Up button at the top. You will need to fill out the forms with your name, address, etc.  

Next, you will need you credit card and your phone at this point. If you do not see the forms to fill in your credit card information, go to the Payment Methods page either by clicking the link on the toolbar to the left or `here <https://portal.aws.amazon.com/gp/aws/developer/account?ie=UTF8&action=payment-method>`__. Enter in your credit card information. (Amazon will only charge you, if you use their cloud services. Signing up for an account should not incur any charges.) 

On the next page, you will be asked to enter your phone number. Have your phone nearby. The form will display a pin code that you will need to enter on your phone's keypad when Amazon calls you. Once your pin has been verified, your account will be set up. 

Obtaining AWS credentials
------------

An AWS key is required for posting new HITs to mechanical turk as well as monitoring existing HITs. You receive your key when you open an Amazon Web Services account. If you already have an AWS account, your key can be retrieved 
`here <http://aws-portal.amazon.com/gp/aws/developer/account/index.html?action=access-key>`__.
The values of these keys need to be placed in you ``~/.psiturkconfig`` file.

Creating an AMT Requester account
----------------------------------

`Amazon's instructions <http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMechanicalTurkGettingStartedGuide/SetUp.html> `

Linking funds
----------------------------------


Additional instructions 
----------------------------------
