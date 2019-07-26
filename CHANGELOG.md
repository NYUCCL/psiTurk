# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Changed
- Drop support for python2
- upgrade cmd2 to 0.9 (python3 only)

### Added
- add ability to customize participant condition assignment. (see 309a623)
- add a sweet dashboard for doing amazing things, and the beginnings of a sort-of REST API that the dashboard uses.
  See `/dashboard` route.

### Fixed
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
