import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminRoles } from '@/features/admin/AdminRoles'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminRoles'))('title'), robots: { index: false } }
}

/** Assign or remove the manager and teacher roles. Platform admins only. */
export default function RolesPage() {
  return <AdminRoles />
}
