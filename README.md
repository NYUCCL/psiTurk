<img src="https://psiturk.org/static/images/psiturk_logo_README.png">

[![Build Status](https://travis-ci.org/NYUCCL/psiTurk.png?branch=master)](https://travis-ci.org/NYUCCL/psiTurk)
[![Latest Version](https://img.shields.io/pypi/v/psiturk.svg?style=flat-square&label=latest%20stable%20version)](https://pypi.python.org/pypi/psiturk/)
[![Coverage Status](https://coveralls.io/repos/github/NYUCCL/psiTurk/badge.svg?branch=master)](https://coveralls.io/github/NYUCCL/psiTurk?branch=master)
[![License](http://img.shields.io/badge/license-MIT-red.svg)](http://en.wikipedia.org/wiki/MIT_License)
[![DOI](https://zenodo.org/badge/4845420.svg)](https://zenodo.org/badge/latestdoi/4845420)


Please visit [psiturk.org](https://psiturk.org) for more information.

[Psiturk Google Group](https://groups.google.com/forum/#!forum/psiturk)



# Versions

- **v2.3.0** | minimum-version that can be used with current Amazon mturk API. python2-only
- **v2.3.1 -- v2.3.x** | python2 branch in the git repo. Supports both python2 and python3. Receiving hot-fixes only, and releases will only increment 2.3.x.
- **unreleased -- forthcoming v3.x.x** | master branch, feature branch. python3 _only_. psiTurk v3.x.x will be released from this branch.




# Developing

Check out a clone of this repo, and install it into your local environment for testing
(consider installing into a virtualenv):

```
git clone git@github.com:NYUCCL/psiTurk.git
pip install -e psiTurk
```

A test suite can be run using `pytest` from within the base directory of psiturk.




# Citing 

To credit psiTurk in your work, please cite both the original conference paper and a version of the Zenodo archive.
The former provides a high level description of the package, and the latter points to a permanent record of all psiTurk
versions (we encourage you to cite the specific version you used). Example citations (for psiTurk 2.3.7):

Eargle, David, Gureckis, Todd, Rich, Alexander S., McDonnell, John, & Martin, Jay B. (2020, January 6). 
psiTurk: An open platform for science on Amazon Mechanical Turk (Version v2.3.7). Zenodo. http://doi.org/10.5281/zenodo.3598652

McDonnell, J.V., Martin, J.B., Markant, D.B., Coenen, A., Rich, A.S., and Gureckis, T.M. 
(2012). psiTurk (Version 1.02) [Software]. New York, NY: New York University. 
Available from https://github.com/NYUCCL/psiTurk