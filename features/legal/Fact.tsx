import { LEGAL, LEGAL_FIELD_LABELS, type LegalField } from '@/config/legal'

/** A fact from config/legal.ts, or a highlighted gap while it is still blank (production builds refuse those). */
export function Fact({ field }: { field: LegalField }) {
  const value = LEGAL[field].trim()
  if (value) return <>{value}</>
  return <mark className="rounded bg-warn/10 px-1 text-warn">[{LEGAL_FIELD_LABELS[field]}]</mark>
}

/** The grievance mailbox as a link, or its gap. */
export function Mailbox() {
  const email = LEGAL.email.trim()
  return email ? <a href={`mailto:${email}`} className="font-medium text-accent underline-offset-2 hover:underline">{email}</a> : <Fact field="email" />
}

/** Who to write to: the Grievance Officer, the mailbox, the post address and the operator. */
export function ContactList({ operatorLabel = 'On behalf of' }: { operatorLabel?: string }) {
  return (
    <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 rounded-2xl border border-border bg-surface p-4 text-sm">
      <dt className="font-semibold">Grievance Officer</dt>
      <dd><Fact field="grievanceOfficer" /></dd>
      <dt className="font-semibold">Email</dt>
      <dd><Mailbox /></dd>
      <dt className="font-semibold">Post</dt>
      <dd><Fact field="address" /></dd>
      <dt className="font-semibold">{operatorLabel}</dt>
      <dd><Fact field="operator" />, which runs LearnViaNotes</dd>
    </dl>
  )
}
