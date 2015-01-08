=======================================================
 Using psiTurk on Amazon's Elastic Compute Cloud (EC2)
=======================================================

If you don't already have an Amazon Web Services (AWS) account, first follow the
instructions in `Getting setup with Amazon Mechanical Turk <amt_setup.html>`.

===================================
 Using the pre-built psiTurk image
===================================

1. Sign in to your AWS account and navigate to `The AWS Console
   <https://console.aws.amazon.com/console/>`, then click on EC2 under the
   "Compute" section.

2. Either click the "Launch Instance" button that appears on the EC2 dashboard,
   or click "Instances" under the "INSTANCES" section on the left menu, then
   click "Launch Instance" there.

3. You should now be at "Step 1: Choose an Amazon Machine Image (AMI)" in the
   EC2 Launch Instance Wizard. Click "Community AMIs" on the left, then in the
   search box enter ami-bcab37d4 in the "Search community AMIs" search box. A
   single AMI should be listed, "ubuntu-psiturk-2 - ami-bcab37d4", click Select
   on this AMI.

4. Choose your instance type. The micro instance is free-tier eligible and
   should be sufficient unless you're expecting very high traffic, bandwidth or
   lots of heavy computation on your experiment server. Click "Next: Configure
   Instance Details" at the bottom.

5. Click Next until you're at "Step 5: Tag Instance".

6. Name your EC2 instance so you'll be able to tell it apart from other
   instances you might run in the future. Click "Next: Configure Security Group"

7. A security group is a set of firewall rules that dictate who can access your
   server (based on IP) and through which ports. You can create multiple
   security groups and assign one or more of them to any of your EC2 instances.
   We'll use a single security group for our instance.

   Check the "Create a new security group" radio button and fill in a name for
   your security group. There should already be a rule for SSH with its `Source`
   (which IPs can connect via SSH) set to `Anywhere` (any IP) . You can change
   this to `My IP` for added security, but if your computer's IP address
   changes, which will likely happen if you change physical locations, you'll
   need to modify this rule before you can connect via SSH again.

   Click `Add Rule`, set the `Type` to Custom TCP Rule, and set the `Port Range`
   to 22362, the port that the psiTurk server runs on by default. If you set the
   `Source` to `My IP`, be sure to change it back to `Anywhere` before you try
   to run the experiment on Mechanical Turk, otherwise nobody will be able to
   access it. Click "Review and Launch"

8. If you chose `Anywhere` for either of the two Security Group Rules, you'll be
   shown a warning about this. Review your settings and click `Launch`.

9. You'll now be prompted to download a key pair to use for public key-based
   authentication when logging in via SSH. This is far more secure than
   password-based authentication. Select `Create a new key pair`, and name the
   key pair after your instance. Click `Download Key Pair` and save the .pem file
   somewhere safe yet accessible, as you'll need it every time you connect via
   ssh. Check the acknowledgment checkbox and click `Launch Instance` to
   complete the instance creation process.

10. On Linux or Mac, set the file permissions on the key so that only you can
    read it ::

     $ chmod 400 your-key.pem

=================================
 Connecting to your EC2 Instance
=================================

1. Find your instance's public IP. Navigate to the EC2 console (`AWS Console
   <https://console.aws.amazon.com/console/>` > EC2 > Instances link on the
   left) and click on the instance you want to connect to. In the info below the
   table, look for the `Public IP` entry.

2. Use the public key you downloaded during instance creation to connect to the
   machine at the IP you just found. The default username for the pre-built
   image is "ubuntu". ::

     ssh -i your-key.pem ubuntu@xx.xx.xx.xxx

   You should now be logged into the instance. If you get a "Permissions ... are
   too open" error, follow the chmod step in the instance setup instructions to
   fix this.
