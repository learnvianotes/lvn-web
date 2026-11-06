import { meetUrlSchema } from '@/lib/contracts/validation/learning'

/** A Meet link this app will open. Anything else is not shown and is not sent. */
export function meetHref(value: string | null | undefined): string | null {
  const parsed = meetUrlSchema.safeParse((value ?? '').trim())
  return parsed.success ? parsed.data : null
}
