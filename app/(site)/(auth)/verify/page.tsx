import type { Metadata } from 'next'
import { Suspense } from 'react'
import { VerifyPanel } from '@/components/auth/VerifyPanel'

export const metadata: Metadata = { title: 'Verify', robots: { index: false } }

export default function VerifyPage() {
  return (
    <Suspense>
      <VerifyPanel />
    </Suspense>
  )
}
