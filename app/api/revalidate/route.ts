import { timingSafeEqual } from 'node:crypto'
import { revalidateTag } from 'next/cache'
import { serverEnv } from '@/lib/server-env'

/**
 * On-demand revalidation (P2d): the API calls this when what the public can read of a note changes, with the shared
 * REVALIDATE_SECRET. Only the tags public pages use are accepted.
 */
const TAG = /^(note:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|public-notes)$/

const same = (a: string, b: string) => a.length === b.length && timingSafeEqual(Buffer.from(a), Buffer.from(b))

export async function POST(request: Request) {
  const secret = serverEnv.revalidateSecret
  if (!secret) return Response.json({ error: 'revalidation is not configured' }, { status: 404 })
  if (!same(request.headers.get('x-revalidate-secret') ?? '', secret)) return Response.json({ error: 'forbidden' }, { status: 401 })
  const body = (await request.json().catch(() => null)) as { tags?: unknown } | null
  const tags = Array.isArray(body?.tags) ? body.tags : []
  if (!tags.length || tags.length > 20 || !tags.every((t): t is string => typeof t === 'string' && TAG.test(t))) {
    return Response.json({ error: 'tags must be note:<id> or public-notes' }, { status: 400 })
  }
  for (const tag of tags) revalidateTag(tag)
  return Response.json({ revalidated: tags })
}
