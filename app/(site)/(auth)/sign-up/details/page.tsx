import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { DetailsForm } from '@/components/auth/DetailsForm'
import { RequireSession } from '@/components/auth/RequireSession'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('auth.details'))('title'), robots: { index: false } }
}

export default function DetailsPage() {
  return (
    <Suspense>
      <RequireSession>
        <DetailsForm />
      </RequireSession>
    </Suspense>
  )
}
