import { legacyDataPaths, legacyDocument } from '@core-server/content'
import { env } from '@/lib/env'

/**
 * The old site's content documents as static JSON (core-app/src/features/catalog/staticSource.ts reads them).
 * Every path is generated at build time; anything else is a 404.
 */
export const dynamic = 'force-static'
export const dynamicParams = false

export function generateStaticParams() {
  // Off unless NEXT_PUBLIC_CORE_ENABLED is true (owner, 2026-10-14): then no document is served.
  return env.NEXT_PUBLIC_CORE_ENABLED ? legacyDataPaths().map((p) => ({ path: p.split('/') })) : []
}

export async function GET(_request: Request, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params
  const doc = legacyDocument(path.join('/'))
  if (!doc) return new Response('Not found', { status: 404 })
  return Response.json(doc)
}
