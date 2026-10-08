import 'server-only'
import { z } from 'zod'
import { env } from './env'

/**
 * Server-only settings (never in client bundles): where server rendering calls the API, and the secret the API's
 * revalidation calls carry (lvn-backend docs/architecture/env.md).
 */
const parsed = z
  .object({
    API_INTERNAL_URL: z.url().optional(),
    REVALIDATE_SECRET: z.string().min(32).optional(),
  })
  .safeParse({ API_INTERNAL_URL: process.env.API_INTERNAL_URL || undefined, REVALIDATE_SECRET: process.env.REVALIDATE_SECRET || undefined })

if (!parsed.success) throw new Error(`Invalid server environment:\n${z.prettifyError(parsed.error)}`)

export const serverEnv = {
  apiUrl: parsed.data.API_INTERNAL_URL ?? env.NEXT_PUBLIC_API_URL,
  revalidateSecret: parsed.data.REVALIDATE_SECRET ?? null,
}
