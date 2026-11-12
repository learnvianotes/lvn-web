import type { Metadata } from 'next'
import { AccountDeletionPage } from '@/features/legal/AccountDeletionPage'

export const metadata: Metadata = {
  title: 'Delete your account',
  description: 'How to delete a LearnViaNotes account, a note or an upload, what is removed, and what is kept.',
  alternates: { canonical: '/delete-account' },
}

/** Public. Google Play’s data-deletion URL points here. No sign-in. */
export default function Page() {
  return <AccountDeletionPage />
}
