'use client'

import { useCallback, useEffect, useState } from 'react'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { loadUsageSummary, loadUserTimeline, PlatformError, type TimelineEntry, type UsageSummary } from '@/lib/platform-api'

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/** DAU, WAU and MAU, the features and actions people use, and one person's timeline. */
export function AdminUsage() {
  const t = useTranslations('adminUsage')
  const format = useFormatter()
  const { role, ready } = useViewerRole()
  const [summary, setSummary] = useState<UsageSummary | null>(null)
  const [error, setError] = useState<string | null>(null)
  const load = useCallback(async () => {
    try {
      setSummary(await loadUsageSummary())
      setError(null)
    } catch (e) {
      setError(e instanceof PlatformError && e.forbidden ? t('notAllowed') : t('failed'))
    }
  }, [t])
  useEffect(() => {
    if (ready && canSeeSection(role, 'usage')) void load()
  }, [ready, role, load])
  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!canSeeSection(role, 'usage')) return <p className="text-muted">{t('notAllowed')}</p>
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {summary ? (
        <>
          <dl className="grid gap-3 sm:grid-cols-3">
            <Stat label={t('dau')} value={format.number(summary.dau)} />
            <Stat label={t('wau')} value={format.number(summary.wau)} />
            <Stat label={t('mau')} value={format.number(summary.mau)} />
          </dl>
          <div className="grid gap-4 lg:grid-cols-2">
            <Rank title={t('pages')} rows={summary.topFeatures} empty={t('noPages')} />
            <Rank title={t('features')} rows={summary.topEvents} empty={t('noFeatures')} />
          </div>
        </>
      ) : null}
      <Timeline />
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-4">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="text-3xl font-extrabold tracking-tight">{value}</dd>
    </div>
  )
}

function Rank({ title, rows, empty }: { title: string; rows: { name: string; count: number }[]; empty: string }) {
  const format = useFormatter()
  const id = title.toLowerCase().replace(/[^a-z]+/g, '-')
  return (
    <section aria-labelledby={id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
      <h2 id={id} className="font-semibold">{title}</h2>
      {!rows.length ? <p className="text-sm text-muted">{empty}</p> : null}
      <ol className="flex flex-col gap-1">
        {rows.map((row) => (
          <li key={row.name} className="flex items-baseline justify-between gap-3 text-sm">
            <span className="truncate">{row.name}</span>
            <span className="font-medium">{format.number(row.count)}</span>
          </li>
        ))}
      </ol>
    </section>
  )
}

function Timeline() {
  const t = useTranslations('adminUsage')
  const format = useFormatter()
  const [userId, setUserId] = useState('')
  const [rows, setRows] = useState<TimelineEntry[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const look = async () => {
    const id = userId.trim()
    if (!UUID.test(id)) return setError(t('badId'))
    setBusy(true)
    setError(null)
    try {
      setRows(await loadUserTimeline(id))
    } catch {
      setRows(null)
      setError(t('failed'))
    } finally {
      setBusy(false)
    }
  }
  return (
    <section aria-labelledby="user-timeline" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <h2 id="user-timeline" className="font-semibold">{t('timeline')}</h2>
      <p className="text-sm text-muted">{t('timelineLead')}</p>
      <form className="flex flex-col gap-2 sm:flex-row" onSubmit={(e) => { e.preventDefault(); void look() }}>
        <label className="flex min-w-0 flex-1 flex-col gap-1">
          <span className="sr-only">{t('userId')}</span>
          <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder={t('userId')} />
        </label>
        <Button type="submit" disabled={busy}>{t('lookUp')}</Button>
      </form>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {rows && !rows.length ? <p className="text-sm text-muted">{t('noEvents')}</p> : null}
      <ol className="flex flex-col gap-2">
        {(rows ?? []).map((row, index) => (
          <li key={`${row.occurredAt}-${row.name}-${index}`} className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
            <span className="font-medium">{row.name}<span className="font-normal text-muted"> · {row.platform}</span></span>
            <time className="text-muted" dateTime={row.occurredAt}>{format.dateTime(new Date(row.occurredAt), { dateStyle: 'medium', timeStyle: 'short' })}</time>
          </li>
        ))}
      </ol>
    </section>
  )
}
