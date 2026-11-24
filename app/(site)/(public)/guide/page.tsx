import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { GuidePage } from '@/features/guide/GuidePage'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('guide')
  return { title: t('title'), description: t('description'), alternates: { canonical: '/guide' } }
}

/** Public map of what the app can do today, linked from the header, the sidebar and the footer. */
export default function Page() {
  return <GuidePage />
}
