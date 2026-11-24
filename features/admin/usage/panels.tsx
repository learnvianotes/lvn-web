'use client'

/** The tabs of the admin usage dashboard. Each tab runs only its own queries, and only while it is open. */
import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useQuery } from '@apollo/client/react'
import { useFormatter, useTranslations } from 'next-intl'
import { useState, type ReactNode } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import {
  AdminUsageContentDocument,
  AdminUsageDocument,
  AdminUsageEngagementDocument,
  AdminUsageFeaturesDocument,
  AdminUsageFunnelDocument,
  AdminUsageGrowthDocument,
  AdminUsageOverviewDocument,
  AdminUsageRetentionDocument,
  AdminUsageSearchQualityDocument,
  AdminUsageSubjectsDocument,
  AdminUsageVerificationDocument,
  AdminUsageVersionsDocument,
  type AdminSubjectMetric,
  type MetricsInterval,
} from '@/graphql/generated/graphql'
import { formatBytes } from '@/features/admin/metrics'
import { BarList, LineChart, RetentionHeatmap } from './charts'
import { contentCsv, engagementCsv, featuresCsv, funnelCsv, growthCsv, overviewCsv, retentionCsv, searchQualityCsv, subjectsCsv, verificationCsv, versionsCsv } from './csv'
import { csvFileName, downloadCsv, funnelRows, istToday, rangeVariables, share, toCsv, valueOn, withShares, type CsvTable, type DayRange } from './shape'

export const USAGE_TABS = ['overview', 'growth', 'engagement', 'content', 'subjects', 'retention', 'verification', 'funnel', 'features', 'search', 'versions'] as const
export type UsageTab = (typeof USAGE_TABS)[number]

/** Database steps the API knows (adminFunnel, ADR-0105). */
export const FUNNEL_STEPS = ['signed_up', 'email_verified', 'first_note', 'returned_d7'] as const
export const SUBJECT_METRICS: AdminSubjectMetric[] = ['NOTES', 'LEARNING_TIME', 'SAVES']
export const RETENTION_WEEKS = 12

export type PanelProps = { range: DayRange; interval: MetricsInterval }

function forbidden(error: unknown): boolean {
  return CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')
}

/** Loading, refusal and failure for a tab; the content once there is data. */
function Panel({ tab, error, loading, hasData, onRetry, children }: { tab: UsageTab; error: unknown; loading: boolean; hasData: boolean; onRetry: () => void; children: ReactNode }) {
  const t = useTranslations('adminUsage')
  if (forbidden(error)) return <p className="text-muted">{t('notAllowed')}</p>
  if (!hasData) {
    if (error)
      return (
        <Alert tone="error">
          {t('failed')}{' '}
          <button type="button" className="font-medium text-accent underline" onClick={onRetry}>{t('retry')}</button>
        </Alert>
      )
    return <p className="text-muted" aria-busy={loading} data-testid={`loading-${tab}`}>{t('loading')}</p>
  }
  return <div className="flex flex-col gap-4">{children}</div>
}

