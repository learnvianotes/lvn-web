import type { Metadata } from 'next'

/**
 * The legal documents people accept (lvn-backend §15.2). One version covers all three; it must equal the API's
 * TERMS_VERSION (contexts/users/src/domain/rules.ts), and changing it asks every signed-in person to accept again.
 */
export const TERMS_VERSION = '2026-11-03'

export type LegalDocument = 'terms' | 'privacy' | 'licence' | 'grievance'

/** Every legal page: its address, title and the description search engines and link previews show. */
export const LEGAL_DOCUMENTS: Record<LegalDocument, { title: string; path: string; description: string }> = {
  terms: {
    title: 'Terms of Service',
    path: '/legal/terms',
    description: 'The rules for using LearnViaNotes: who can have an account, your notes, community rules, moderation and our responsibilities.',
  },
  privacy: {
    title: 'Privacy Policy',
    path: '/legal/privacy',
    description: 'What LearnViaNotes collects, why, who processes it, how long it is kept and how to use your rights.',
  },
  licence: {
    title: 'Content licence',
    path: '/legal/content-licence',
    description: 'What you allow LearnViaNotes to do with notes you share or make public, and what others may do with them.',
  },
  grievance: {
    title: 'Grievance Redressal',
    path: '/legal/grievance',
    description: 'How to raise a complaint with the LearnViaNotes Grievance Officer, and how quickly we respond.',
  },
}

/** The documents people accept at sign-up and again when they change; the Grievance page explains, it is not accepted. */
export const ACCEPTED_DOCUMENTS: LegalDocument[] = ['terms', 'privacy', 'licence']

/** A legal page's title, description and canonical address (relative to the site's metadataBase). */
export function legalMetadata(doc: LegalDocument): Metadata {
  const { title, description, path } = LEGAL_DOCUMENTS[doc]
  return { title, description, alternates: { canonical: path } }
}
