import type { Metadata } from 'next'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Privacy } from '@/features/legal/Privacy'

export const metadata: Metadata = { title: LEGAL_DOCUMENTS.privacy.title }

export default function Page() {
  return (
    <LegalPage doc="privacy">
      <Privacy />
    </LegalPage>
  )
}
