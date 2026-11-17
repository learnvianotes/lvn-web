import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { AdminContent } from '@/features/admin/AdminContent'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminContent'))('title'), robots: { index: false } }
}

/** Browse content that is not private. Platform admins only. */
export default function ContentPage() {
  return (
    <Suspense>
      <AdminContent />
    </Suspense>
  )
}
