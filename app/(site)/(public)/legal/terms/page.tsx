import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Terms } from '@/features/legal/Terms'

export const metadata: Metadata = legalMetadata('terms')

export default function Page() {
  return (
    <LegalPage doc="terms">
      <Terms />
    </LegalPage>
  )
}
