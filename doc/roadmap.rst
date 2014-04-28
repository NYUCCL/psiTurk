Project Roadmap
==========================================

**psiTurk** is always looking to improve and to increase
the number of contributors.  We thought it would be helpful
to lay out a basic roadmap of where we would like to see the
project go in the future.  This roadmap may inspire you to
implement a new feature!


General priorities
~~~~~~~~~~~~~~~~~~

Documentation
-----------------
The documentation is greatly lagging behind progress on
the **psiTurk** platform.  We need help with people debugging
documentation, improving it, and making additions!  Notice how
all documentation pages (including this one!) include a link
to "Edit on GitHub".  Make a pull request and help us
improve these docs!

Automated testing
-----------------
The version 2.0 release introduced a number of new features
which are fairly complex because they require communication
over the Internet, RESTful APIs, etc...  While there are
automated unit tests for many of these features, it is
important to have better tests of these features.  Testing
isn't glamorous but writing tests improves your health,
looks, and chances of getting in heaven.

Alternative database solutions
-------------------------------
Currently **psiTurk** offers a variety of database solutions
including local SQLite files, self-administered MySQL
servers, and MySQL processes hosted on Amazon's Web
Services (RDS) platform.  However, all of these are a little
clunky and require users to know quite a bit about data management.
The demands placed on these databases by a single experiment
are not excessive, and thus there might be a more robust
solution (e.g., NoSQL).  One possibility is to host a robust
cloud-based data API off psiturk.org.

psiturk.js
------------------
All projects currently should use **psiturk.js** to 
save data to the server and update the user status as
they progress.  It might be nice if these included
additional features including easily displaying
instructions, providing simple quizes, etc...  In
theory many parts of the psiturk command
shell could be moved into the psiturk.js
library (e.g., one could even create hits and ads
via javascript calls).  This might eventually allow
the power of the psiturk platform to be leveraged
even on simple, standard web server platforms
(i.e., not relying on Flask).

Ad Server 
----------
The Ad Server has the potential to gather valuable
data about participants in studies, how naive they
are, etc...  Currently only a limited number of
statistics are gathered, and much of this data is
not publically accessible via an API or interface.  
Future versions of the psiturk.org dashboard could 
provide users with more interesting statistics 
about participants in their experiments, their geographic 
location, etc...

Unique IP issues
-----------------
A major issue with **psiTurk** is that it requires
a unique, Internet addressable IP address.  This is
a hurdle at some universities or companies.  This is
a bug and a feature at some level.  The feature side
is that for many users the ability to serve
experiments off their local computer obviates the
need for a dedicated server and simplifies some
web security issues.  For other users thought this
is a fustrating hurdle to overcome in order to
use psiturk.  We are interesting in the community's
thoughts about this and suggestions about best
practices include cloud based hosting systems like
Red Hat's OpenShift and Amazon's AWS.

Version 3.0
~~~~~~~~~~~~~~~~~~

We envision that eventually psiturk could move
entirely into the cloud (i.e., no need for
user to install command line tool).  This may be
supported by changes and extensions to the psiturk.org API
and the psiturk.js library.  The emphasis in our
initial development has been on advanced users/programmers
comfortable in a unix environment, 
but future version could emphasize novice web programmers
who are new to online experiments (e.g., undergrads).

If you have ideas about future directions for the project
the Github `issues tracker <https://github.com/NYUCCL/psiTurk/issues?state=open>`__ is a great place to share them.

