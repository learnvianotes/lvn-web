import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { CommunityPage } from '@/features/feeds/CommunityPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('community'))('title'), robots: { index: false } }
}

export default function Community() {
  return <CommunityPage />
}
