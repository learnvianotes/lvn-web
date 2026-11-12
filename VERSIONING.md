# Versioning and releases

This file is the single source of truth for how this repo is versioned. Every person and every agent (Cursor cloud agents, Claude Code, Grok Bot agents) follows it. If anything here conflicts with an older habit, this file wins.

## 1. Scheme: Semantic Versioning (MAJOR.MINOR.PATCH)

- **PATCH** (0.1.3 -> 0.1.4): bug fixes, UI polish, copy changes, dependency bumps with no behaviour change.
- **MINOR** (0.1.4 -> 0.2.0): new user-visible features, new screens/pages, new GraphQL fields or mutations that are backward compatible.
- **MAJOR** (0.x -> 1.0.0, 1.x -> 2.0.0): breaking changes (removed/renamed API fields, data model changes old clients can't handle). While we are on 0.x, a breaking change bumps MINOR and must be called out as **BREAKING** in the changelog.
- 1.0.0 is cut only when the owner (K Manideep) says the product is generally available.

Each repo (lvn-backend, lvn-web, lvn-mobile) has its **own** version. They do not have to match.

## 2. Where the version lives

| Repo | Version source | Extra |
|---|---|---|
| lvn-mobile | `version` in `app.config.ts` / `app.json` and `package.json` (kept identical) | Android `versionCode` and iOS `buildNumber` (see 3) |
| lvn-web | `version` in `package.json` (read by `next.config.ts` into `NEXT_PUBLIC_APP_VERSION`) | Docker image tags (see 5) |
| lvn-backend | `version` in root `package.json` (and each workspace package that is released) | Docker image tags (see 5) |

The terms/privacy version (`TERMS_VERSION`, e.g. `2026-11-12`) is a **date**, independent of the app version. Only bump it when the legal text changes.

## 3. Mobile build numbers (lvn-mobile only)

- Android `versionCode` is an integer that goes **up by exactly 1 for every build uploaded to Google Play**, on any track. It is never reused and never goes down, even if a build is rejected or discarded.
- iOS `buildNumber` follows the same number as `versionCode`.
- A new `versionCode` with the same `version` is allowed only for a rebuild of the same code (e.g. signing fix). Any code change = new PATCH or higher.
- History so far: 0.1.2 (4), 0.1.3 (5), 0.1.4 (6). The next upload is versionCode 7.

## 4. Who bumps the version, and when

To avoid parallel agents fighting over the same version number:

1. **Feature/fix PRs do NOT change the version.** They add one line to `CHANGELOG.md` under `## [Unreleased]` in the right section (Added / Changed / Fixed / Removed / Security), written for a human, with the PR link.
2. **A release is its own small PR** titled `release: vX.Y.Z` (mobile: `release: vX.Y.Z (versionCode N)`). It only:
   - moves the `[Unreleased]` entries into a new `## [X.Y.Z] - YYYY-MM-DD` section,
   - bumps the version (and mobile `versionCode`/`buildNumber`),
   - nothing else.
3. After the release PR is merged, the release commit on `main` is tagged `vX.Y.Z` (annotated tag). Tags are never moved or deleted.
4. Builds and deploys are made **only from a tagged commit on `main`**. Never ship from a branch or an untagged commit.
5. Hotfix: branch from `main`, fix, PR, then a release PR with a PATCH bump. Same rules.

Only the owner merges to `main` unless he has explicitly authorised an agent for that change. Agents never merge their own PRs. All PRs target `main`; do not stack PRs.

## 5. Docker images (lvn-backend, lvn-web)

Every image built for deploy gets **two** tags:
- the short git SHA (e.g. `lvn-backend:d9d27b2d71f0`, `ghcr.io/learnvianotes/lvn-web:production-31e81150d2d5`), which is what deploy scripts pin to, and
- the version (e.g. `lvn-backend:v0.4.1`, `ghcr.io/learnvianotes/lvn-web:production-v0.5.0`).

The running version must be visible: backend exposes it on the health endpoint / `RELEASE` env as `vX.Y.Z+<shortsha>`; web shows it in the page footer or `/version`.

## 6. CHANGELOG.md

- Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
- Newest release at the top, `[Unreleased]` always present above it.
- Mobile entries also note the `versionCode` and the Play track(s) it went to.
- Write for users and the owner, not for machines: "Code blocks now scroll sideways on phones", not "fix overflow-x".

## 7. Checklist for any agent touching this repo

- [ ] My PR does not change the version (unless it is a `release:` PR).
- [ ] I added a line under `[Unreleased]` in `CHANGELOG.md`.
- [ ] For a release PR: version bumped in every file listed in section 2, mobile `versionCode` = previous + 1, changelog section dated (Asia/Calcutta date).
- [ ] After merge: tag `vX.Y.Z` on the merge commit; build/deploy only from that tag; record the image SHA tags / AAB SHA-256 in the release notes.
