import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminErrors } from '@/features/admin/AdminErrors'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminErrors'))('title'), robots: { index: false } }
}

/** Platform errors grouped by type, with the people who hit each one. */
export default function ErrorsPage() {
  return <AdminErrors />
}
