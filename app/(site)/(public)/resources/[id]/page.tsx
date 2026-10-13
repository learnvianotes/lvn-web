import type { Metadata } from 'next'
import { ResourcePage } from '@/features/resources/ResourceView'

/** Out of search engines until people have saved it (lvn-backend ADR-0074; the saves arrive with the catalogue). */
export const metadata: Metadata = { title: 'Resource', robots: { index: false, follow: false } }

/** A resource: public once moderators approved it; its submitter sees it while it waits. */
export default async function ResourceRoute({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <ResourcePage id={id} />
}
