# ADR-0004: Phase 0 documents start in lvn-web

- Status: Accepted
- Date: 2026-10-08
- Spec sections: §3, §18 (Phase 0)

## Context

§3 places `docs/` (architecture, adr, api-changes, runbooks, releases) in lvn-backend. Phase 0 starts in the only
repository that exists today, this one (which becomes lvn-web).

## Decision

Phase 0 documents are written here under the same folder structure. When lvn-backend is created, `docs/architecture/`
(except `web-addendum.md`), `docs/adr/`, `docs/api-changes/`, `docs/runbooks/` and `docs/releases/` move there with
history (`git filter-repo` or a subtree split), and this repo keeps `web-addendum.md` plus a pointer README.

## Consequences

Agents read one copy of the spec. The move is a single, mechanical PR at the start of Phase 1.
