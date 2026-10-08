import type { MetadataRoute } from 'next'
import { getCatalog } from '@/features/core-content/source'
import { listPublicNotes } from '@/features/public-notes/data'
import { publicNotePath } from '@/features/public-notes/paths'
import { env } from '@/lib/env'

/** The sitemap is rebuilt with the public notes list (tag `public-notes`), at most hourly. */
export const revalidate = 3600

/** Static pages, /core, and public notes (/n/[slug]-[id]) from the API; without the API the rest still ships. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = env.NEXT_PUBLIC_SITE_URL
  const catalog = getCatalog()
  const lastModified = new Date(catalog.generatedAt)
  const notes = await listPublicNotes().catch(() => [])
  return [
    { url: `${base}/`, lastModified },
    { url: `${base}/core`, lastModified },
    { url: `${base}/core/about`, lastModified },
    ...catalog.subjects.flatMap((s) => [
      { url: `${base}/core/${s.id}`, lastModified },
      ...s.topics.map((t) => ({ url: `${base}/core/${s.id}/${t.id}`, lastModified })),
    ]),
    ...notes.map((n) => ({ url: `${base}${publicNotePath(n)}`, ...(n.publishedAt ? { lastModified: new Date(n.publishedAt) } : {}) })),
  ]
}
