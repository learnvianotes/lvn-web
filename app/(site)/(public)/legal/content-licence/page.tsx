import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Licence } from '@/features/legal/Licence'

export const metadata: Metadata = legalMetadata('licence')

/** The version label comes from the API, which an admin can change (features/legal/terms-version.ts). */
export const revalidate = 60

export default function Page() {
  return (
    <LegalPage doc="licence">
      <Licence />
    </LegalPage>
  )
}
