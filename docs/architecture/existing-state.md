# Existing state — Phase 0 inventory

Date: 2026-10-08 · Repository: `learnvianotes` (becomes **lvn-web**) · Branch: `platform/v2-rewrite`

The architecture spec ([lvn-architecture-v2.md](lvn-architecture-v2.md), section 3) asks Phase 0 to record what already
exists and whether it is **kept**, **migrated** or **deleted**. Nothing below is rewritten blindly: the old code stays
on `main` and in git history; this branch is the clean rewrite.

## What existed

### `main` — the live site (learnvianotes.in)

A Vite + React 19 single-page app on Firebase (Auth, Firestore, Cloud Functions), installable as a PWA.

| Area | Path on `main` | Decision | Why / where it went |
| --- | --- | --- | --- |
| Study content, authoring sources | `content-src/` | **Kept, unchanged** | The subject notes are the product's existing value. Python authoring kits still build them. |
| Study content, built output | `content-build/` (catalog + 757 topics + 150 problems, ~10 MB JSON) | **Kept, unchanged** | Read at build time by the new `/core` pages (ADR-0002). |
| Content pipeline | `scripts/content/{extract,sanitize,check-code,validate-code,compile-java,config}.mjs` | **Kept, unchanged** | Still produces `content-build/`. Exposed as `pnpm content:*`. |
| Firestore seeder | `scripts/content/seed/` | **Deleted** | Wrote content into Firestore; v2 has no Firestore. Subjects/Topics move to Postgres (`notes` context) in Phase 2. |
| Web app | `src/`, `index.html`, `vite.config.ts`, `tsconfig*.json`, `eslint.config.js` | **Deleted** (rewritten) | Replaced by the Next.js 15 app (section 12). Reading pages are re-implemented under `/core`. |
| Sign-in, sync, history, streaks, focus timer, read-aloud, study kit, help centre, personal notes | `src/features/{auth,progress,focus,voice,study/kit,help,settings}` | **Deleted** | Accounts and learner data are owned by the backend from Phase 1 (section 7); learning features return in Phases 2–6 on the new model. Old routes redirect to `/` (see `next.config.ts`). |
| Firestore rules, indexes, Cloud Functions, Firebase config | `firestore.*`, `functions/`, `firebase.json`, `.firebaserc` | **Deleted** | v2 pins NestJS + Postgres (section 2). Production Firebase resources are untouched until cut-over (see "Cut-over" below). |
| Firestore document schema | `schema/` | **Deleted** | Replaced by Zod schemas for `content-build/` (`features/core-content/schema.ts`) and, later, `@lvn/contracts`. |
| Old docs | `docs/*.md` | **Deleted** | Described the Firebase app; still readable on `main`. |
| Icons, branding | `public/icons/`, `branding/` | **Kept** | Same brand. |
| Search Console verification | `public/google2985af6e32e281ab.html` | **Kept** | Domain verification. |
| Hosting configs | `vercel.json`, `public/_redirects`, `public/_headers` | **Deleted** | Security headers and redirects now live in `next.config.ts`. |

### `origin/platform/monorepo-foundation` — earlier platform attempt (last commit 2026-09-29, 56 commits)

npm-workspaces monorepo: `apps/legacy-web` (the Vite app), `apps/web` (Next.js 16), `apps/mobile` (**Flutter**),
`packages/{analytics,content,design-tokens,i18n}`, plus docs (`TRACKER.md`, `HANDOFF.md`, `FIREBASE_SETUP.md`).

| Item | Decision | Why |
| --- | --- | --- |
| Monorepo layout | **Not carried over** | v2 pins three repositories (section 2, 3). |
| Flutter mobile app | **Not carried over** | v2 pins Expo (section 2). Its screens, copy and i18n strings (en/hi/te) are a reference for `lvn-mobile`. |
| Next.js 16 web app | **Not carried over** | v2 pins Next.js 15. |
| Firebase-auth gateway design | **Superseded** | v2 pins backend-issued JWT + rotating refresh tokens (section 7). |
| `packages/design-tokens`, `packages/i18n` | **Reference only** | Re-evaluate when building the design system and `next-intl` messages; nothing imported. |

