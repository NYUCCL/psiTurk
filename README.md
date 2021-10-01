<img src="https://raw.githubusercontent.com/NYUCCL/psiTurk/gh-pages/static/images/psiturk_logo_README.png">

[![Build Status](https://github.com/NYUCCL/psiTurk/actions/workflows/python-app.yml/badge.svg)](https://github.com/NYUCCL/psiTurk/actions/workflows/python-app.yml)
[![Latest Version](https://img.shields.io/pypi/v/psiturk.svg?style=flat-square&label=latest%20stable%20version)](https://pypi.python.org/pypi/psiturk/)
[![Coverage Status](https://coveralls.io/repos/github/NYUCCL/psiTurk/badge.svg?branch=master)](https://coveralls.io/github/NYUCCL/psiTurk?branch=master)
[![License](http://img.shields.io/badge/license-MIT-red.svg)](http://en.wikipedia.org/wiki/MIT_License)
[![DOI](https://zenodo.org/badge/4845420.svg)](https://zenodo.org/badge/latestdoi/4845420)


Please visit [psiturk.org](https://psiturk.org) for more information.

[Psiturk Google Group](https://groups.google.com/forum/#!forum/psiturk)



# Versions

psiTurk v3 has been released! See the migration guide [here](https://psiturk.readthedocs.io/en/latest/migrating.html).

psiTurk v3 does not support the psiturk ad server. If you still need
the psiTurk ad server, use psiTurk v2.3.12, and remove all HTML comments
from your `ad.html` file. Versions less than v2.3.12 will not be able to post
HITs due to a change implemented by the psiturk ad server's hosting provider. You can upgrade to psiturk v2.3.12 by running `pip install --upgrade psiturk=2.3.12`.

# Python versions

- Psiturk v2 supports python 2 and python 3. Documentation for psiturk v2 is available [here](https://psiturk.readthedocs.io/en/python2/)
- Psiturk v3 is python 3 only. Documentation available [here](https://psiturk.readthedocs.io/en/latest/)

# Developing

Check out a clone of this repo, and install it into your local environment for testing
(consider installing into a virtualenv):

```
git clone git@github.com:NYUCCL/psiTurk.git
pip install -e psiTurk
```

A test suite can be run using `pytest` from within the base directory of psiturk.




# Citing

To credit psiTurk in your work, please cite both the original journal paper and a version of the Zenodo archive.
The former provides a high level description of the package, and the latter points to a permanent record of all psiTurk
versions (we encourage you to cite the specific version you used). Example citations (for psiTurk 2.3.7):

### Zenodo Archive:  
Eargle, David, Gureckis, Todd, Rich, Alexander S., McDonnell, John, & Martin, Jay B. (2020, January 6).
psiTurk: An open platform for science on Amazon Mechanical Turk (Version v2.3.7). Zenodo. http://doi.org/10.5281/zenodo.3598652

### Journal Paper:  
Gureckis, T.M., Martin, J., McDonnell, J., Rich, A.S., Markant, D., Coenen, A., Halpern, D., Hamrick, J.B., Chan, P. (2016) psiTurk: An open-source framework for conducting replicable behavioral experiments online. Behavioral Research Methods, 48 (3), 829-842.	DOI: http://doi.org/10.3758/s13428-015-0642-8
