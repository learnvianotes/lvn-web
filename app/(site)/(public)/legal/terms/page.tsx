import type { Metadata } from 'next'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Terms } from '@/features/legal/Terms'

export const metadata: Metadata = { title: LEGAL_DOCUMENTS.terms.title }

export default function Page() {
  return (
    <LegalPage doc="terms">
      <Terms />
    </LegalPage>
  )
}
