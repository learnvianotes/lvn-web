import type { AdminContentCountsQueryVariables, AdminContentFilter, AdminContentQueryVariables, AdminContentType, AdminContentVisibility } from '@/graphql/generated/graphql'

/** The kinds adminContent returns, in the schema's order. */
export const CONTENT_TYPES = ['NOTE', 'COMMENT', 'GROUP', 'GROUP_POST', 'CLASSROOM', 'CLASSROOM_POST', 'QUIZ', 'DOUBT', 'DOUBT_ANSWER', 'SHARE', 'UPLOAD', 'RESOURCE', 'HIGHLIGHT', 'CONTEST'] as const satisfies readonly AdminContentType[]

export const CONTENT_VISIBILITIES = ['PUBLIC', 'SHARED', 'UNLISTED', 'PRIVATE', 'MEMBERS'] as const satisfies readonly AdminContentVisibility[]

/** The API's default page, and its maximum is 100. */
export const CONTENT_PAGE_SIZE = 20

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
const DAY = /^\d{4}-\d{2}-\d{2}$/
/** The same clock the usage dashboard buckets in. A chosen day is that whole day in India. */
const IST = '+05:30'

export type ContentFilters = {
  type: AdminContentType | ''
  /** A handle, or an account id. */
  user: string
  /** YYYY-MM-DD, or empty. */
  from: string
  to: string
  visibility: AdminContentVisibility | ''
  after: string
}

export const EMPTY_FILTERS: ContentFilters = { type: '', user: '', from: '', to: '', visibility: '', after: '' }

function oneOf<T extends string>(value: string | null, allowed: readonly T[]): T | '' {
  return value && (allowed as readonly string[]).includes(value) ? (value as T) : ''
}

/** A YYYY-MM-DD from the URL, or blank when it is not one. */
function dayOrBlank(value: string | null): string {
  return value && DAY.test(value) ? value : ''
}

/** The start or the last millisecond of a calendar day in India Standard Time. */
export function dayInstant(day: string, end: boolean): string | undefined {
  if (!DAY.test(day)) return undefined
  const clock = end ? 'T23:59:59.999' : 'T00:00:00.000'
  return new Date(`${day}${clock}${IST}`).toISOString()
}

/** Read the filters the address holds. Anything it does not understand is left out. */
export function readFilters(params: URLSearchParams): ContentFilters {
  return {
    type: oneOf(params.get('type'), CONTENT_TYPES),
    user: params.get('user') ?? '',
    from: dayOrBlank(params.get('from')),
    to: dayOrBlank(params.get('to')),
    visibility: oneOf(params.get('visibility'), CONTENT_VISIBILITIES),
    after: params.get('after') ?? '',
  }
}

/** The query string for these filters. Empty fields are left out, so a cleared filter leaves the URL. */
export function writeFilters(filters: ContentFilters): string {
  const search = new URLSearchParams()
  if (filters.type) search.set('type', filters.type)
  if (filters.user) search.set('user', filters.user)
  if (filters.from) search.set('from', filters.from)
  if (filters.to) search.set('to', filters.to)
  if (filters.visibility) search.set('visibility', filters.visibility)
  if (filters.after) search.set('after', filters.after)
  return search.toString()
}

/** A handle, unless the text is an account id. Blank sends neither. */
export function authorFilter(user: string): Pick<AdminContentFilter, 'userId' | 'handle'> {
  const value = user.trim()
  if (!value) return {}
  return UUID.test(value) ? { userId: value } : { handle: value }
}

export function listVariables(filters: ContentFilters): AdminContentQueryVariables {
  const from = dayInstant(filters.from, false)
  const to = dayInstant(filters.to, true)
  const filter: AdminContentFilter = {
    ...(filters.type ? { type: filters.type } : {}),
    ...authorFilter(filters.user),
    ...(from ? { from } : {}),
    ...(to ? { to } : {}),
    ...(filters.visibility ? { visibility: filters.visibility } : {}),
  }
  return {
    filter: Object.keys(filter).length ? filter : null,
    first: CONTENT_PAGE_SIZE,
    after: filters.after || null,
  }
}

/** Counts follow the date range only. Type, person and visibility narrow the table, not the totals. */
export function countVariables(filters: ContentFilters): AdminContentCountsQueryVariables {
  const from = dayInstant(filters.from, false)
  const to = dayInstant(filters.to, true)
  return { ...(from ? { from } : {}), ...(to ? { to } : {}) }
}
