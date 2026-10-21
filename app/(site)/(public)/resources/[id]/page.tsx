import type { Metadata } from 'next'
import { env } from '@/lib/env'
import { getResource, resourceJsonLd } from '@/features/resources/data'
import { ResourcePage } from '@/features/resources/ResourceView'
import { templated } from '@/lib/page-title'

type Props = { params: Promise<{ id: string }> }

/**
 * A resource: public once approved, rendered with its schema.org data; out of search engines until three people saved
 * it (lvn-backend ADR-0074, ADR-0075). Its submitter sees it while it waits, in the browser.
 */
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const r = await getResource((await params).id)
  if (!r) return { title: 'Resource', robots: { index: false, follow: false } }
  const url = `${env.NEXT_PUBLIC_SITE_URL}/resources/${r.id}`
  return {
    title: templated(r.title),
    description: r.description?.slice(0, 160) ?? `${r.title} on LearnViaNotes`,
    alternates: { canonical: url },
    robots: { index: r.indexable, follow: false },
    openGraph: { type: 'website', url, title: r.title, siteName: 'LearnViaNotes', ...(r.description ? { description: r.description.slice(0, 200) } : {}) },
  }
}

export default async function ResourceRoute({ params }: Props) {
  const { id } = await params
  const r = await getResource(id)
  return (
    <>
      {r ? <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(resourceJsonLd(r, `${env.NEXT_PUBLIC_SITE_URL}/resources/${r.id}`)).replace(/</g, '\\u003c') }} /> : null}
      <ResourcePage id={id} />
    </>
  )
}
