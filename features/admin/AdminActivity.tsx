'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useQuery } from '@apollo/client/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useFormatter, useTranslations } from 'next-intl'
import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AdminActivityDocument, AdminActivitySummaryDocument, type AdminActivityQuery } from '@/graphql/generated/graphql'
import { canSeeSection } from '@/features/admin/AdminNav'
import { BarList, DataTable } from '@/features/admin/usage/charts'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { ACTIVITY_PAGE_SIZE, activityWindow, draftFromParams, emptyDraft, paramsFromDraft, presetRange, utcDayKey, type ActivityDraft } from '@/features/admin/activity'
import { isMfaRequiredError } from '@/lib/auth/mfa'

type Entry = AdminActivityQuery['adminActivity']['entries'][number]

/**
 * Audit log for platform admins: a 30-day summary (or the range in the URL), then the rows, newest first.
 * Filters live in the query string. Further pages follow nextCursor.
 */
export function AdminActivity() {
  const t = useTranslations('adminActivity')
  const format = useFormatter()
  const router = useRouter()
  const params = useSearchParams()
  const appliedKey = params.toString()
  const applied = useMemo(() => draftFromParams(new URLSearchParams(appliedKey)), [appliedKey])
  const parsed = useMemo(() => activityWindow(applied), [applied])
  const [draft, setDraft] = useState<ActivityDraft>(applied)
  const [seen, setSeen] = useState(appliedKey)
  if (seen !== appliedKey) {
    setSeen(appliedKey)
    setDraft(applied)
  }

  const { role, ready } = useViewerRole()
  const allowed = canSeeSection(role, 'activity')
  const issue = 'issue' in parsed ? parsed.issue : null
  const range = 'window' in parsed ? parsed.window : null
  const skip = !ready || !allowed || !range

  const summary = useQuery(AdminActivitySummaryDocument, { skip, variables: range ? { from: range.from, to: range.to } : undefined })
  const list = useQuery(AdminActivityDocument, { skip, variables: range ? { filter: range.filter, limit: ACTIVITY_PAGE_SIZE } : undefined })
  const client = useApolloClient()
  const filterKey = JSON.stringify(range?.filter ?? null)
  const [more, setMore] = useState<{ key: string; entries: Entry[]; cursor: string | null | undefined; loading: boolean }>({ key: filterKey, entries: [], cursor: undefined, loading: false })
  if (more.key !== filterKey) setMore({ key: filterKey, entries: [], cursor: undefined, loading: false })

  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!allowed) return <p className="text-muted">{t('notAllowed')}</p>

  const summaryData = summary.data?.adminActivitySummary
  const first = list.data?.adminActivity
  const entries = [...(first?.entries ?? []), ...more.entries]
  const nextCursor = more.cursor === undefined ? (first?.nextCursor ?? null) : more.cursor
  const failed = summary.error ?? list.error
  const mfa = isMfaRequiredError(summary.error) || isMfaRequiredError(list.error)
  const forbidden = isForbidden(summary.error) || isForbidden(list.error)

  const commit = (next: ActivityDraft) => {
    const query = paramsFromDraft(next)
    router.replace(query ? `/admin/activity?${query}` : '/admin/activity', { scroll: false })
  }

  const loadMore = async () => {
    if (!nextCursor || !range || more.loading) return
    setMore((current) => ({ ...current, loading: true }))
    try {
      const result = await client.query({
        query: AdminActivityDocument,
        variables: { filter: range.filter, cursor: nextCursor, limit: ACTIVITY_PAGE_SIZE },
        fetchPolicy: 'network-only',
      })
      const page = result.data?.adminActivity
      if (!page) {
        setMore((current) => ({ ...current, loading: false }))
        return
      }
      setMore((current) => ({ key: filterKey, entries: [...current.entries, ...page.entries], cursor: page.nextCursor, loading: false }))
    } catch {
      setMore((current) => ({ ...current, loading: false }))
    }
  }

  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
  const days = summaryData?.byDay ?? []
  const maxDay = Math.max(1, ...days.map((day) => day.count))
  const actions = (summaryData?.byAction ?? []).slice(0, 8)

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>

      <form
        className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4"
        aria-label={t('filters')}
        onSubmit={(event) => {
          event.preventDefault()
          commit(draft)
        }}
      >
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex min-w-40 flex-1 flex-col gap-1 text-sm">
            <span className="font-medium">{t('action')}</span>
            <Input value={draft.action} onChange={(event) => setDraft((current) => ({ ...current, action: event.target.value }))} placeholder={t('actionHint')} />
          </label>
          <label className="flex min-w-40 flex-1 flex-col gap-1 text-sm">
            <span className="font-medium">{t('actor')}</span>
            <Input value={draft.actor} onChange={(event) => setDraft((current) => ({ ...current, actor: event.target.value }))} placeholder={t('actorHint')} spellCheck={false} />
          </label>
          <label className="flex min-w-36 flex-1 flex-col gap-1 text-sm">
            <span className="font-medium">{t('target')}</span>
            <Input value={draft.target} onChange={(event) => setDraft((current) => ({ ...current, target: event.target.value }))} placeholder={t('targetHint')} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('from')}</span>
            <Input type="date" value={draft.from} max={draft.to || undefined} onChange={(event) => setDraft((current) => ({ ...current, from: event.target.value }))} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('to')}</span>
            <Input type="date" value={draft.to} min={draft.from || undefined} onChange={(event) => setDraft((current) => ({ ...current, to: event.target.value }))} />
          </label>
          <Button type="submit" size="sm">{t('apply')}</Button>
          <Button
            type="button"
            size="sm"
            variant="ghost"
            onClick={() => {
              const cleared = emptyDraft()
              setDraft(cleared)
              commit(cleared)
            }}
          >
            {t('clear')}
          </Button>
        </div>
        <div className="flex flex-wrap gap-1" role="group" aria-label={t('presets')}>
          {[7, 30, 90].map((days) => (
            <Button
              key={days}
              type="button"
              size="sm"
              variant="secondary"
              onClick={() => {
                const next = { ...draft, ...presetRange(days) }
                setDraft(next)
                commit(next)
              }}
            >
              {t('last', { days })}
            </Button>
          ))}
        </div>
        {issue ? <p role="alert" className="text-sm text-bad">{t(`issue.${issue}`)}</p> : null}
        {summaryData ? (
          <p className="text-xs text-muted">
            {t('showing', {
              from: format.dateTime(new Date(summaryData.from), { dateStyle: 'medium', timeStyle: 'short', timeZone }),
              to: format.dateTime(new Date(summaryData.to), { dateStyle: 'medium', timeStyle: 'short', timeZone }),
            })}
          </p>
        ) : null}
      </form>

      {mfa ? <p role="alert" className="text-sm text-bad">{t('mfa')}</p> : null}
      {forbidden ? <p className="text-muted">{t('notAllowed')}</p> : null}
      {failed && !mfa && !forbidden ? <p role="alert" className="text-sm text-bad">{t('failed')}</p> : null}

      <section aria-label={t('summary')} className="flex flex-col gap-4">
        <p className="text-sm font-semibold">{summaryData ? t('total', { count: summaryData.total }) : t('loading')}</p>
        <figure className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
          <figcaption className="font-semibold">{t('byDay')}</figcaption>
          {!days.length ? <p className="text-sm text-muted">{t('noDays')}</p> : (
            <div className="flex h-36 items-end gap-1 overflow-x-auto" data-testid="activity-days" aria-hidden>
              {days.map((day) => (
                <div key={day.day} className="flex h-full min-w-2 flex-1 flex-col justify-end" title={`${utcDayKey(day.day)} ${day.count}`}>
                  <div className="w-full rounded-t bg-accent" style={{ height: `${Math.max(day.count > 0 ? 8 : 0, (day.count / maxDay) * 100)}%` }} />
                </div>
              ))}
            </div>
          )}
          {days.length ? (
            <DataTable caption={t('byDay')} header={[t('day'), t('count')]} rows={days.map((day) => [utcDayKey(day.day), format.number(day.count)])} />
          ) : null}
        </figure>
        <BarList title={t('byAction')} valueLabel={t('count')} bars={actions.map((row) => ({ key: row.action, label: row.action, value: row.count }))} />
      </section>

      <div className="overflow-x-auto rounded-2xl border border-border bg-surface">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">{t('table')}</caption>
          <thead>
            <tr className="border-b border-border text-muted">
              <th scope="col" className="px-3 py-2 font-medium">{t('time')}</th>
              <th scope="col" className="px-3 py-2 font-medium">{t('actor')}</th>
              <th scope="col" className="px-3 py-2 font-medium">{t('action')}</th>
              <th scope="col" className="px-3 py-2 font-medium">{t('target')}</th>
              <th scope="col" className="px-3 py-2 font-medium">{t('ip')}</th>
              <th scope="col" className="px-3 py-2 font-medium">{t('details')}</th>
            </tr>
          </thead>
          <tbody>
            {!entries.length && !list.loading ? (
              <tr>
                <td colSpan={6} className="px-3 py-6 text-muted">{t('empty')}</td>
              </tr>
            ) : null}
            {entries.map((entry) => (
              <tr key={entry.id} className="border-b border-border align-top last:border-0">
                <td className="whitespace-nowrap px-3 py-2">
                  <time dateTime={entry.createdAt}>{format.dateTime(new Date(entry.createdAt), { dateStyle: 'medium', timeStyle: 'short', timeZone })}</time>
                </td>
                <td className="px-3 py-2">{entry.actorEmail ?? t('removedActor')}</td>
                <td className="px-3 py-2 font-medium">{entry.action}</td>
                <td className="px-3 py-2">
                  <span className="block">{entry.targetType}</span>
                  {entry.targetId ? <span className="block break-all text-xs text-muted">{entry.targetId}</span> : null}
                </td>
                <td className="whitespace-nowrap px-3 py-2">{entry.ip ?? t('none')}</td>
                <td className="px-3 py-2">
                  <details>
                    <summary className="cursor-pointer text-accent">{t('details')}</summary>
                    {entry.userAgent ? <p className="mt-2 text-xs text-muted">{entry.userAgent}</p> : null}
                    <pre className="mt-2 max-w-md overflow-x-auto whitespace-pre-wrap text-xs">{entry.details == null ? t('noDetails') : JSON.stringify(entry.details, null, 2)}</pre>
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {nextCursor ? (
        <Button type="button" variant="secondary" disabled={more.loading} onClick={() => void loadMore()}>{more.loading ? t('loading') : t('loadMore')}</Button>
      ) : null}
    </div>
  )
}

function isForbidden(error: unknown): boolean {
  return CombinedGraphQLErrors.is(error) && error.errors.some((item) => item.extensions?.code === 'FORBIDDEN')
}
