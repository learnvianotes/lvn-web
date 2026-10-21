import type { Metadata } from 'next'
import { legalMetadata } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { Privacy } from '@/features/legal/Privacy'

export const metadata: Metadata = legalMetadata('privacy')

export default function Page() {
  return (
    <LegalPage doc="privacy">
      <Privacy />
    </LegalPage>
  )
}
