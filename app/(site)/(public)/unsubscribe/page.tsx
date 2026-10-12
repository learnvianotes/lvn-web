import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Unsubscribe } from '@/features/settings/Unsubscribe'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('settings'))('unsubscribeTitle'), robots: { index: false } }
}

export default async function UnsubscribePage({ searchParams }: { searchParams: Promise<{ t?: string }> }) {
  return <Unsubscribe token={(await searchParams).t ?? ''} />
}
