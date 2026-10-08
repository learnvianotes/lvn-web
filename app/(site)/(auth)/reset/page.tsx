import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { ResetPanel } from '@/components/auth/ResetPanel'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('auth.reset'))('title'), robots: { index: false } }
}

export default function ResetPage() {
  return (
    <Suspense>
      <ResetPanel />
    </Suspense>
  )
}
