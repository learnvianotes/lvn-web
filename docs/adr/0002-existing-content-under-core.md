# ADR-0002: Serve the existing study content at /core

- Status: Accepted
- Date: 2026-10-08
- Spec sections: §1, §3 ("Nothing is rewritten blindly"), §12.1, §18

## Context

learnvianotes.in today serves 22 subjects (757 topics, 150 interview problems) written and verified over months.
The v2 spec rewrites the product as a community of user notes; its route map (§12.1) has no place for curated
subject notes until the `notes` context owns Subjects and Topics in Phase 2, and "Problems" is removed from scope.
Dropping the content during the rewrite would lose search traffic and the reason students visit today.

The owner asked for the existing pages to move to `learnvianotes.com/core/*` and for the app itself to be a
complete rewrite, without the old sign-in features.

## Decision

- The rewritten Next.js app serves the existing content read-only at `/core`, `/core/[subjectId]` and
  `/core/[subjectId]/[itemId]`, statically generated at build time from `content-build/` (unchanged).
- The old app's code is **not** reused; rendering is re-implemented (`features/core-content/`). No sign-in, progress,
  history, notes, read-aloud or focus timer under `/core`.
- Sheet 150 stays as read-only content. No new problem features are built (respects "Problems removed from scope").
- Old root URLs redirect permanently: `/<subject>/<item>` → `/core/<subject>/<item>`.
- `content-src/`, `content-build/` and the extraction scripts stay in this repo until Phase 2.

## Consequences

- Existing readers and search rankings carry over with one redirect hop.
- `/core` adds ~800 static pages to every web build (~10 s today).
- **Phase 2 follow-up:** when `notes` owns Subject/Topic, import `content-build/` into Postgres as curated topics,
  switch `features/core-content/source.ts` to GraphQL, and move the authoring kit to lvn-backend (seed data) or its
  own repo. A new ADR decides whether curated content becomes PUBLIC notes owned by an LVN account.
