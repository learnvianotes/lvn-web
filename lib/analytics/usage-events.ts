/**
 * The fixed values the v2 usage events carry (lvn-backend ADR-0107). The API refuses a whole batch when a
 * `feature_use`, `search_no_results` or `quiz_start` lacks its value, so the tracker checks them here first and drops a
 * bad event instead. The lists mirror the GraphQL enums (upper case there, lower case on the wire); the type checks
 * below fail the build when the schema gains or loses an id.
 */
import type { QuizStartKind as GqlQuizStartKind, UsageFeature as GqlUsageFeature, UsageSearchScope as GqlUsageSearchScope } from '@/graphql/generated/graphql'

export const USAGE_FEATURES = [
  'notes_editor',
  'page_editor',
  'pdf_viewer',
  'voice_note',
  'quick_capture',
  'read_aloud',
  'class_quiz',
  'shared_quiz',
  'flashcards_review',
  'exam_plan',
  'focus',
  'groups',
  'classroom',
  'doubts',
  'ai_assist',
  'resources',
  'search',
  'profile',
  'settings',
] as const
export type UsageFeature = (typeof USAGE_FEATURES)[number]

export const USAGE_SEARCH_SCOPES = ['all', 'notes', 'people', 'groups', 'classrooms', 'resources', 'topics'] as const
export type UsageSearchScope = (typeof USAGE_SEARCH_SCOPES)[number]

export const QUIZ_START_KINDS = ['class', 'shared', 'note', 'practice'] as const
export type QuizStartKind = (typeof QUIZ_START_KINDS)[number]

/** `wordCount` past this is sent as this: 20 means 20 or more words. */
export const WORD_COUNT_CAP = 20

// Exact match both ways with the schema's enums: a missing or extra id is a type error here.
type Same<A, B> = [A] extends [B] ? ([B] extends [A] ? true : false) : false
export type UsageEnumsMatchSchema = [
  Same<Uppercase<UsageFeature>, GqlUsageFeature>,
  Same<Uppercase<UsageSearchScope>, GqlUsageSearchScope>,
  Same<Uppercase<QuizStartKind>, GqlQuizStartKind>,
] extends [true, true, true]
  ? true
  : never
export const USAGE_ENUMS_MATCH_SCHEMA: UsageEnumsMatchSchema = true

const FEATURES: ReadonlySet<string> = new Set(USAGE_FEATURES)
const SCOPES: ReadonlySet<string> = new Set(USAGE_SEARCH_SCOPES)
const KINDS: ReadonlySet<string> = new Set(QUIZ_START_KINDS)

export const isUsageFeature = (value: unknown): value is UsageFeature => typeof value === 'string' && FEATURES.has(value)
export const isUsageSearchScope = (value: unknown): value is UsageSearchScope => typeof value === 'string' && SCOPES.has(value)
export const isQuizStartKind = (value: unknown): value is QuizStartKind => typeof value === 'string' && KINDS.has(value)

/** Words in a search as the API stores them: a whole number, capped. The words themselves never leave the browser. */
export function wordCountOf(text: string): number {
  const trimmed = text.trim()
  return Math.min(trimmed ? trimmed.split(/\s+/).length : 0, WORD_COUNT_CAP)
}

/**
 * The scope a search is reported under: the one scope asked for, else `all` (every scope, or several: the API takes
 * one scope per event).
 */
export function searchScopeOf(scopes: readonly string[] | null | undefined): UsageSearchScope {
  if (!scopes || scopes.length !== 1) return 'all'
  const one = scopes[0]!.toLowerCase()
  return isUsageSearchScope(one) ? one : 'all'
}

/**
 * The props of an event with a schema as they are sent, or null when the API would refuse them (the event is then
 * dropped). Any other key is left out. Undefined for the older events, which go through `usageProps`.
 */
export function schemaProps(name: string, props: Record<string, unknown> | undefined): Record<string, string | number> | null | undefined {
  switch (name) {
    case 'feature_use': {
      const feature = props?.['feature']
      return isUsageFeature(feature) ? { feature } : null
    }
    case 'quiz_start': {
      const kind = props?.['kind']
      return isQuizStartKind(kind) ? { kind } : null
    }
    case 'search_no_results': {
      const scope = props?.['scope']
      const words = props?.['wordCount']
      if (!isUsageSearchScope(scope) || typeof words !== 'number' || !Number.isInteger(words) || words < 0) return null
      return { scope, wordCount: Math.min(words, WORD_COUNT_CAP) }
    }
    default:
      return undefined
  }
}

/** MAJOR.MINOR[.PATCH[.BUILD]], optional -prerelease and +build: the API's appVersion rule (at most 32 characters). */
const APP_VERSION = /^[0-9]{1,6}(\.[0-9]{1,6}){1,3}(-[0-9A-Za-z.-]{1,20})?(\+[0-9A-Za-z.-]{1,20})?$/

/** A version as the API stores it, or null when it is not one (then none is sent). A leading `v` is dropped. */
export function normalizeAppVersion(value: string | null | undefined): string | null {
  const trimmed = value?.trim().replace(/^[vV]/, '')
  if (!trimmed || trimmed.length > 32 || !APP_VERSION.test(trimmed)) return null
  return trimmed
}

/** This web build's version, the same on every event: NEXT_PUBLIC_APP_VERSION, which next.config.ts sets from the env or package.json. */
export function webAppVersion(): string | null {
  return normalizeAppVersion(process.env.NEXT_PUBLIC_APP_VERSION)
}

/**
 * The product area a page belongs to, for the screens that are a feature by themselves; null for the rest. Features
 * used inside a page (the note editor, a voice note, read aloud, AI actions, a focus session, quick capture) are
 * recorded where they start instead.
 */
const PATH_FEATURES: [RegExp, UsageFeature][] = [
  [/^\/groups\/[^/]+\/doubts(\/|$)/, 'doubts'],
  [/^\/groups(\/|$)/, 'groups'],
  [/^\/classes\/[^/]+\/quizzes\/[^/]+$/, 'class_quiz'],
  [/^\/classes(\/|$)/, 'classroom'],
  [/^\/(quiz|q)\/[^/]+$/, 'shared_quiz'],
  [/^\/(review|flashcards)$/, 'flashcards_review'],
  [/^\/exams(\/|$)/, 'exam_plan'],
  [/^\/resources(\/|$)/, 'resources'],
  [/^\/search$/, 'search'],
  [/^\/ask$/, 'ai_assist'],
  [/^\/profile\/notifications$/, 'settings'],
  [/^\/profile(\/|$)/, 'profile'],
]

export function featureOfPath(path: string): UsageFeature | null {
  return PATH_FEATURES.find(([pattern]) => pattern.test(path))?.[1] ?? null
}
