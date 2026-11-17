# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security

- Next.js is updated to 16.4.5, closing a flaw that could return one visitor's cached content to another (CVE-2026-119790). https://github.com/learnvianotes/lvn-web/pull/82

### Added

- A versioning policy, a `/version` endpoint that reports the build's commit, and the version in the page footer. https://github.com/learnvianotes/lvn-web/pull/68

### Fixed

- Leaving a page no longer records the cancelled request as a network error. A request that fails, or times out, still does. https://github.com/learnvianotes/lvn-web/pull/79

## [0.5.0] - 2026-11-12

First managed version. This is what is on production at `31e8115`.

### Added

- Sign-up from age 13. Ages 13–17 need a parent or guardian's consent, and the Privacy Policy and Terms are dated 2026-11-12.
- A public page at `/delete-account` that explains how to delete an account.
- One sign-in for the site.

### Changed

- The interface was revamped.

Older detail is in the git history.
