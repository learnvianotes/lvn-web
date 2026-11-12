/** The secret /api/revalidate expects in Playwright runs (playwright.config.ts sets it; public-notes.spec.ts sends it). */
export const E2E_REVALIDATE_SECRET = 'e2e-revalidate-secret-0123456789abcdef'
/** Full git SHA baked into the e2e build. /version reports the first 12 characters, as deploy.yml does. */
export const E2E_GIT_SHA = '0123456789abcdef0123456789abcdef01234567'
/** Where the e2e build looks for live updates (lvn-backend ADR-0042): nothing listens there unless a test routes it. */
export const LIVE_URL = 'ws://127.0.0.1:9/graphql/live'
