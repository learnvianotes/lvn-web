# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.1] - 2026-11-25

### Fixed

- Signing in works on the live site again, and the Google button is back: the site was built to call the server at the app's own address, which does not answer there. It now calls api.learnvianotes.in (new `LVN_API_URL` deploy variable).
- The Appearance settings no longer show an error for the Ink colour.

### Changed

- Sign-up asks only for your name, email and password (or one tap with Google). No age, no college email (add it later from Verify), no checkbox.
- Sign-in and sign-up are one focused screen that fits without scrolling: Google first, then your email; password and passkey are one tap away.
- A sharper look everywhere: white and near-black instead of warm paper, real borders, small square corners and no soft shadows.

## [0.7.0] - 2026-11-25

### Added

- A new look across the site: warm paper, ink blue and a highlighter yellow, IBM Plex Sans, a flat LVN logo and icons, and a landing page that shows the product instead of clip-art. [#86](https://github.com/learnvianotes/lvn-web/pull/86)
- Sign in with a passkey or a 6-digit code sent to your email; a password is still one tap away. The assistant is called Nova. [#86](https://github.com/learnvianotes/lvn-web/pull/86)

### Changed

- A PDF you just uploaded opens by itself once its virus check finishes, instead of saying it is not there. [#86](https://github.com/learnvianotes/lvn-web/pull/86)

### Removed

- GitHub and LinkedIn sign-in. [#86](https://github.com/learnvianotes/lvn-web/pull/86)

### Security

- Every library is on its latest compatible release, and the site knows about the newest messages the server can send (an admin sign-in code, age limits, protections for younger users). Library updates now arrive as one weekly pull request instead of ten. [#84](https://github.com/learnvianotes/lvn-web/pull/84)

### Fixed

- PDFs keep opening in the phone app: the site stays on the pdf.js version the app is built with, because the app loads pdf.js's files from the site. [#85](https://github.com/learnvianotes/lvn-web/pull/85)

## [0.6.0] - 2026-11-17

### Security

- Next.js is updated to 16.4.5, closing a flaw that could return one visitor's cached content to another (CVE-2026-119790). https://github.com/learnvianotes/lvn-web/pull/82

### Added

- Admins enter a code emailed to them before using admin tools, and can read an activity log of what admins changed. Ship this with the API change in learnvianotes/lvn-backend#92. https://github.com/learnvianotes/lvn-web/pull/80
- Platform admins can browse content that is not private, and anyone can turn product update emails off. https://github.com/learnvianotes/lvn-web/pull/81

### Fixed

- Leaving a page no longer records the cancelled request as a network error. A request that fails, or times out, still does. https://github.com/learnvianotes/lvn-web/pull/79

## [0.5.0] - 2026-11-12

First managed version. This is what is on production at `31e8115`.

### Added

- Sign-up from age 13. Ages 13–17 need a parent or guardian's consent, and the Privacy Policy and Terms are dated 2026-11-12.
- A public page at `/delete-account` that explains how to delete an account.
- One sign-in for the site.
- A versioning policy, a `/version` endpoint that reports the build's commit, and the version in the page footer. https://github.com/learnvianotes/lvn-web/pull/68

### Changed

- The interface was revamped.

Older detail is in the git history.
