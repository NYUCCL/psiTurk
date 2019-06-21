# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- test suite to pave the way for migrating to Python 3 (woo!)

### Changed
- `psiturk_shell` file does all printing through cmd2's `.poutput` so that stuff can be redirected
- when a hit is created, its hit_id is added
- most `amt_services_wrapper` functions support 
- psiturk status message is pulled from github repo instead of from an api call to the psiturk.org api server.
  Also, the call to load this does not depend directly on urllib2 anymore.
