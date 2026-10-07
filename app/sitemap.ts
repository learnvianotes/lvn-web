import type { MetadataRoute } from 'next'
import { getCatalog } from '@/features/core-content/source'
import { env } from '@/lib/env'

/** Static pages + /core today; public notes (/n/[slug]-[id]) are added from the API in Phase 2. */
export default function sitemap(): MetadataRoute.Sitemap {
  const base = env.NEXT_PUBLIC_SITE_URL
  const catalog = getCatalog()
  const lastModified = new Date(catalog.generatedAt)
  return [
    { url: `${base}/`, lastModified },
    { url: `${base}/core`, lastModified },
    ...catalog.subjects.flatMap((s) => [
      { url: `${base}/core/${s.id}`, lastModified },
      ...s.topics.map((t) => ({ url: `${base}/core/${s.id}/${t.id}`, lastModified })),
    ]),
  ]
}
