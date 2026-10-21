# Docs

The architecture spec, ADRs, ERD, environment reference, API-change notes and release notes are shared by all three
repositories and live in **lvn-backend `docs/`** (ADR-0004). Start with lvn-backend
`docs/architecture/lvn-architecture-v2.md` — the single source of truth.

This repository keeps only what is specific to the web app:

| File | Contents |
| --- | --- |
| [architecture/web-addendum.md](architecture/web-addendum.md) | How lvn-web implements spec §12: route map, folder map, budgets |
| [runbooks/web.md](runbooks/web.md) | Web-only operational procedures |
| [launch.md](launch.md) | The College/Interview launch fixes on the rewrite: status, the owner's open decisions, the age check, legal notes |
| [runbooks/release.md](runbooks/release.md) | Releasing: the sandbox from `release/**`, production from `v*` tags (lvn-backend ADR-0093) |
| [runbooks/infra.md](runbooks/infra.md) | One-time setup for the launch: Firebase projects, Google Analytics, deploy credentials, the grievance mailbox |
