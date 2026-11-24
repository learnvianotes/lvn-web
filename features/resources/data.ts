import 'server-only'
import { print } from 'graphql'
import { cache } from 'react'
import { PublicResourceDocument, SitemapResourcesDocument } from '@/graphql/generated/graphql'
import { serverEnv } from '@/lib/server-env'

/**
 * A resource as anyone sees it (lvn-backend ADR-0074, ADR-0075), read anonymously on the server for its page's metadata
 * and schema.org data: approved resources only (anything else is null to a guest).
 */
export interface PublicResource {
  id: string
  type: 'BOOK' | 'COURSE' | 'TOOL' | 'SOFTWARE' | 'HARDWARE' | 'OTHER'
  title: string
  description: string | null
  url: string
  author: string | null
  isbn: string | null
  saveCount: number
  indexable: boolean
  createdAt: string
}

const QUERY = print(PublicResourceDocument)
const SITEMAP = print(SitemapResourcesDocument)

type SitemapAnswer = {
  resources: { edges: { node: { id: string; indexable: boolean } }[]; pageInfo: { hasNextPage: boolean; endCursor: string | null } }
}

/** Approved resources search engines may index, for sitemap.xml. Guests can read this list. */
export async function listIndexableResources(limit = 5_000): Promise<{ id: string }[]> {
  const out: { id: string }[] = []
  let after: string | null = null
  do {
    const res = await fetch(serverEnv.apiUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ query: SITEMAP, variables: { after } }),
      next: { revalidate: 300, tags: ['resources'] },
      signal: AbortSignal.timeout(5_000),
    })
    if (!res.ok) throw new Error(`API answered HTTP ${res.status}`)
    const body = (await res.json()) as { data?: SitemapAnswer; errors?: { message: string }[] }
    if (body.errors?.length || !body.data) throw new Error(`API error: ${body.errors?.[0]?.message ?? 'no data'}`)
    out.push(...body.data.resources.edges.map((e) => e.node).filter((n) => n.indexable).map((n) => ({ id: n.id })))
    after = body.data.resources.pageInfo.hasNextPage ? body.data.resources.pageInfo.endCursor : null
  } while (after && out.length < limit)
  return out.slice(0, limit)
}

export const getResource = cache(async (id: string): Promise<PublicResource | null> => {
  if (!/^[0-9a-f-]{36}$/i.test(id)) return null
  try {
    const res = await fetch(serverEnv.apiUrl, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ query: QUERY, variables: { id } }), next: { revalidate: 300, tags: [`resource:${id}`] }, signal: AbortSignal.timeout(5_000) })
    if (!res.ok) return null
    const body = (await res.json()) as { data?: { resource: PublicResource | null } }
    return body.data?.resource ?? null
  } catch {
    return null
  }
})

const SCHEMA_TYPE: Record<PublicResource['type'], string> = { BOOK: 'Book', COURSE: 'Course', TOOL: 'SoftwareApplication', SOFTWARE: 'SoftwareApplication', HARDWARE: 'CreativeWork', OTHER: 'CreativeWork' }

/** schema.org data for the page: what it is, by whom, where; never offers or prices (ADR-0074, no commerce). */
export function resourceJsonLd(r: PublicResource, pageUrl: string) {
  const type = SCHEMA_TYPE[r.type]
  return {
    '@context': 'https://schema.org',
    '@type': type,
    name: r.title,
    ...(r.description ? { description: r.description } : {}),
    url: pageUrl,
    sameAs: r.url,
    ...(r.author ? { [type === 'Course' ? 'provider' : 'author']: { '@type': type === 'Course' ? 'Organization' : 'Person', name: r.author } } : {}),
    ...(r.isbn ? { isbn: r.isbn } : {}),
    ...(type === 'SoftwareApplication' ? { applicationCategory: 'EducationalApplication' } : {}),
    interactionStatistic: { '@type': 'InteractionCounter', interactionType: 'https://schema.org/BookmarkAction', userInteractionCount: r.saveCount },
  }
}
