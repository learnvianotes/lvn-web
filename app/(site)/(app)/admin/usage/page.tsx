import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminUsage } from '@/features/admin/AdminUsage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminUsage'))('title'), robots: { index: false } }
}

/** How many people use the product, which parts they use, and one person's timeline. */
export default function UsagePage() {
  return <AdminUsage />
}
