/**
 * The legal documents people accept (lvn-backend §15.2). One version covers all three; it must equal the API's
 * TERMS_VERSION (contexts/users/src/domain/rules.ts), and changing it asks every signed-in person to accept again.
 */
export const TERMS_VERSION = '2026-10-08'

export type LegalDocument = 'terms' | 'privacy' | 'licence'

export const LEGAL_DOCUMENTS: Record<LegalDocument, { title: string; path: string }> = {
  terms: { title: 'Terms of Service', path: '/legal/terms' },
  privacy: { title: 'Privacy Policy', path: '/legal/privacy' },
  licence: { title: 'Content licence', path: '/legal/content-licence' },
}
