import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { CoreApp } from '@core/app/CoreApp'
import { pageInfo } from '@core/app/title'
import { legacyCatalog } from '@core-server/content'

/**
 * Every /core page is the old site's app (core-app/), which routes in the browser exactly as before.
 * Each path is still generated here so it has its own title, description and canonical URL. Any other
 * path is a 404 that shows the old app's own "not found" page (../not-found.tsx).
 */
function corePaths(): string[][] {
  return [
    [],
    ['about'],
    ...legacyCatalog().subjects.flatMap((s) => [[s.id], ...s.topics.map((t) => [s.id, t.id])]),
  ]
}

let known: Set<string> | undefined
const isCorePath = (slug: string[]) => (known ??= new Set(corePaths().map((p) => p.join('/')))).has(slug.join('/'))

export function generateStaticParams(): { slug: string[] }[] {
  return corePaths().map((slug) => ({ slug }))
}

export async function generateMetadata({ params }: { params: Promise<{ slug?: string[] }> }): Promise<Metadata> {
  const { slug = [] } = await params
  if (!isCorePath(slug)) return {}
  const { title, description } = pageInfo(legacyCatalog(), slug)
  const url = `/core${slug.length ? `/${slug.join('/')}` : ''}`
  return {
    title: { absolute: title },
    description,
    alternates: { canonical: url },
    openGraph: { title, description, url, type: slug.length > 1 ? 'article' : 'website' },
  }
}

export default async function CorePage({ params }: { params: Promise<{ slug?: string[] }> }) {
  const { slug = [] } = await params
  if (!isCorePath(slug)) notFound()
  return <CoreApp />
}
