import { z } from 'zod'

/**
 * Every environment variable the web app reads, validated once at start-up (section 16.1). URLs have no
 * defaults: they come from .env / .env.local here and from the hosting environment in sandbox and production
 * (lvn-backend ADR-0022). Interim home until `@lvn/contracts/config` is published — see lvn-backend ADR-0003.
 * It mirrors `webConfigSchema` there.
 * Only NEXT_PUBLIC_* values may be read in client components.
 */
const schema = z.object({
  NEXT_PUBLIC_APP_ENV: z.enum(['development', 'sandbox', 'production']).default('development'),
  NEXT_PUBLIC_SITE_URL: z.url(),
  /** /core feedback reports (core-app/src/config.ts reads it directly); empty disables sending. */
  NEXT_PUBLIC_FEEDBACK_URL: z.union([z.url(), z.literal('')]).optional(),
})

const parsed = schema.safeParse({
  NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV,
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
  NEXT_PUBLIC_FEEDBACK_URL: process.env.NEXT_PUBLIC_FEEDBACK_URL,
})

if (!parsed.success) {
  throw new Error(`Invalid environment:\n${z.prettifyError(parsed.error)}`)
}

export const env = parsed.data