/** The toolbar row of a tab: when the figures were made and a CSV of them. */
function TabFooter({ tab, generatedAt, tables, range }: { tab: UsageTab; generatedAt?: string | null; tables: CsvTable[]; range?: DayRange }) {
  const t = useTranslations('adminUsage')
  const format = useFormatter()
  return (
    <div className="flex flex-wrap items-center justify-between gap-2">
      <p className="text-xs text-muted">{generatedAt ? t('generatedAt', { when: format.dateTime(new Date(generatedAt), { dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Kolkata' }) }) : null}</p>
      <Button variant="secondary" size="sm" type="button" onClick={() => downloadCsv(csvFileName(tab, range), toCsv(tables))}>
        {t('exportCsv')}
      </Button>
    </div>
  )
}

/** "N small groups hidden" under any breakdown the API trimmed for k-anonymity (fewer than 5 people). */
export function HiddenGroups({ count }: { count: number }) {
  const t = useTranslations('adminUsage')
  if (!count) return null
  return <p className="text-xs text-muted" data-testid="hidden-groups">{t('hiddenGroups', { count })}</p>
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-2xl border border-border bg-surface p-4">
      <dt className="text-sm text-muted">{label}</dt>
      <dd className="text-2xl font-semibold">{value}</dd>
      {hint ? <dd className="text-xs text-muted">{hint}</dd> : null}
    </div>
  )
}

function Stats({ children }: { children: ReactNode }) {
  return <dl className="grid gap-3 [grid-template-columns:repeat(auto-fit,minmax(min(100%,11rem),1fr))]">{children}</dl>
}

function useFormat() {
  const format = useFormatter()
  return {
    n: (v: number) => format.number(v),
    pct: (v: number | null) => (v === null ? '—' : format.number(v, { style: 'percent', maximumFractionDigits: 1 })),
    hours: (v: number | null | undefined) => (v === null || v === undefined ? '—' : format.number(v, { maximumFractionDigits: 1 })),
  }
}

// --- Overview ---------------------------------------------------------------------------------------------------

export function OverviewPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const vars = rangeVariables(range)
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageOverviewDocument, { variables: vars, fetchPolicy: 'cache-and-network' })
  const usage = useQuery(AdminUsageDocument, { variables: vars, fetchPolicy: 'cache-and-network' })
  const shown = data ?? previousData
  const summary = (usage.data ?? usage.previousData)?.adminUsage ?? null
  const today = istToday()
  const newToday = shown && range.to === today ? valueOn(shown.adminGrowth.series, today, (p) => p.signUps) : null
  return (
    <Panel tab="overview" error={error} loading={loading} hasData={!!shown} onRetry={() => void refetch()}>
      {shown ? (
        <>
          <Stats>
            <Stat label={t('kpi.users')} value={f.n(shown.adminMetrics.users.total)} hint={t('kpi.active', { count: shown.adminMetrics.users.active })} />
            <Stat label={t('kpi.newToday')} value={newToday === null ? '—' : f.n(newToday)} hint={newToday === null ? t('kpi.newTodayHint') : undefined} />
            <Stat label={t('kpi.new7')} value={f.n(shown.adminMetrics.users.newLast7Days)} />
            <Stat label={t('dau')} value={f.n(shown.adminEngagement.dau)} />
            <Stat label={t('wau')} value={f.n(shown.adminEngagement.wau)} />
            <Stat label={t('mau')} value={f.n(shown.adminEngagement.mau)} />
            <Stat label={t('kpi.stickiness')} value={f.pct(shown.adminEngagement.stickiness)} hint={t('kpi.stickinessHint')} />
            <Stat label={t('kpi.verified')} value={f.pct(share(shown.adminGrowth.totals.verifications, shown.adminGrowth.totals.signUps))} hint={t('kpi.verifiedHint')} />
          </Stats>
          {summary ? (
            <div className="grid gap-4 lg:grid-cols-2">
              <BarList title={t('pages')} valueLabel={t('count')} bars={summary.topFeatures.map((r) => ({ key: r.name, label: r.name, value: r.count }))} />
              <BarList title={t('features')} valueLabel={t('count')} bars={summary.topEvents.map((r) => ({ key: r.name, label: r.name, value: r.count }))} />
            </div>
          ) : null}
          <TabFooter tab="overview" generatedAt={shown.adminMetrics.generatedAt} tables={overviewCsv(shown, summary, newToday)} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

// --- Growth -----------------------------------------------------------------------------------------------------

export function GrowthPanel({ range, interval }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageGrowthDocument, { variables: { ...rangeVariables(range), interval }, fetchPolicy: 'cache-and-network' })
  const g = (data ?? previousData)?.adminGrowth
  return (
    <Panel tab="growth" error={error} loading={loading} hasData={!!g} onRetry={() => void refetch()}>
      {g ? (
        <>
          <Stats>
            <Stat label={t('growth.signUps')} value={f.n(g.totals.signUps)} />
            <Stat label={t('growth.emailVerified')} value={f.n(g.totals.emailVerified)} />
            <Stat label={t('growth.registrations')} value={f.n(g.totals.registrationsCompleted)} />
            <Stat label={t('growth.verifications')} value={f.n(g.totals.verifications)} />
          </Stats>
          <LineChart
            title={t('growth.chart')}
            dates={g.series.map((p) => p.date)}
            series={[
              { key: 'signUps', label: t('growth.signUps'), values: g.series.map((p) => p.signUps) },
              { key: 'registrations', label: t('growth.registrations'), values: g.series.map((p) => p.registrationsCompleted) },
              { key: 'verifications', label: t('growth.verifications'), values: g.series.map((p) => p.verifications) },
            ]}
          />
          <BarList
            title={t('growth.methods')}
            valueLabel={t('people')}
            bars={withShares(g.signUpMethods, (r) => r.users).map(({ row, value, share: s }) => ({ key: row.method, label: t(`method.${row.method}`), value, display: `${f.n(value)} (${f.pct(s)})` }))}
          />
          <HiddenGroups count={g.hiddenSmallGroups} />
          <TabFooter tab="growth" generatedAt={g.generatedAt} tables={growthCsv({ adminGrowth: g })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

// --- Engagement -------------------------------------------------------------------------------------------------

export function EngagementPanel({ range, interval }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageEngagementDocument, { variables: { ...rangeVariables(range), interval }, fetchPolicy: 'cache-and-network' })
  const e = (data ?? previousData)?.adminEngagement
  return (
    <Panel tab="engagement" error={error} loading={loading} hasData={!!e} onRetry={() => void refetch()}>
      {e ? (
        <>
          <Stats>
            <Stat label={t('dau')} value={f.n(e.dau)} />
            <Stat label={t('wau')} value={f.n(e.wau)} />
            <Stat label={t('mau')} value={f.n(e.mau)} />
            <Stat label={t('kpi.stickiness')} value={f.pct(e.stickiness)} />
          </Stats>
          <LineChart title={t('engagement.active')} dates={e.series.map((p) => p.date)} series={[{ key: 'active', label: t('engagement.activeUsers'), values: e.series.map((p) => p.activeUsers) }]} />
          <LineChart
            title={t('engagement.learning')}
            dates={e.series.map((p) => p.date)}
            series={[
              { key: 'minutes', label: t('engagement.learningMinutes'), values: e.series.map((p) => p.learningMinutes) },
              { key: 'quizzes', label: t('engagement.quizAttempts'), values: e.series.map((p) => p.quizAttempts) },
            ]}
          />
          <TabFooter tab="engagement" generatedAt={e.generatedAt} tables={engagementCsv({ adminEngagement: e })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

// --- Content ----------------------------------------------------------------------------------------------------

export function ContentPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageContentDocument, { variables: rangeVariables(range), fetchPolicy: 'cache-and-network' })
  const c = (data ?? previousData)?.adminContentStats
  return (
    <Panel tab="content" error={error} loading={loading} hasData={!!c} onRetry={() => void refetch()}>
      {c ? (
        <>
          <h3 className="font-semibold">{t('content.notes')}</h3>
          <Stats>
            <Stat label={t('content.created')} value={f.n(c.notes.created)} />
            <Stat label={t('content.public')} value={f.n(c.notes.public)} />
            <Stat label={t('content.shared')} value={f.n(c.notes.shared)} />
            <Stat label={t('content.unlisted')} value={f.n(c.notes.unlisted)} />
            <Stat label={t('content.private')} value={f.n(c.notes.private)} />
          </Stats>
          <h3 className="font-semibold">{t('content.uploads')}</h3>
          <Stats>
            <Stat label={t('content.files')} value={f.n(c.uploads.files)} />
            <Stat label={t('content.bytes')} value={formatBytes(c.uploads.bytes)} />
            <Stat label={t('content.scansFlagged')} value={f.n(c.scans.infected)} hint={t('content.scansHint', { clean: c.scans.clean, pending: c.scans.pending, failed: c.scans.failed })} />
          </Stats>
          <BarList
            title={t('content.byPurpose')}
            valueLabel={t('content.files')}
            bars={[...c.uploads.byPurpose].sort((a, b) => b.files - a.files).map((r) => ({ key: r.purpose, label: r.purpose, value: r.files, display: `${f.n(r.files)} · ${formatBytes(r.bytes)}` }))}
          />
          <HiddenGroups count={c.uploads.hiddenSmallGroups} />
          <h3 className="font-semibold">{t('content.doubts')}</h3>
          <Stats>
            <Stat label={t('content.asked')} value={f.n(c.doubts.asked)} />
            <Stat label={t('content.answered')} value={f.n(c.doubts.answered)} />
            <Stat label={t('content.resolved')} value={f.n(c.doubts.resolved)} />
            <Stat label={t('content.answers')} value={f.n(c.doubts.answers)} />
            <Stat label={t('content.medianAnswer')} value={f.hours(c.doubts.medianHoursToFirstAnswer)} />
          </Stats>
          <h3 className="font-semibold">{t('content.places')}</h3>
          <Stats>
            <Stat label={t('content.groups')} value={f.n(c.places.groups)} hint={t('content.posts', { count: c.places.groupPosts })} />
            <Stat label={t('content.classrooms')} value={f.n(c.places.classrooms)} hint={t('content.posts', { count: c.places.classroomPosts })} />
            <Stat label={t('content.noteShares')} value={f.n(c.sharing.noteShares)} />
            <Stat label={t('content.saves')} value={f.n(c.sharing.saves)} />
          </Stats>
          <TabFooter tab="content" generatedAt={c.generatedAt} tables={contentCsv({ adminContentStats: c })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

// --- Subjects ---------------------------------------------------------------------------------------------------

export function SubjectsPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const [by, setBy] = useState<AdminSubjectMetric>('NOTES')
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageSubjectsDocument, { variables: { ...rangeVariables(range), by, first: 20 }, fetchPolicy: 'cache-and-network' })
  const s = (data ?? previousData)?.adminTopSubjects
  return (
    <div className="flex flex-col gap-4">
      <fieldset className="flex flex-wrap items-center gap-2">
        <legend className="sr-only">{t('subjects.by')}</legend>
        {SUBJECT_METRICS.map((m) => (
          <Button key={m} type="button" size="sm" variant={m === by ? 'primary' : 'secondary'} aria-pressed={m === by} onClick={() => setBy(m)}>
            {t(`subjects.metric.${m}`)}
          </Button>
        ))}
      </fieldset>
      <Panel tab="subjects" error={error} loading={loading} hasData={!!s} onRetry={() => void refetch()}>
        {s ? (
          <>
            <div className="overflow-x-auto rounded-2xl border border-border bg-surface p-4">
              <table className="w-full text-left text-sm">
                <caption className="pb-2 text-left font-semibold">{t('subjects.caption', { metric: t(`subjects.metric.${s.by}`) })}</caption>
                <thead>
                  <tr>
                    <th scope="col" className="border-b border-border px-2 py-1 font-medium text-muted">#</th>
                    <th scope="col" className="border-b border-border px-2 py-1 font-medium text-muted">{t('subjects.subject')}</th>
                    <th scope="col" className="border-b border-border px-2 py-1 text-right font-medium text-muted">{t(`subjects.metric.${s.by}`)}</th>
                    <th scope="col" className="border-b border-border px-2 py-1 text-right font-medium text-muted">{t('people')}</th>
                  </tr>
                </thead>
                <tbody>
                  {s.subjects.map((row, i) => (
                    <tr key={row.subjectId}>
                      <td className="px-2 py-1 text-muted">{i + 1}</td>
                      <th scope="row" className="px-2 py-1 font-normal">{row.title}</th>
                      <td className="px-2 py-1 text-right font-medium">{f.n(row.value)}</td>
                      <td className="px-2 py-1 text-right">{f.n(row.users)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!s.subjects.length ? <p className="pt-2 text-sm text-muted">{t('chart.empty')}</p> : null}
            </div>
            <HiddenGroups count={s.hiddenSmallGroups} />
            <TabFooter tab="subjects" generatedAt={s.generatedAt} tables={subjectsCsv({ adminTopSubjects: s })} range={range} />
          </>
        ) : null}
      </Panel>
    </div>
  )
}

// --- Retention --------------------------------------------------------------------------------------------------

export function RetentionPanel() {
  const t = useTranslations('adminUsage')
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageRetentionDocument, { variables: { weeks: RETENTION_WEEKS }, fetchPolicy: 'cache-and-network' })
  const r = (data ?? previousData)?.adminRetention
  return (
    <Panel tab="retention" error={error} loading={loading} hasData={!!r} onRetry={() => void refetch()}>
      {r ? (
        <>
          <p className="text-sm text-muted">{t('retention.lead', { first: r.firstWeek, last: r.lastWeek })}</p>
          {r.cohorts.length ? <RetentionHeatmap cohorts={r.cohorts} /> : <p className="text-sm text-muted">{t('chart.empty')}</p>}
          <HiddenGroups count={r.hiddenSmallGroups} />
          <TabFooter tab="retention" generatedAt={r.generatedAt} tables={retentionCsv({ adminRetention: r })} />
        </>
      ) : null}
    </Panel>
  )
}

// --- Verification -----------------------------------------------------------------------------------------------

export function VerificationPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageVerificationDocument, { variables: rangeVariables(range), fetchPolicy: 'cache-and-network' })
  const v = (data ?? previousData)?.adminVerificationStats
  return (
    <Panel tab="verification" error={error} loading={loading} hasData={!!v} onRetry={() => void refetch()}>
      {v ? (
        <>
          <Stats>
            <Stat label={t('verification.pending')} value={f.n(v.pending)} hint={t('verification.oldest', { hours: f.hours(v.oldestPendingHours) })} />
            <Stat label={t('verification.requested')} value={f.n(v.requested)} />
            <Stat label={t('verification.approved')} value={f.n(v.approved)} hint={f.pct(share(v.approved, v.approved + v.rejected))} />
            <Stat label={t('verification.rejected')} value={f.n(v.rejected)} />
            <Stat label={t('verification.median')} value={f.hours(v.medianHoursToDecision)} />
          </Stats>
          <div className="overflow-x-auto rounded-2xl border border-border bg-surface p-4">
            <table className="w-full text-left text-sm">
              <caption className="pb-2 text-left font-semibold">{t('verification.byMethod')}</caption>
              <thead>
                <tr>
                  {['method', 'requested', 'approved', 'rejected'].map((h) => (
                    <th key={h} scope="col" className="border-b border-border px-2 py-1 font-medium text-muted">{t(`verification.${h}`)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {v.byMethod.map((row) => (
                  <tr key={row.method}>
                    <th scope="row" className="px-2 py-1 font-normal">{t(`verificationMethod.${row.method}`)}</th>
                    <td className="px-2 py-1">{f.n(row.requested)}</td>
                    <td className="px-2 py-1">{f.n(row.approved)}</td>
                    <td className="px-2 py-1">{f.n(row.rejected)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!v.byMethod.length ? <p className="pt-2 text-sm text-muted">{t('chart.empty')}</p> : null}
          </div>
          <HiddenGroups count={v.hiddenSmallGroups} />
          <TabFooter tab="verification" generatedAt={v.generatedAt} tables={verificationCsv({ adminVerificationStats: v })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

// --- Funnel -----------------------------------------------------------------------------------------------------

export function FunnelPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageFunnelDocument, {
    variables: { since: rangeVariables(range).from, steps: [...FUNNEL_STEPS] },
    fetchPolicy: 'cache-and-network',
  })
  const steps = (data ?? previousData)?.adminFunnel
  return (
    <Panel tab="funnel" error={error} loading={loading} hasData={!!steps} onRetry={() => void refetch()}>
      {steps ? (
        <>
          <p className="text-sm text-muted">{t('funnel.lead', { since: range.from })}</p>
          <BarList
            title={t('funnel.title')}
            valueLabel={t('people')}
            bars={funnelRows(steps).map((row) => ({
              key: row.name,
              label: t.has(`funnel.step.${row.name}`) ? t(`funnel.step.${row.name}`) : row.name,
              value: row.users,
              display: row.ofPrevious === null ? f.n(row.users) : `${f.n(row.users)} (${f.pct(row.ofPrevious)} · ${f.pct(row.ofFirst)})`,
            }))}
            note={t('funnel.note')}
          />
          <TabFooter tab="funnel" tables={funnelCsv({ adminFunnel: steps })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

// --- First-party events v2 (lvn-backend ADR-0107) ---------------------------------------------------------------

/** A plain table of aggregates, with a caption and an empty note. */
function CountTable({ caption, header, rows }: { caption: string; header: string[]; rows: { key: string; cells: ReactNode[] }[] }) {
  const t = useTranslations('adminUsage')
  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-surface p-4">
      <table className="w-full text-left text-sm">
        <caption className="pb-2 text-left font-semibold">{caption}</caption>
        <thead>
          <tr>
            {header.map((h, i) => (
              <th key={h} scope="col" className={`border-b border-border px-2 py-1 font-medium text-muted${i ? ' text-right' : ''}`}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key}>
              {row.cells.map((cell, i) =>
                i ? (
                  <td key={i} className="px-2 py-1 text-right">{cell}</td>
                ) : (
                  <th key={i} scope="row" className="px-2 py-1 font-normal">{cell}</th>
                ),
              )}
            </tr>
          ))}
        </tbody>
      </table>
      {!rows.length ? <p className="pt-2 text-sm text-muted">{t('chart.empty')}</p> : null}
    </div>
  )
}

/** A wire id shown by its label when the messages have one, else as it is. */
function useLabel(prefix: string) {
  const t = useTranslations('adminUsage')
  return (id: string) => (t.has(`${prefix}.${id}`) ? t(`${prefix}.${id}`) : id)
}

export function FeaturesPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const feature = useLabel('featureName')
  const quiz = useLabel('quizKind')
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageFeaturesDocument, { variables: rangeVariables(range), fetchPolicy: 'cache-and-network' })
  const u = (data ?? previousData)?.adminFeatureUsage
  return (
    <Panel tab="features" error={error} loading={loading} hasData={!!u} onRetry={() => void refetch()}>
      {u ? (
        <>
          <Stats>
            <Stat label={t('featureUse.events')} value={f.n(u.events)} />
            <Stat label={t('featureUse.quizStarts')} value={f.n(u.quizStarts.starts)} />
          </Stats>
          <BarList
            title={t('featureUse.title')}
            valueLabel={t('people')}
            bars={u.features.map((row) => ({ key: row.feature, label: feature(row.feature.toLowerCase()), value: row.users, display: t('featureUse.peopleEvents', { users: f.n(row.users), events: f.n(row.events) }) }))}
            note={t('featureUse.note')}
          />
          <HiddenGroups count={u.hiddenSmallGroups} />
          <CountTable
            caption={t('featureUse.quizTitle')}
            header={[t('featureUse.kind'), t('featureUse.starts'), t('people')]}
            rows={u.quizStarts.byKind.map((row) => ({ key: row.kind, cells: [quiz(row.kind.toLowerCase()), f.n(row.starts), f.n(row.users)] }))}
          />
          <HiddenGroups count={u.quizStarts.hiddenSmallGroups} />
          <TabFooter tab="features" generatedAt={u.generatedAt} tables={featuresCsv({ adminFeatureUsage: u })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

export function SearchQualityPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const scope = useLabel('searchScope')
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageSearchQualityDocument, { variables: rangeVariables(range), fetchPolicy: 'cache-and-network' })
  const q = (data ?? previousData)?.adminSearchQuality
  return (
    <Panel tab="search" error={error} loading={loading} hasData={!!q} onRetry={() => void refetch()}>
      {q ? (
        <>
          <Stats>
            <Stat label={t('searchQuality.searches')} value={f.n(q.searches)} />
            <Stat label={t('searchQuality.zeroResults')} value={f.n(q.zeroResults)} />
            <Stat label={t('searchQuality.zeroRate')} value={f.pct(q.zeroResultRate ?? null)} hint={t('searchQuality.zeroRateHint')} />
          </Stats>
          <CountTable
            caption={t('searchQuality.byScope')}
            header={[t('searchQuality.scope'), t('searchQuality.searches'), t('searchQuality.zeroResults'), t('searchQuality.zeroRate'), t('people')]}
            rows={q.byScope.map((row) => ({
              key: row.scope ?? 'none',
              cells: [row.scope ? scope(row.scope.toLowerCase()) : t('searchQuality.noScope'), f.n(row.searches), f.n(row.zeroResults), f.pct(row.zeroResultRate ?? null), f.n(row.users)],
            }))}
          />
          <p className="text-xs text-muted">{t('searchQuality.note')}</p>
          <HiddenGroups count={q.hiddenSmallGroups} />
          <TabFooter tab="search" generatedAt={q.generatedAt} tables={searchQualityCsv({ adminSearchQuality: q })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}

export function VersionsPanel({ range }: PanelProps) {
  const t = useTranslations('adminUsage')
  const f = useFormat()
  const { data, previousData, error, loading, refetch } = useQuery(AdminUsageVersionsDocument, { variables: rangeVariables(range), fetchPolicy: 'cache-and-network' })
  const v = (data ?? previousData)?.adminVersionAdoption
  return (
    <Panel tab="versions" error={error} loading={loading} hasData={!!v} onRetry={() => void refetch()}>
      {v ? (
        <>
          {v.platforms.map((p) => (
            <CountTable
              key={p.platform}
              caption={t('versions.platform', { platform: t.has(`versions.platformName.${p.platform}`) ? t(`versions.platformName.${p.platform}`) : p.platform, users: f.n(p.users), events: f.n(p.events) })}
              header={[t('versions.version'), t('people'), t('versions.share'), t('versions.events')]}
              rows={p.versions.map((row) => ({ key: row.appVersion ?? 'none', cells: [row.appVersion ?? t('versions.none'), f.n(row.users), f.pct(row.share), f.n(row.events)] }))}
            />
          ))}
          {!v.platforms.length ? <p className="text-sm text-muted">{t('chart.empty')}</p> : null}
          <p className="text-xs text-muted">{t('versions.note')}</p>
          <HiddenGroups count={v.hiddenSmallGroups} />
          <TabFooter tab="versions" generatedAt={v.generatedAt} tables={versionsCsv({ adminVersionAdoption: v })} range={range} />
        </>
      ) : null}
    </Panel>
  )
}
