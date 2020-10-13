# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased 3.0.0]
### Changed
- Drop support for python2
- upgrade cmd2 to 0.9 (python3 only)

### Added
- add ability to customize participant condition assignment. (see 309a623)
- add a sweet dashboard for doing amazing things, and the beginnings of a sort-of REST API that the dashboard uses.
  See `/dashboard` route.
- if a commonly-forgotten required template is missing when not using the psiturk ad server, raise an exception

## [2.3.11]
### Fixed
- fix unable to do non-aws things on without aws credentials (#427)

## [2.3.10]
### Fixed
-- patch pass bonus amount as shell arg

## [2.3.9]
### Fixed
- fix extend hit (#421)

## [2.3.8]
### Fixed
- specified `setproctitle` in requirements.txt, to fix "server blocked" status message. Necessary for gunicorn < 20.0,
  but gunicorn >=20.0 requires python3

## [2.3.7]
### Fixed
- requirements.txt generated with help of `pipreqs` instead of `pip freeze`, removing stale child dependencies, one
  of which was breaking zsh on osx catalina (#386)

## [2.3.6]
### Fixed
- download_datafiles works on both python2 and python3 (#375)
- gnureadline not forced onto macosx users (#371)

## [2.3.5]
### Fixed
- moved _get_local_hitids out of list comprehension (#380)


## [2.3.4]
### Fixed
- worker bonus didn't do anything because of shell parsing bug (see #377)
- (probably) fixed utf-8 encoding issue when opening consent.html or ad.html


## [2.3.3]
### Fixed
- datastring encoding to db was wrong
- for python2, needed to check against six.string_types instead of str
- `worker approve <assignmentid | hitid>` was incorrectly looking for already-credited local submissions instead of just submitted ones
- `worker approve --hitid` was not filtering to just the local study


## [2.3.2]
### Added
- add explanation for non-aws-users for how to use psiturk server commands without launching the shell

### Fixed
- `psiturk hit create` with use_psiturk_ad_server was throwing an error when trying to create a hit because
  of a missing success attribute on wrapperresponsesuccess


## [2.3.1]
### Added
- test suite to pave the way for migrating to Python 3 (woo!)
- Support for Python 3.6 and 3.7
- travis CI runs setup.py tests for python 2.7, 3.6, and 3.7
- table that tracks psiturk-created HITids in local db

### Changed
- `psiturk_shell` file does all printing through cmd2's `.poutput` so that stuff can be redirected
- `amt_services_wrapper` and `amt_services` functions are wrapped via decorator so that they return a consistent Response-type object. This
  effectively separates the `print`ing of any psiturk_shell data from the core psiturk functions. This will make a web interface doable. Also,
  it allows for the core functions to throw meaningful exceptions, which are caught by the wrapper and returned.
- psiturk status message is pulled from github repo instead of from an api call to the psiturk.org api server.
  Also, the call to load this does not depend directly on urllib2 anymore.
- update many dependencies because why not

### Removed
- Shell support for EC2 MySQL

### Fixed
- #352 - expiring a hit didn't push far enough into the past to actually expire instead of extend on the mturk side

## [2.3.0]
### Fixed
- moved AWS mturk api to 2017–01–17 via a move to boto3. No psiturk version prior to 2.3.0 will work.


[Unreleased 3.0.0]: https://github.com/NYUCCL/psiTurk/tree/master
[Unreleased 2.3.x]: https://github.com/NYUCCL/psiTurk/tree/python2
[2.3.5]: https://github.com/NYUCCL/psiTurk/compare/2.3.4...2.3.5
[2.3.4]: https://github.com/NYUCCL/psiTurk/compare/2.3.3...2.3.4
[2.3.3]: https://github.com/NYUCCL/psiTurk/compare/2.3.2...2.3.3
[2.3.2]: https://github.com/NYUCCL/psiTurk/compare/2.3.1...2.3.2
[2.3.1]: https://github.com/NYUCCL/psiTurk/compare/2.3.0...2.3.1
