import { z } from 'zod'

/**
 * Every environment variable the web app reads, validated once at start-up (section 16.1). URLs have no
 * defaults: they come from .env / .env.local here and from the hosting environment in sandbox and production
 * (lvn-backend ADR-0022). Interim home until `@lvn/contracts/config` is published — see lvn-backend ADR-0003.
 * It mirrors `webConfigSchema` there.
 * Only NEXT_PUBLIC_* values may be read in client components.
 */
const optional = z.string().min(1).optional()

const schema = z.object({
  NEXT_PUBLIC_APP_ENV: z.enum(['development', 'sandbox', 'production']).default('development'),
  NEXT_PUBLIC_SITE_URL: z.url(),
  /** The GraphQL endpoint of lvn-backend (its gateway, `/graphql`). */
  NEXT_PUBLIC_API_URL: z.url(),
  /** /core feedback reports (core-app/src/config.ts reads it directly); empty disables sending. */
  NEXT_PUBLIC_FEEDBACK_URL: z.union([z.url(), z.literal('')]).optional(),
  // Google sign-in through Firebase Authentication (lvn-backend ADR-0007). Public identifiers, not secrets.
  NEXT_PUBLIC_FIREBASE_API_KEY: optional,
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: optional,
  NEXT_PUBLIC_FIREBASE_PROJECT_ID: optional,
  NEXT_PUBLIC_FIREBASE_APP_ID: optional,
  // GitHub and LinkedIn sign-in (Authorization Code + PKCE, §7.1): public client ids and the providers' consent pages.
  NEXT_PUBLIC_GITHUB_CLIENT_ID: optional,
  NEXT_PUBLIC_GITHUB_AUTHORIZE_URL: z.url().optional(),
  NEXT_PUBLIC_LINKEDIN_CLIENT_ID: optional,
  NEXT_PUBLIC_LINKEDIN_AUTHORIZE_URL: z.url().optional(),
  /** Sentry for unexpected errors (§16.5); off without it. Read directly by instrumentation*.ts, validated here. */
  NEXT_PUBLIC_SENTRY_DSN: z.url().refine((u) => /^https?:\/\//.test(u), 'must be an http(s) URL').optional(),
})

// Each NEXT_PUBLIC_* is read by its full name so Next can inline it into client bundles. An empty value (as hosts and
// Docker build arguments often pass) means "not set".
const unsetIfEmpty = (raw: Record<string, string | undefined>) => Object.fromEntries(Object.entries(raw).map(([k, v]) => [k, v === '' ? undefined : v]))
const parsed = schema.safeParse(unsetIfEmpty({
  NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV,
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_FEEDBACK_URL: process.env.NEXT_PUBLIC_FEEDBACK_URL,
  NEXT_PUBLIC_FIREBASE_API_KEY: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  NEXT_PUBLIC_FIREBASE_APP_ID: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  NEXT_PUBLIC_GITHUB_CLIENT_ID: process.env.NEXT_PUBLIC_GITHUB_CLIENT_ID,
  NEXT_PUBLIC_GITHUB_AUTHORIZE_URL: process.env.NEXT_PUBLIC_GITHUB_AUTHORIZE_URL,
  NEXT_PUBLIC_LINKEDIN_CLIENT_ID: process.env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID,
  NEXT_PUBLIC_LINKEDIN_AUTHORIZE_URL: process.env.NEXT_PUBLIC_LINKEDIN_AUTHORIZE_URL,
  NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
}))

if (!parsed.success) {
  throw new Error(`Invalid environment:\n${z.prettifyError(parsed.error)}`)
}

export const env = parsed.data

/** Firebase web config for Google sign-in, or null when this deployment has none. */
export const firebaseConfig =
  env.NEXT_PUBLIC_FIREBASE_API_KEY && env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN && env.NEXT_PUBLIC_FIREBASE_PROJECT_ID && env.NEXT_PUBLIC_FIREBASE_APP_ID
    ? { apiKey: env.NEXT_PUBLIC_FIREBASE_API_KEY, authDomain: env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN, projectId: env.NEXT_PUBLIC_FIREBASE_PROJECT_ID, appId: env.NEXT_PUBLIC_FIREBASE_APP_ID }
    : null
