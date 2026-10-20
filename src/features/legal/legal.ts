/* ============================================================
   LEGAL — the facts the Privacy Policy, Terms and Grievance
   pages are built from (operator, contact, dates). The values
   live in src/config.ts → LEGAL; a production build refuses to
   run while any of them is blank (build/launch-checks.ts).
   ============================================================ */

import { LEGAL } from '@/config'

export type LegalField = Exclude<keyof typeof LEGAL, 'effective'>

/** What each field is called where it's missing (pages, build check). */
export const LEGAL_FIELD_LABELS: Record<LegalField, string> = {
  operator: 'operator’s legal name',
  address: 'postal address',
  courtsCity: 'city for disputes',
  grievanceOfficer: 'Grievance Officer’s name',
  email: 'grievance email',
}

export function missingLegalFields(values: Record<LegalField, string> = LEGAL): LegalField[] {
  return (Object.keys(LEGAL_FIELD_LABELS) as LegalField[]).filter((k) => !values[k].trim())
}

/** "22 October 2026" — legal pages spell dates out, so no reader misreads 10/11. */
export function formatLegalDate(iso: string): string {
  const d = new Date(`${iso}T00:00:00Z`)
  return new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(d)
}

/** The version a learner accepts at sign-up (stored with their account). */
export const TERMS_VERSION = LEGAL.effective

export type LegalDoc = 'privacy' | 'terms' | 'grievance'

/** Path and title of each legal page (the router, links and the build's page list read these). */
export const LEGAL_PAGES: Record<LegalDoc, { path: string; title: string; description: string }> = {
  privacy: {
    path: '/privacy',
    title: 'Privacy Policy',
    description: 'What LearnViaNotes collects, why, who processes it, how long it is kept and how to use your rights.',
  },
  terms: {
    path: '/terms',
    title: 'Terms of Use',
    description: 'The rules for using LearnViaNotes: who can have an account, what you may do with the notes, and our responsibilities.',
  },
  grievance: {
    path: '/grievance',
    title: 'Grievance Redressal',
    description: 'How to raise a complaint with the LearnViaNotes Grievance Officer, and how quickly we respond.',
  },
}
