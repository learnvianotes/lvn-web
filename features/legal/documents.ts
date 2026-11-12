import type { Metadata } from 'next'

/** One version of the Terms, Privacy Policy and content licence this web app has published. */
export interface PublishedTermsVersion {
  /** The text's date, YYYY-MM-DD: the value people accept and the API's `terms_version` setting holds. */
  version: string
  /** What changed from the version before, in a line, for the admin version picker. */
  summary: string
}

/**
 * Every version of the legal documents people accept (lvn-backend §15.2, ADR-0103), oldest first. One version covers
 * all three. This list is the source of truth for which versions the web has published: the admin settings page only
 * offers versions on it, and lvn-backend's `terms_published_versions` allowlist (setting, else the
 * `TERMS_PUBLISHED_VERSIONS` environment variable, else its built-in default) must list the same versions. The pages
 * always show the newest text; to publish a new version, add it last here with its text, deploy, add it to the
 * allowlist, then switch `terms_version` on /admin/settings. Never remove or reorder an entry: people accepted it.
 */
export const PUBLISHED_TERMS_VERSIONS = [
  { version: '2026-10-08', summary: 'First Terms of Service, Privacy Policy and content licence.' },
  { version: '2026-11-03', summary: 'Adults only (18 and over), optional Google Analytics, the Grievance page and the operator’s details.' },
  { version: '2026-11-12', summary: 'Accounts from age 13, parental consent for ages 13–17 (India’s DPDP Act), the processors in use, and how to delete an account.' },
] as const satisfies readonly PublishedTermsVersion[]

/**
 * The newest published version: the one the pages' text is, and the one shown when the API cannot be asked. The
 * version people accept is the API's `Query.termsVersion`, which an admin may set to any published version.
 */
export const TERMS_VERSION: string = PUBLISHED_TERMS_VERSIONS[PUBLISHED_TERMS_VERSIONS.length - 1]!.version

const LEGAL_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'] as const

/** A published version (`YYYY-MM-DD`) as the legal pages’ “Last updated” line, for example `12 November 2026`. */
export function legalLastUpdated(version: string = TERMS_VERSION): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(version)
  const month = match ? LEGAL_MONTHS[Number(match[2]) - 1] : undefined
  if (!match || !month) return version
  return `${Number(match[3])} ${month} ${match[1]}`
}

/** True when this web app has published `version`. */
export function isPublishedTermsVersion(version: string): boolean {
  return PUBLISHED_TERMS_VERSIONS.some((v) => v.version === version)
}

/** The registry entry for `version`, or undefined when this web app has not published it. */
export function publishedTermsVersion(version: string): PublishedTermsVersion | undefined {
  return PUBLISHED_TERMS_VERSIONS.find((v) => v.version === version)
}

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
