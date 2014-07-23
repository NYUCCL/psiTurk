# Contributing to psiTurk

Note: This guide is copied more or less from the [contributors guidelines](https://github.com/gureckis/gunicorn/blob/master/CONTRIBUTING.md)
of the [gunicorn](https://github.com/benoitc/gunicorn) project. Alternations
were made for the nature of this particular project.

Want to contributed to **psiTurk**? Awesome! Here are instructions to get you
started. We want to improve these as we go, so please provide feedback.

## Contribution guidelines

### Pull requests are always welcome

We are always thrilled to receive pull requests, and do our best to
process them as fast as possible. Not sure if that typo is worth a pull
request? Do it! We will appreciate it.

If your pull request is not accepted on the first try, don't be
discouraged! If there's a problem with the implementation, hopefully you
received feedback on what to improve.

We're trying very hard to keep **psiTurk** lean, focused, and useable. We don't want it
to do everything for everybody. This means that we might decide against
incorporating a new feature. However, there might be a way to implement
that feature *on top of* **psiTurk**.

**Please create pull requests for the dev branch rather than master**
so they can go through regular testing and evaluation prior to being
distributed via pypi.

### Discuss your design on the mailing list

We recommend discussing your plans in our [Google group](https://groups.google.com/d/forum/psiturk)
before starting to code -
especially for more ambitious contributions.  This gives other
contributors a chance to point you in the right direction, give feedback
on your design, and maybe point out if someone else is working on the
same thing.

### Create issues...

Any significant improvement should be documented as [a github
issue](https://github.com/NYUCCL/psiTurk/issues) before anybody starts
working on it.

### ...but check for existing issues first!

Please take a moment to check that an issue doesn't already exist
documenting your bug report or improvement proposal. If it does, it
never hurts to add a quick "+1" or "I have this problem too". This will
help prioritize the most common problems and requests.

### Conventions

Fork the repo and make changes on your fork in a new feature branch:

- If it's a bugfix branch, name it XXX-something where XXX is the number
  of the issue
- If it's a feature branch, create an enhancement issue to announce your
  intentions, and name it `XXX-something` where XXX is the number of the
issue.

Make sure you include relevant updates or additions to documentation
when creating or modifying features.

Write clean code. 

Pull requests descriptions should be as clear as possible and include a
reference to all the issues that they address.

Code review comments may be added to your pull request. Discuss, then
make the suggested modifications and push additional commits to your
feature branch. Be sure to post a comment after pushing. The new commits
will show up in the pull request automatically, but the reviewers will
not be notified unless you comment.

Commits that fix or close an issue should include a reference like
`Closes #XXX` or `Fixes #XXX`, which will automatically close the issue
when merged.

Add your name to the THANKS file, but make sure the list is sorted and
your name and email address match your git configuration.

## Contributing to the docs

Our docs are currently hosted at [readthedocs](psiturk.readthedocs.org). 
Readthedocs uses [Sphinx](http://sphinx-doc.org/) as the backend for their
documentation so in order to update the docs you will first have to install
Sphinx simply by typing

    easy_install -U Sphinx
into the command line.
All documentation files are in the docs folder and are formatted as 
reStructured Text. A good, detailed manual for the reStructured Text 
syntax can be found [here](http://docutils.sourceforge.net/docs/user/rst/quickstart.html). 
Some essentials:
The index page is the main page that users see will see when they open the 
docs. It is also how readthedocs generates the sidebar that contains all
the names of individual pages in the documentary so it is important that 
this is formatted correctly.
The main important feature is the [toctree](http://sphinx-doc.org/markup/toctree.html).
The toctree just looks like this:
```javascript
  .. toctree::
    forward
    install
    quickstart
    recording
```

Sphinx will go through the pages listed in the toctree, search for subject
headers and create both links for the index page and the sidebar in the 
correct format in the order that the pages are listed. For this reason, 
it is also very important that subjected headers be used correctly on
the individual pages. For example, the forward page has a title that looks 
like this:

    Forward
    =======

and subtitles that look like this:

    What is psiTurk?
    ~~~~~~~~~~~~~~~~

It actually doesn't matter what character you use for the underline, it can 
be any of 

    = - ` ' " : ~ ^ _ * + # < >
but it must be consistent since all headers with the same character will be 
at the same level. For convenience, we are using ===== to mean title and ~~~~~ 
to mean sub header.
Some other basic things in rST:

Links look like this: 

    `Getting psiTurk installed on your computer <install.html>`__
with the actual page in angle brackets. If the link is to another page within the docs, 
you only need to include the name of the page.
Whenever you include a code example, put this line before:

    .. code:: javascript


## Decision process

### How are decisions made?

In general, all decisions affecting **psiTurk**, big and small, follow the same 3 steps:

* Step 1: Open a pull request. Anyone can do this.

* Step 2: Discuss the pull request. Anyone can do this.

* Step 3: Accept or refuse a pull request. The little dictators do this (see below "Who decides what?")


### Who decides what?

psiTurk, like gunicorn, follows the timeless, highly efficient and totally unfair system
known as [Benevolent dictator for
life](http://en.wikipedia.org/wiki/Benevolent_Dictator_for_Life).  In the case of
psiTurk, there are multiple little dictators which are the core members of the
[gureckislab](http://gureckislab.org) research group and alumni.  The dictators
can be emailed at [authors@psiturk.org](mailto:authors@psiturk.org).

For new features from outside contributors, the hope is that friendly
consensus can be reached in the discussion on a pull request.  In cases where it 
isn't the original project creators [John McDonnell](https://github.com/johnmcdonnell) 
and/or [Todd Gureckis](https://github.com/gureckis) will intervene to decide.

The little dictators are not required to create pull requests when
proposing changes to the project.

### Is it possible to become a little dictator if I'm not in the Gureckis lab?

Yes, we will accept new dictators from people esp. engaged and helpful in 
improving the project.

### How is this process changed?

Just like everything else: by making a pull request :)
