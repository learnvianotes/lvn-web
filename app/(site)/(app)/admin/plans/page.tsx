import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminPlans } from '@/features/admin/AdminPlans'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminPlans'))('title'), robots: { index: false } }
}

/** Plans and what they cost. Saving a price charges nobody. */
export default function AdminPlansPage() {
  return <AdminPlans />
}
