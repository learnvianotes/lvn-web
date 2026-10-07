import { z } from 'zod'

/**
 * Every environment variable the web app reads, validated once at start-up (section 16.1).
 * Interim home until `@lvn/contracts/config` is published by lvn-backend — see lvn-backend docs/adr/0003.
 * It mirrors `webConfigSchema` there.
 * Only NEXT_PUBLIC_* values may be read in client components.
 */
const schema = z.object({
  NEXT_PUBLIC_APP_ENV: z.enum(['development', 'sandbox', 'production']).default('development'),
  NEXT_PUBLIC_SITE_URL: z.url().default('http://localhost:3000'),
})

const parsed = schema.safeParse({
  NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV,
  NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
})

if (!parsed.success) {
  throw new Error(`Invalid environment:\n${z.prettifyError(parsed.error)}`)
}

export const env = parsed.data
