import { PUBLISHED_TERMS_VERSIONS, type PublishedTermsVersion } from '@/features/legal/documents'

/**
 * The admin terms-version controls (lvn-backend ADR-0103). Pure: the card passes what the API said
 * (`adminTermsStatus`) and this web build's registry (features/legal/documents.ts).
 */

export const TERMS_VERSION_KEY = 'terms_version'
export const TERMS_PUBLISHED_VERSIONS_KEY = 'terms_published_versions'

/** Fewer distinct accounts than this is not shown; the API sends null for such a count. */
export const K_ANONYMITY_THRESHOLD = 5

export type TermsSource = 'SETTING' | 'ENV' | 'DEFAULT'

/**
 * Versions an admin may switch to: published by this web build (its text is deployed) and on the API's allowlist
 * (`terms_published_versions`, which the API enforces). Newest first.
 */
export function selectableTermsVersions(apiPublished: readonly string[], web: readonly PublishedTermsVersion[] = PUBLISHED_TERMS_VERSIONS): PublishedTermsVersion[] {
  const allowed = new Set(apiPublished)
  return web.filter((v) => allowed.has(v.version)).reverse()
}

/**
 * Where the two lists disagree. `webOnly`: published here but not allowed by the API yet (add them to
 * terms_published_versions to offer them). `apiOnly`: allowed by the API but this web build has no text for them.
 */
export function termsRegistryGaps(apiPublished: readonly string[], web: readonly PublishedTermsVersion[] = PUBLISHED_TERMS_VERSIONS): { webOnly: string[]; apiOnly: string[] } {
  const api = new Set(apiPublished)
  const local = new Set(web.map((v) => v.version))
  return {
    webOnly: web.map((v) => v.version).filter((v) => !api.has(v)),
    apiOnly: [...api].filter((v) => !local.has(v)).sort(),
  }
}

/** True when the version in effect has no text in this web build: the legal pages then show the newest local one. */
export function currentIsUnpublished(current: string, web: readonly PublishedTermsVersion[] = PUBLISHED_TERMS_VERSIONS): boolean {
  return !web.some((v) => v.version === current)
}

/** The version the picker starts on: the one in effect when it can be chosen, otherwise none (''). */
export function initialTermsChoice(current: string, selectable: readonly PublishedTermsVersion[]): string {
  return selectable.some((v) => v.version === current) ? current : ''
}

export type TermsChoiceIssue = 'empty' | 'unchanged' | 'unavailable'

/** Why switching from `current` to `next` cannot be offered, or null when it can (after a confirm). */
export function termsChoiceIssue(current: string, next: string, selectable: readonly PublishedTermsVersion[]): TermsChoiceIssue | null {
  if (!next) return 'empty'
  if (next === current) return 'unchanged'
  if (!selectable.some((v) => v.version === next)) return 'unavailable'
  return null
}
