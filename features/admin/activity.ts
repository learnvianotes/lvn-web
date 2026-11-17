/** Query string and date window for /admin/activity. The API takes an inclusive start and an exclusive end. */

const DAY = 24 * 60 * 60 * 1000
export const ACTIVITY_MAX_DAYS = 366
export const ACTIVITY_PAGE_SIZE = 50

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export type ActivityDraft = {
  action: string
  actor: string
  target: string
  from: string
  to: string
}

export type ActivityIssue = 'actor' | 'order' | 'range'

export type ActivityFilter = {
  action?: string
  actorId?: string
  targetType?: string
  from: string
  to: string
}

export type ActivityWindow = {
  from: string
  to: string
  filter: ActivityFilter
}

export function emptyDraft(): ActivityDraft {
  return { action: '', actor: '', target: '', from: '', to: '' }
}

export function draftFromParams(params: Pick<URLSearchParams, 'get'>): ActivityDraft {
  return {
    action: params.get('action') ?? '',
    actor: params.get('actor') ?? '',
    target: params.get('target') ?? '',
    from: params.get('from') ?? '',
    to: params.get('to') ?? '',
  }
}

export function paramsFromDraft(draft: ActivityDraft): string {
  const params = new URLSearchParams()
  const action = draft.action.trim()
  const actor = draft.actor.trim()
  const target = draft.target.trim()
  if (action) params.set('action', action)
  if (actor) params.set('actor', actor)
  if (target) params.set('target', target)
  if (draft.from) params.set('from', draft.from)
  if (draft.to) params.set('to', draft.to)
  return params.toString()
}

/** Calendar dates for a preset ending today, in the viewer's local zone. */
export function presetRange(days: number, now = new Date()): Pick<ActivityDraft, 'from' | 'to'> {
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const start = new Date(end.getFullYear(), end.getMonth(), end.getDate() - (days - 1))
  return { from: dateInput(start), to: dateInput(end) }
}

function dateInput(value: Date): string {
  const month = String(value.getMonth() + 1).padStart(2, '0')
  const day = String(value.getDate()).padStart(2, '0')
  return `${value.getFullYear()}-${month}-${day}`
}

function localDayStart(date: string): Date | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(date)
  if (!match) return null
  const year = Number(match[1])
  const month = Number(match[2])
  const day = Number(match[3])
  const value = new Date(year, month - 1, day)
  if (value.getFullYear() !== year || value.getMonth() !== month - 1 || value.getDate() !== day) return null
  return value
}

/**
 * The summary and the table share one window. With no dates, that window is the last 30 days ending now,
 * which is what adminActivitySummary does when both arguments are omitted.
 */
export function activityWindow(draft: ActivityDraft, now = new Date()): { window: ActivityWindow } | { issue: ActivityIssue } {
  const actor = draft.actor.trim()
  if (actor && !UUID.test(actor)) return { issue: 'actor' }

  let start: Date
  let end: Date
  if (!draft.from && !draft.to) {
    end = now
    start = new Date(now.getTime() - 30 * DAY)
  } else {
    const from = draft.from ? localDayStart(draft.from) : null
    const to = draft.to ? localDayStart(draft.to) : null
    if ((draft.from && !from) || (draft.to && !to)) return { issue: 'range' }
    start = from ?? new Date((to ?? now).getTime() - 30 * DAY)
    end = to ? new Date(to.getFullYear(), to.getMonth(), to.getDate() + 1) : now
  }

  if (start.getTime() >= end.getTime()) return { issue: 'order' }
  if (end.getTime() - start.getTime() > ACTIVITY_MAX_DAYS * DAY) return { issue: 'range' }

  const from = start.toISOString()
  const to = end.toISOString()
  const filter: ActivityFilter = { from, to }
  const action = draft.action.trim()
  const target = draft.target.trim()
  if (action) filter.action = action
  if (actor) filter.actorId = actor
  if (target) filter.targetType = target
  return { window: { from, to, filter } }
}

/** UTC day the summary bar belongs to, as YYYY-MM-DD. */
export function utcDayKey(iso: string): string {
  const value = new Date(iso)
  if (Number.isNaN(value.getTime())) return iso
  return value.toISOString().slice(0, 10)
}
