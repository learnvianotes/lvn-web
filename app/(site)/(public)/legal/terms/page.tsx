import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Terms } from '@/features/legal/Terms'

export const metadata: Metadata = legalMetadata('terms')

/** The version label comes from the API, which an admin can change (features/legal/terms-version.ts). */
export const revalidate = 60

export default function Page() {
  return (
    <LegalPage doc="terms">
      <Terms />
    </LegalPage>
  )
}
