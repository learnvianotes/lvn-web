import type { Metadata } from 'next'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Licence } from '@/features/legal/Licence'

export const metadata: Metadata = { title: LEGAL_DOCUMENTS.licence.title }

export default function Page() {
  return (
    <LegalPage doc="licence">
      <Licence />
    </LegalPage>
  )
}
