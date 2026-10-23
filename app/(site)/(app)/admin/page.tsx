import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminOverview } from '@/features/admin/AdminOverview'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminOverview'))('title'), robots: { index: false } }
}

/** Platform-admin overview: people, content, AI usage, storage, verification and moderation. */
export default function AdminOverviewPage() {
  return <AdminOverview />
}
