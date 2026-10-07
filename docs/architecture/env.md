# Environment variables

Canonical list (section 16.1). CI fails if code reads a variable that is missing here or from `.env.example`.
Every value is validated with Zod at start-up; a missing or malformed value stops the process.

## lvn-web

Validated in `lib/env.ts` until `@lvn/contracts/config` is published (ADR-0003).

| Variable | Required | Default | Development | Sandbox | Production | Purpose |
| --- | --- | --- | --- | --- | --- | --- |
| `NEXT_PUBLIC_APP_ENV` | yes | `development` | `development` | `sandbox` | `production` | Gates indexing (`robots`, `noindex`) and, later, feature defaults |
| `NEXT_PUBLIC_SITE_URL` | yes | `http://localhost:3000` | `http://localhost:3000` | `https://sandbox.learnvianotes.com` | `https://learnvianotes.com` | Canonical URLs, sitemap, Open Graph |

Added in Phase 1 (names proposed, owned by `@lvn/contracts/config`): `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`,
`NEXT_PUBLIC_SENTRY_DSN`, `REVALIDATE_SECRET` (server-only, for the API's on-demand ISR webhook).

## lvn-backend and lvn-mobile

Defined by those repositories in Phase 1 and listed here when `@lvn/contracts/config` is published. Secrets are
never listed with values; sandbox and production read them from AWS Secrets Manager.
