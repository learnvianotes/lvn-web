import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminSettings } from '@/features/admin/AdminSettings'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminSettings'))('title'), robots: { index: false } }
}

/** Platform configuration, one control per setting (lvn-backend contracts 0.68.0). */
export default function AdminSettingsPage() {
  return <AdminSettings />
}
