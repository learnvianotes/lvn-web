import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { Grievance } from '@/features/legal/Grievance'
import { LegalPage } from '@/features/legal/LegalPage'

export const metadata: Metadata = legalMetadata('grievance')

export default function Page() {
  return (
    <LegalPage doc="grievance">
      <Grievance />
    </LegalPage>
  )
}
