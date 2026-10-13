import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { env } from '@/lib/env'
import { Catalogue } from '@/features/resources/Catalogue'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('resources.catalogue')
  return { title: t('title'), description: t('lead'), alternates: { canonical: `${env.NEXT_PUBLIC_SITE_URL}/resources` } }
}

/** The catalogue of resources people added and moderators approved (lvn-backend ADR-0075); guests browse it too. */
export default function ResourcesRoute() {
  return <Catalogue />
}
