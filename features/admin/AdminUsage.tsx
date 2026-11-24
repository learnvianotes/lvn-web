'use client'

import { useState, type ReactNode } from 'react'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { MetricsInterval } from '@/graphql/generated/graphql'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import {
  ContentPanel,
  EngagementPanel,
  FeaturesPanel,
  FunnelPanel,
  GrowthPanel,
  OverviewPanel,
  RetentionPanel,
  SearchQualityPanel,
  SubjectsPanel,
  USAGE_TABS,
  VerificationPanel,
  VersionsPanel,
  type PanelProps,
  type UsageTab,
} from '@/features/admin/usage/panels'
import { lastDays, rangeIssue, type DayRange, type RangeIssue } from '@/features/admin/usage/shape'
import { loadUserTimeline, type TimelineEntry } from '@/lib/platform-api'

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
const PRESETS = [7, 30, 90] as const

const PANELS: Record<UsageTab, (props: PanelProps) => ReactNode> = {
  overview: OverviewPanel,
  growth: GrowthPanel,
  engagement: EngagementPanel,
  content: ContentPanel,
  subjects: SubjectsPanel,
  retention: RetentionPanel,
  verification: VerificationPanel,
  funnel: FunnelPanel,
  features: FeaturesPanel,
  search: SearchQualityPanel,
  versions: VersionsPanel,
}

/** Tabs that draw a series per day or week; the others are totals for the range. */
const WITH_INTERVAL: ReadonlySet<UsageTab> = new Set(['growth', 'engagement'])

/**
 * The admin usage dashboard: aggregate counts in tabs over an IST date range, a CSV of what each tab shows, and one
 * person's timeline behind an explicit "Look up a user" (lvn-backend ADR-0105, ADR-0106). Opted-out accounts are
 * never counted and any breakdown group under 5 people is hidden by the API.
 */
export function AdminUsage() {
  const t = useTranslations('adminUsage')
  const { role, ready } = useViewerRole()
  const [tab, setTab] = useState<UsageTab>('overview')
  const [range, setRange] = useState<DayRange>(() => lastDays(30))
  const [draft, setDraft] = useState<DayRange>(range)
  const [issue, setIssue] = useState<RangeIssue | null>(null)
  const [interval, setBucket] = useState<MetricsInterval>('DAY')
  const [lookUp, setLookUp] = useState(false)
  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!canSeeSection(role, 'usage')) return <p className="text-muted">{t('notAllowed')}</p>

  const apply = (next: DayRange) => {
    const problem = rangeIssue(next)
    setIssue(problem)
    if (!problem) {
      setDraft(next)
      setRange(next)
    }
  }
  const Active = PANELS[tab]
  const showsRange = tab !== 'retention'

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h1 className="text-2xl font-semibold">{t('title')}</h1>
          <Button type="button" variant="secondary" size="sm" aria-expanded={lookUp} aria-controls="user-timeline-section" onClick={() => setLookUp((v) => !v)}>
            {lookUp ? t('hideLookUp') : t('lookUpUser')}
          </Button>
        </div>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>

      {lookUp ? <Timeline /> : null}

      <form
        className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4"
        aria-label={t('range.label')}
        onSubmit={(e) => {
          e.preventDefault()
          apply(draft)
        }}
      >
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('range.from')}</span>
            <Input type="date" value={draft.from} max={draft.to || undefined} onChange={(e) => setDraft((d) => ({ ...d, from: e.target.value }))} disabled={!showsRange} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('range.to')}</span>
            <Input type="date" value={draft.to} min={draft.from || undefined} onChange={(e) => setDraft((d) => ({ ...d, to: e.target.value }))} disabled={!showsRange} />
          </label>
          <Button type="submit" size="sm" disabled={!showsRange}>{t('range.apply')}</Button>
          <div className="flex flex-wrap gap-1" role="group" aria-label={t('range.presets')}>
            {PRESETS.map((days) => (
              <Button key={days} type="button" size="sm" variant="ghost" disabled={!showsRange} onClick={() => apply(lastDays(days))}>
                {t('range.last', { days })}
              </Button>
            ))}
          </div>
          {WITH_INTERVAL.has(tab) ? (
            <div className="flex gap-1" role="group" aria-label={t('interval.label')}>
              {(['DAY', 'WEEK'] as const).map((value) => (
                <Button key={value} type="button" size="sm" variant={interval === value ? 'primary' : 'secondary'} aria-pressed={interval === value} onClick={() => setBucket(value)}>
                  {t(`interval.${value}`)}
                </Button>
              ))}
            </div>
          ) : null}
        </div>
        <p className="text-xs text-muted">{showsRange ? t('range.shown', { from: range.from, to: range.to }) : t('range.notUsed')}</p>
        {issue ? <p role="alert" className="text-sm text-bad">{t(`range.${issue}`)}</p> : null}
      </form>

      <div role="tablist" aria-label={t('tabsLabel')} className="flex gap-1 overflow-x-auto border-b border-border">
        {USAGE_TABS.map((key) => (
          <button
            key={key}
            id={`usage-tab-${key}`}
            role="tab"
            type="button"
            aria-selected={key === tab}
            aria-controls="usage-tabpanel"
            tabIndex={key === tab ? 0 : -1}
            onClick={() => setTab(key)}
            onKeyDown={(e) => {
              const i = USAGE_TABS.indexOf(key)
              const next = e.key === 'ArrowRight' ? USAGE_TABS[(i + 1) % USAGE_TABS.length] : e.key === 'ArrowLeft' ? USAGE_TABS[(i - 1 + USAGE_TABS.length) % USAGE_TABS.length] : null
              if (next) {
                e.preventDefault()
                setTab(next)
                document.getElementById(`usage-tab-${next}`)?.focus()
              }
            }}
            className={`-mb-px min-h-11 whitespace-nowrap border-b-2 px-4 py-2 text-sm font-semibold ${key === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}
          >
            {t(`tab.${key}`)}
          </button>
        ))}
      </div>
      <section id="usage-tabpanel" role="tabpanel" aria-labelledby={`usage-tab-${tab}`} className="flex flex-col gap-4">
        <Active range={range} interval={interval} />
      </section>
    </div>
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
    <section id="user-timeline-section" aria-labelledby="user-timeline" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <h2 id="user-timeline" className="font-semibold">{t('timeline')}</h2>
      <p className="text-sm text-muted">{t('timelineLead')}</p>
      <form className="flex flex-col gap-2 sm:flex-row" onSubmit={(e) => { e.preventDefault(); void look() }}>
        <label className="flex min-w-0 flex-1 flex-col gap-1">
          <span className="sr-only">{t('userId')}</span>
          <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder={t('userId')} />
        </label>
        <Button type="submit" disabled={busy}>{t('lookUp')}</Button>
      </form>
      {error ? <p role="alert" className="text-sm text-bad">{error}</p> : null}
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
