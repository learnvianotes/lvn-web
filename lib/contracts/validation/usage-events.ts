// Copied from lvn-backend contracts/src/validation/usage-events.ts by scripts/contracts-sync.mjs — do not edit here.
import { QUIZ_START_KINDS, USAGE_EVENT_LIMITS, USAGE_FEATURES, USAGE_SEARCH_SCOPES, UsageEventName, type QuizStartKind, type UsageFeature, type UsageSearchScope } from '../domain/usage-events'

/**
 * What a usage event may carry (ADR-0107). The API runs every event through these before storing it, and the clients
 * may run them first so nothing is sent that would be dropped. No free text survives: the events with a schema keep
 * only their own keys and fixed values; the older events keep short tokens, numbers and booleans under keys that do not
 * name personal data, and drop the rest.
 */

export type UsagePropValue = string | number | boolean
export type UsageProps = Record<string, UsagePropValue>

export type UsagePropsResult = { ok: true; props: UsageProps | null } | { ok: false; path: string; message: string }

/** `props` of `feature_use`, `search_no_results` and `quiz_start`, as stored. */
export interface FeatureUseProps {
  feature: UsageFeature
}
export interface SearchNoResultsProps {
  scope: UsageSearchScope
  wordCount: number
}
export interface QuizStartProps {
  kind: QuizStartKind
}

const FEATURES: ReadonlySet<string> = new Set(USAGE_FEATURES)
const SCOPES: ReadonlySet<string> = new Set(USAGE_SEARCH_SCOPES)
const KINDS: ReadonlySet<string> = new Set(QUIZ_START_KINDS)
const WITH_SCHEMA: ReadonlySet<string> = new Set([UsageEventName.FEATURE_USE, UsageEventName.SEARCH_NO_RESULTS, UsageEventName.QUIZ_START])

const KEY = new RegExp(`^[A-Za-z][A-Za-z0-9_]{0,${USAGE_EVENT_LIMITS.keyChars - 1}}$`)
/** Keys that name personal data or text. Matched anywhere in the key, any case. */
const BLOCKED_KEY = /email|name|handle|phone|token|password|secret|query|text|message|reason|address|user|title|file|content|comment|body|url|path|agent|^ip$|^q$/i
/** A short token: a letter or digit, then letters, digits or `_ . : -`. No spaces, `@` or `/`. */
const TOKEN = new RegExp(`^[A-Za-z0-9][A-Za-z0-9_.:-]{0,${USAGE_EVENT_LIMITS.tokenChars - 1}}$`)
/** Eight or more hex digits in a row: an id, a hash or a long number. */
const ID_LIKE = /[0-9a-f]{8,}/i

/**
 * A client's app version, semver-like: `MAJOR.MINOR[.PATCH[.BUILD]]`, an optional `-prerelease` and `+build`, at most
 * 32 characters. A leading `v` is dropped. The API stores anything else as no version.
 */
export const APP_VERSION_PATTERN = /^[0-9]{1,6}(\.[0-9]{1,6}){1,3}(-[0-9A-Za-z.-]{1,20})?(\+[0-9A-Za-z.-]{1,20})?$/

/** The version as stored, or null when it is missing or not a version. */
export function normalizeAppVersion(value: string | null | undefined): string | null {
  const trimmed = value?.trim().replace(/^[vV]/, '')
  if (!trimmed || trimmed.length > USAGE_EVENT_LIMITS.appVersionChars || !APP_VERSION_PATTERN.test(trimmed)) return null
  return trimmed
}

/** A client session id: letters, digits, `_` and `-`, at most 64 characters (a UUID fits). */
export function isUsageSessionId(value: string | null | undefined): value is string {
  return typeof value === 'string' && new RegExp(`^[A-Za-z0-9_-]{1,${USAGE_EVENT_LIMITS.sessionIdChars}}$`).test(value)
}

const isObject = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value)
const wordCount = (value: unknown): number | null => (typeof value === 'number' && Number.isInteger(value) && value >= 0 ? Math.min(value, USAGE_EVENT_LIMITS.wordCountCap) : null)
const refuse = (path: string, message: string): UsagePropsResult => ({ ok: false, path, message })
const done = (props: UsageProps): UsagePropsResult => ({ ok: true, props: Object.keys(props).length ? props : null })

/** A value of an older event's props kept as it is, or undefined when it is dropped. */
function tokenValue(value: unknown): UsagePropValue | undefined {
  if (typeof value === 'boolean') return value
  if (typeof value === 'number') return Number.isFinite(value) && Math.abs(value) <= USAGE_EVENT_LIMITS.maxNumber ? value : undefined
  if (typeof value === 'string' && TOKEN.test(value) && !ID_LIKE.test(value)) return value
  return undefined
}

/**
 * The props of a usage event as they may be stored, for an allow-listed name. Refused: props that are not an object,
 * longer than 1024 characters as JSON or with more than 16 keys, and a `feature_use`, `search_no_results` or
 * `quiz_start` without its required value. Dropped: every key an event with a schema does not have, and in the older
 * events any key that names personal data or text and any value that is not a short token, a number or a boolean.
 */
export function sanitizeUsageProps(name: UsageEventName, props: unknown): UsagePropsResult {
  // The events with a schema need their value, so no props is the same as empty props for them.
  if (props == null) {
    if (!WITH_SCHEMA.has(name)) return { ok: true, props: null }
    props = {}
  }
  if (!isObject(props)) return refuse('props', 'props is an object.')
  if (JSON.stringify(props).length > USAGE_EVENT_LIMITS.propsChars) return refuse('props', `props is at most ${USAGE_EVENT_LIMITS.propsChars} characters.`)
  if (Object.keys(props).length > USAGE_EVENT_LIMITS.propsKeys) return refuse('props', `props has at most ${USAGE_EVENT_LIMITS.propsKeys} keys.`)

  switch (name) {
    case UsageEventName.FEATURE_USE: {
      const feature = props['feature']
      if (typeof feature !== 'string' || !FEATURES.has(feature)) return refuse('props.feature', 'feature is one of the UsageFeature ids.')
      return done({ feature })
    }
    case UsageEventName.QUIZ_START: {
      const kind = props['kind']
      if (typeof kind !== 'string' || !KINDS.has(kind)) return refuse('props.kind', 'kind is one of the QuizStartKind values.')
      return done({ kind })
    }
    case UsageEventName.SEARCH_NO_RESULTS: {
      const scope = props['scope']
      if (typeof scope !== 'string' || !SCOPES.has(scope)) return refuse('props.scope', 'scope is one of the UsageSearchScope values.')
      const words = wordCount(props['wordCount'])
      if (words == null) return refuse('props.wordCount', 'wordCount is a whole number, 0 or more.')
      return done({ scope, wordCount: words })
    }
    case UsageEventName.SEARCH: {
      // Clients from before ADR-0107 send `words` and no scope: both stay optional, and a bad value is dropped.
      const out: UsageProps = {}
      const scope = props['scope']
      if (typeof scope === 'string' && SCOPES.has(scope)) out['scope'] = scope
      const words = wordCount(props['wordCount'] ?? props['words'])
      if (words != null) out['wordCount'] = words
      return done(out)
    }
    default: {
      const out: UsageProps = {}
      for (const [key, value] of Object.entries(props)) {
        if (!KEY.test(key) || BLOCKED_KEY.test(key)) continue
        const kept = tokenValue(value)
        if (kept !== undefined) out[key] = kept
      }
      return done(out)
    }
  }
}
