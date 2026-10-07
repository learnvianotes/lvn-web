# ADR-0001: Record architecture decisions

- Status: Accepted
- Date: 2026-10-08
- Spec sections: §0, §19

## Context

The architecture spec (`docs/architecture/lvn-architecture-v2.md`) pins every technology and rule. Section 0 says any
deviation needs an accepted ADR before implementation, and §19 says disagreements are settled by ADR, not code.

## Decision

- ADRs live in `docs/adr/NNNN-kebab-title.md`, numbered in order, written from `template.md`.
- An ADR is **Proposed** when opened in a PR and **Accepted** when the owner approves the PR. Agents implement only
  Accepted ADRs.
- ADRs are never edited after acceptance except to change Status to "Superseded by ADR-NNNN".
- The spec itself is changed only by PR; each change notes the ADR that motivated it.
- Until `lvn-backend` exists, ADRs that affect all three repos live here; they move to `lvn-backend/docs/adr/`
  (keeping their numbers) when that repository is created (ADR-0004).

## Consequences

Every decision has one place to look. Small cost per decision; reviewers must reject PRs that deviate from the spec
without an ADR.
