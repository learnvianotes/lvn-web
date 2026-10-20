/* Facts from src/config.ts → LEGAL, or a visible gap where one is still blank. */

import { LEGAL } from '@/config'
import { LEGAL_FIELD_LABELS, type LegalField } from './legal'

export function Fact({ field }: { field: LegalField }) {
  const value = LEGAL[field].trim()
  if (value) return <>{value}</>
  return <mark className="legal-gap">[{LEGAL_FIELD_LABELS[field]}]</mark>
}

/** The grievance mailbox as a link (or its gap). */
export function Mailbox() {
  const email = LEGAL.email.trim()
  return email ? <a href={`mailto:${email}`}>{email}</a> : <Fact field="email" />
}
