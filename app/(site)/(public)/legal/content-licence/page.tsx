import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Licence } from '@/features/legal/Licence'

export const metadata: Metadata = legalMetadata('licence')

export default function Page() {
  return (
    <LegalPage doc="licence">
      <Licence />
    </LegalPage>
  )
}
