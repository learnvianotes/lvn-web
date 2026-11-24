import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminUsers } from '@/features/admin/AdminUsers'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminUsers'))('title'), robots: { index: false } }
}

/** Search, correct, block, or delete accounts. Platform admins only. */
export default function UsersPage() {
  return <AdminUsers />
}
