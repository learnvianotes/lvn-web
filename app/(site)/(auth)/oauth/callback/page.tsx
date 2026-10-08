import type { Metadata } from 'next'
import { Suspense } from 'react'
import { OAuthCallback } from '@/components/auth/OAuthCallback'

export const metadata: Metadata = { title: 'Signing in', robots: { index: false } }

export default function OAuthCallbackPage() {
  return (
    <Suspense>
      <OAuthCallback />
    </Suspense>
  )
}
