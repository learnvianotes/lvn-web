# Phase 0 — Architecture (in progress)

Branch: `platform/v2-rewrite` · Spec: [lvn-architecture-v2.md](../architecture/lvn-architecture-v2.md) §18

## Shipped in lvn-web

| Item | Where |
| --- | --- |
| Spec saved as the single source of truth | `docs/architecture/lvn-architecture-v2.md` |
| Existing-state inventory (kept / migrated / deleted) + spec inconsistencies | `docs/architecture/existing-state.md` |
| Web addendum (route map, folder map, budgets) | `docs/architecture/web-addendum.md` |
| ERD draft (per context, Mermaid) | `docs/architecture/erd.md` |
| Env reference | `docs/architecture/env.md`, `.env.example` |
| ADR-0001 … ADR-0004 | `docs/adr/` |
| Next.js 15 app skeleton per §12.1, landing page | `app/`, `components/`, `lib/`, `state/` |
| Existing study content at `/core` (ADR-0002), redirects from old URLs, old service worker removed | `app/(public)/core/`, `features/core-content/`, `next.config.ts`, `public/sw.js` |
| CI: lint, typecheck, unit, build, E2E, gitleaks, audit; Dependabot | `.github/` |

## Test evidence (2026-10-08, local)

- `pnpm lint`, `pnpm typecheck`: clean.
- `pnpm test`: 7 unit tests pass (renderer, grouping).
- `pnpm build`: 805 static pages; 106 kB first-load JS per route.
- `pnpm test:e2e`: 12/12 pass (6 tests × desktop + Pixel 7), including axe (no serious/critical violations).
- `pnpm audit --prod --audit-level high`: no known vulnerabilities.

## Exit criteria still open

- [ ] lvn-backend created: GraphQL schema skeleton, permission matrix + enums in `@lvn/contracts/domain`, empty
      api + worker build in CI.
- [ ] lvn-mobile created (Expo, three EAS profiles), CI green.
- [ ] Spec inconsistencies in `existing-state.md` resolved.
- [ ] Backend, Web and Mobile agents sign off on the same documents.
- [ ] Decision on existing Firebase users' data (existing-state.md → Cut-over).

GraphQL schema version: none yet.
