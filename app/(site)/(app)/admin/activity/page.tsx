import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { AdminActivity } from '@/features/admin/AdminActivity'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminActivity'))('title'), robots: { index: false } }
}

/** What admins changed, newest first, with a summary of the selected range. */
export default function ActivityPage() {
  return (
    <Suspense>
      <AdminActivity />
    </Suspense>
  )
}