The branch is left as-is on the remote for reference. Delete it once `lvn-mobile` has reviewed it.

## What this branch contains now

See [web-addendum.md](web-addendum.md) for the route map and how lvn-web implements section 12.

- Next.js 15 (App Router) + React 19 + Tailwind 4 + shadcn-style primitives + Zustand (theme store) + next-intl (English).
- `/` landing page and `/core/*` — every existing subject, topic and problem sheet, statically generated (805 pages).
- 301 redirects from the old root URLs (`/<subject>/<topic>`) to `/core/<subject>/<topic>`.
- `public/sw.js` removes the old PWA service worker from returning visitors' browsers.
- Vitest unit tests, Playwright E2E (desktop + phone) with axe accessibility checks, GitHub Actions CI, Dependabot.

## Not yet started (other repositories)

| Repository | Phase 0 items still open |
| --- | --- |
| `lvn-backend` | Create the repo; pnpm + Turborepo; GraphQL schema skeleton; permission matrix and domain enums in `@lvn/contracts/domain`; `@lvn/contracts/config`; CI that builds an empty api + worker. |
| `lvn-mobile` | Create the Expo repo with the three EAS profiles; CI. |

## Cut-over from the old site

The old site keeps running on Firebase Hosting at learnvianotes.in until this app is deployed to learnvianotes.com.
At cut-over:

1. Point learnvianotes.in at the new deployment (or 301 the whole domain to learnvianotes.com).
2. Keep the Firebase project until Phase 1 decides what happens to existing Firebase Auth users and their Firestore
   data (streaks, history, personal notes). **Open question for the owner** — options: import into Postgres in
   Phase 1, or announce a fresh start.
3. Leave `public/sw.js` deployed for at least 6 months so every returning browser drops the old service worker.

## Inconsistencies in the spec to settle before Phase 1

These are wording conflicts inside lvn-architecture-v2.md, not deviations. Each needs a one-line fix in the spec
(or an ADR) before agents rely on it.

| # | Where | Conflict | Suggested resolution |
| --- | --- | --- | --- |
| 1 | §0 | Role briefs reference "sections 13, 14 or 7–12", but web is §12 and mobile is §13; §14 is learning events. | Web brief = §12, Mobile = §13, Backend = §6–11, 14. |
| 2 | §18 Phase 0/1 | "empty monorepo builds", "Monorepo, `packages/config`" — contradicts three repos and `@lvn/contracts/config` (§2, §3). | Read as "three repos build"; config lives in `@lvn/contracts/config`. |
| 3 | §10.1 | Prompts in `apps/api/src/modules/ai/prompts/` — contradicts the `contexts/ai/` layout (§3). | `contexts/ai/prompts/`. |
| 4 | §12 | "It owns `apps/web` only"; §13 "owns `apps/mobile`" — paths from the monorepo era. | The `lvn-web` / `lvn-mobile` repositories. |
| 5 | §1 | Domain is learnvianotes.com; the live site is learnvianotes.in. | Confirm learnvianotes.com is registered; plan the .in → .com redirect. |
| 6 | §1 vs §2 | Admin, college and company platforms listed with domains, but §1 also says "Two applications". | "Student platform now; three separate apps later". |
| 7 | §1 changelog | "Problems" removed from scope, but the existing Sheet 150 problem set is live content. | Kept read-only under `/core` (ADR-0002); no new problem features. |
| 8 | §8 | Subsection order 8.1, 8.3, 8.2. | Renumber. |
| 9 | §13.1 | Production bundle id renders as an empty code span. | `com.learnvianotes`. |
| 10 | §2 Mobile | Expo SDK 52+ — current SDK is newer; Next.js 15 is pinned while 16 is current. | Keep pins as written; revisit by ADR when an upgrade is needed. |
