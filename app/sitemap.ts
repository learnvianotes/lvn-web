import type { MetadataRoute } from 'next'
import { getCatalog } from '@/features/core-content/source'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'
import { listPublicNotes } from '@/features/public-notes/data'
import { publicNotePath } from '@/features/public-notes/paths'
import { listSubjects } from '@/features/subjects/data'
import { env } from '@/lib/env'

/**
 * Built on request, never at build time (the API is not there while images build); the public notes list it reads is
 * cached for an hour and dropped when the API says it changed (tag `public-notes`).
 */
export const dynamic = 'force-dynamic'

/**
 * Static pages (the landing page, subjects, resources and the legal pages), the subjects and their topics, and public
 * notes (/n/[slug]-[id]) from the API; /core only while the old notes are on (owner, 2026-10-14). Without the API the
 * rest still ships. Every address here answers 200; anything else on the site answers 404.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = env.NEXT_PUBLIC_SITE_URL
  const [notes, subjects] = await Promise.all([listPublicNotes().catch(() => []), listSubjects().catch(() => [])])
  const core = env.NEXT_PUBLIC_CORE_ENABLED ? getCatalog() : null
  return [
    { url: `${base}/` },
    { url: `${base}/subjects` },
    { url: `${base}/resources` },
    ...Object.values(LEGAL_DOCUMENTS).map((d) => ({ url: `${base}${d.path}` })),
    ...subjects.flatMap((s) => [{ url: `${base}/subjects/${s.slug}` }, ...s.topics.flatMap((t) => [t, ...t.children]).map((t) => ({ url: `${base}/subjects/${s.slug}/${t.slug}` }))]),
    ...(core
      ? [
          { url: `${base}/core`, lastModified: new Date(core.generatedAt) },
          { url: `${base}/core/about`, lastModified: new Date(core.generatedAt) },
          ...core.subjects.flatMap((s) => [{ url: `${base}/core/${s.id}` }, ...s.topics.map((t) => ({ url: `${base}/core/${s.id}/${t.id}` }))]),
        ]
      : []),
    ...notes.map((n) => ({ url: `${base}${publicNotePath(n)}`, ...(n.publishedAt ? { lastModified: new Date(n.publishedAt) } : {}) })),
  ]
}
