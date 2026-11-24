import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminAccess } from '@/features/admin/AdminAccess'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminAccess'))('title'), robots: { index: false } }
}

/** Emails allowed to sign in while the beta allowlist is on. */
export default function AdminAccessPage() {
  return <AdminAccess />
}
