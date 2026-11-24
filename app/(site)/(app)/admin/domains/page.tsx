import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminDomains } from '@/features/admin/AdminDomains'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminDomains'))('title'), robots: { index: false } }
}

/** Institution email domains waiting for approval. Platform admins only. */
export default function DomainsPage() {
  return <AdminDomains />
}
