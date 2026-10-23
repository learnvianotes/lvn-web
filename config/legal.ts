/**
 * Who runs LearnViaNotes, and the facts the Privacy Policy, Terms and Grievance Redressal pages state. The owner fills
 * these in; until then the pages show each gap, and a production build refuses to run (lib/launch-checks.ts). They are
 * the same for every environment, so they live here rather than in the environment.
 */
export const LEGAL = {
  /** Legal name of the person or company that operates LearnViaNotes (the data fiduciary). */
  operator: 'K Manideep & K Thrishank',
  /** Postal address for notices: street, city, state, PIN. */
  address: 'Bengaluru 560046',
  /** City whose courts hear disputes under the Terms. */
  courtsCity: '',
  /** The Grievance Officer's name (IT Rules 2021, rule 3(2); SPDI Rules 2011, rule 5(9)). */
  grievanceOfficer: '',
  /** Mailbox for privacy and grievance mail, e.g. grievance@learnvianotes.in. */
  email: '',
}

export type LegalField = keyof typeof LEGAL

/** What each fact is called where it is missing (the pages' gaps, the build check). */
export const LEGAL_FIELD_LABELS: Record<LegalField, string> = {
  operator: 'operator’s legal name',
  address: 'postal address',
  courtsCity: 'city for disputes',
  grievanceOfficer: 'Grievance Officer’s name',
  email: 'grievance email',
}

/** The facts still blank, in the order the pages list them. */
export function missingLegalFields(values: Record<LegalField, string> = LEGAL): LegalField[] {
  return (Object.keys(LEGAL_FIELD_LABELS) as LegalField[]).filter((k) => !values[k].trim())
}

/**
 * The youngest age that may hold an account, as the Privacy Policy and Terms state it. Must match the API's
 * ACCOUNT_MINIMUM_AGE (lvn-backend ADR-0091). The sign-up forms never show it.
 */
export const ACCOUNTS_FROM_AGE = 18

/**
 * How long data is kept, as the Privacy Policy states it (lvn-backend spec §15.2, ADR-0018, ADR-0088, ADR-0089). Change
 * the policy and the systems together.
 */
export const RETENTION = {
  /** Deleted notes stay in the trash this long (§4.1). */
  trashDays: 30,
  /** A deleted account goes this long after the request (ADR-0088). */
  deletionGraceDays: 14,
  /** A data export can be downloaded this long (ADR-0018). */
  exportDays: 7,
  /** Raw learning events; after that only totals (§15.2). */
  learningEventsMonths: 24,
  /** Server logs (§15.2). */
  logsDays: 30,
  /** Security and moderation records, the audit log (§15.2). */
  auditYears: 7,
  /** Database backups (ADR-0089). */
  backupDays: 7,
  /** Google Analytics → Admin → Data retention (2 or 14 months), when analytics is on (ADR-0092). */
  analyticsMonths: 2,
}
