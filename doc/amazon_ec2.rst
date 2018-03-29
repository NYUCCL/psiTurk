Running psiTurk on Amazon's Elastic Compute Cloud (EC2)
=========================================================

With `Amazon Web Services` (commonly abbreviated as `AWS`), you can host your experiment in the cloud, using `Amazon's Elastic Compute Cloud` (commonly abbreviated as `EC2`). What follows is a description of how to set up and modify `psiTurk` on `AWS` using a pre-built `EC2` image.

If you don't already have an `AWS` account, first follow the
instructions in `Getting setup with Amazon Mechanical Turk <amt_setup.html>`_.


Setting up a psiTurk EC2 instance using a pre-built image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Sign in to your Amazon Web Services account and navigate to `The AWS Console <https://console.aws.amazon.com/console/>`_, then click on EC2 under the 'Compute' section, located under the 'All services' heading.

#. Make sure that the location in the top right corner is set to 'US East (N. Virginia)'. (If not, you will not find the pre-built image when searching for it.)

#. Either click the 'Launch Instance' button that appears on the EC2 dashboard,
   or click 'Instances' under the 'INSTANCES' section on the left menu, then
   click 'Launch Instance' there.

#. You should now be at 'Step 1: Choose an Amazon Machine Image (AMI)' in the
   EC2 Launch Instance Wizard. Click 'Community AMIs' on the left, then in the 'Search community AMIs'
   search box, search for 'ami-bcab37d4'. A
   single AMI should be listed: 'ubuntu-psiturk-2 - ami-bcab37d4'. Click 'Select'
   on this AMI.

#. Choose your instance type. The micro instance is free-tier eligible and
   should be sufficient unless you're expecting very high traffic, bandwidth or
   lots of heavy computation on your experiment server. Click 'Next: Configure
   Instance Details' at the bottom.

#. Click 'Next: Add Storage' and then 'Next: Add Tags'.

#. You should now be at 'Step 5: Tag Instance'. Click 'Add Tag' and name your EC2 instance in the 'Key' field so that you'll be able to tell it apart from other instances you might run in the future. Then click 'Next: Configure Security Group'.

#. A security group is a set of firewall rules that dictate who can access your server (based on IP) and through which ports. You can create multiple security groups and assign one or more of them to any of your EC2 instances. We'll use a single security group for our instance.

   Check the 'Create a new security group' radio button and fill in a name for
   your security group. There should already be a rule for SSH with its `Source`
   (which IPs can connect via SSH) set to `Anywhere` (any IP). You can change
   this to `My IP` for added security, but if your computer's IP address
   changes, which will likely happen if you change physical locations, you'll
   need to modify this rule before you can connect via SSH again.

   Click `Add Rule`, set the `Type` to Custom TCP Rule, and set the `Port Range`
   to '22362', the port that the psiTurk server runs on by default. If you set the
   `Source` to `My IP`, be sure to change it back to `Anywhere` before you try
   to run the experiment on Mechanical Turk, otherwise nobody will be able to
   access it. Click 'Review and Launch'.

#. If you chose `Anywhere` for either of the two Security Group Rules, you'll be shown a warning about this. Review your settings and click `Launch`.

#. You'll now be prompted to download a key pair to use for public key-based authentication when logging in via `SSH <https://en.wikipedia.org/wiki/Secure_Shell>`_. This is far more secure than password-based authentication. Select `Create a new key pair`, and name the key pair to whatever you want (preferably the same name as your instance). Click `Download Key Pair` and save the .pem file somewhere safe yet accessible as you'll need it every time you connect via `SSH`. Check the acknowledgment checkbox and click `Launch Instance` to complete the instance creation process.

#. On Linux or Mac, set the file permissions on the key so that only you can read it. You can do this by opening the terminal, navigate to the folder where you saved your key pair and then type ::

     $ chmod 400 your-key.pem


Connecting to your EC2 instance using SSH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#. Navigate back to the EC2 console (`AWS Console
   <https://console.aws.amazon.com/console/>`. Then click on "Instances" under the "INSTANCES" section on the left menu and click in the checkbox for the instance that you want to connect to. In the info appearing at the bottom, look for the `IPv4 Public IP` entry.

#. Use the public key you downloaded during instance creation to connect to the
   machine at the public IP you just found. The default username for the pre-built
   image is `ubuntu`. On `Linux` or `MacOS`, open up a terminal session, navigate to the folder where you saved your key pair and type ::

     ssh -i your-key.pem.txt ubuntu@xx.xx.xx.xxx

   where `xx.xx.xx.xxx` should be replaced with the public IP you just found. Type `yes` when the system asks you whether to continue connecting. You should now be logged into the instance. If you get a `Permissions ... are
   too open` error, follow the `chmod step` in the previous section to
   fix this.
