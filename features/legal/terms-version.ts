import 'server-only'
import { print } from 'graphql'
import { cache } from 'react'
import { LegalTermsVersionDocument } from '@/graphql/generated/graphql'
import { serverEnv } from '@/lib/server-env'
import { isPublishedTermsVersion, TERMS_VERSION } from './documents'

/** How long a legal page keeps the version it read from the API (lvn-backend ADR-0103: an admin can change it). */
export const TERMS_VERSION_REVALIDATE_SECONDS = 60

const QUERY = print(LegalTermsVersionDocument)

/**
 * The version label a legal page shows, from the version the API has in effect. If the API gave none (unreachable or
 * an error), it is the newest local version. If the API's version is one this web app has not published, the pages
 * cannot have its text, so they show the newest local one and the mismatch is logged for the operator.
 */
export function displayedTermsVersion(apiVersion: string | null, warn: (message: string) => void = console.warn): string {
  if (apiVersion === null) return TERMS_VERSION
  if (isPublishedTermsVersion(apiVersion)) return apiVersion
  warn(`[legal] The API's terms version ${JSON.stringify(apiVersion.slice(0, 40))} is not in PUBLISHED_TERMS_VERSIONS (features/legal/documents.ts); showing ${TERMS_VERSION}.`)
  return TERMS_VERSION
}

/** Query.termsVersion, read anonymously; null when the API cannot answer. Cached for TERMS_VERSION_REVALIDATE_SECONDS. */
export async function fetchTermsVersion(): Promise<string | null> {
  try {
    const res = await fetch(serverEnv.apiUrl, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ query: QUERY }),
      next: { revalidate: TERMS_VERSION_REVALIDATE_SECONDS, tags: ['terms-version'] },
      signal: AbortSignal.timeout(3_000),
    })
    if (!res.ok) return null
    const body = (await res.json()) as { data?: { termsVersion?: unknown } | null }
    const version = body.data?.termsVersion
    return typeof version === 'string' && version ? version : null
  } catch {
    return null
  }
}

/** The version a legal page shows: the API's, else the newest local one. Never throws. */
export const getDisplayedTermsVersion = cache(async (): Promise<string> => displayedTermsVersion(await fetchTermsVersion()))
