import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { Grievance } from '@/features/legal/Grievance'
import { LegalPage } from '@/features/legal/LegalPage'

export const metadata: Metadata = legalMetadata('grievance')

/** The version label comes from the API, which an admin can change (features/legal/terms-version.ts). */
export const revalidate = 60

export default function Page() {
  return (
    <LegalPage doc="grievance">
      <Grievance />
    </LegalPage>
  )
}
