'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState, type ReactNode } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { AdminMetricsDocument, type AdminMetricsQuery } from '@/graphql/generated/graphql'
import { aiRangeIssue, aiRangeVariables, failureRate, formatBytes, formatDecimal, microUsdToUsd, providerLabel } from '@/features/admin/metrics'

type Metrics = AdminMetricsQuery['adminMetrics']
type UsageRow = { tasksRun: number; failures: number; promptTokens: string; completionTokens: string; costMicroUsd: string }

export function AdminOverview() {
  const t = useTranslations('adminOverview')
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [applied, setApplied] = useState<{ from: string; to: string } | null>(null)
  const [rangeError, setRangeError] = useState<string | null>(null)
  const { data, error, previousData } = useQuery(AdminMetricsDocument, {
    variables: applied ? aiRangeVariables(applied.from, applied.to) : {},
    fetchPolicy: 'cache-and-network',
  })
  const metrics = data?.adminMetrics ?? previousData?.adminMetrics

  const apply = () => {
    const issue = aiRangeIssue(from, to)
    if (issue) {
      setRangeError(t(`range.${issue}`))
      return
    }
    setRangeError(null)
    setApplied(from && to ? { from, to } : null)
  }
  const clear = () => {
    setFrom('')
    setTo('')
    setRangeError(null)
    setApplied(null)
  }

  if (CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')) return <p className="text-muted">{t('notAllowed')}</p>
  if (!metrics) return error ? <Alert tone="error">{t('failed')}</Alert> : <p className="text-muted">{t('loading')}</p>

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
        <p className="text-sm text-muted">{t('generatedAt', { when: formatWhen(metrics.generatedAt) })}</p>
      </header>

      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        <Users metrics={metrics} />
        <Content metrics={metrics} />
        <Storage metrics={metrics} />
        <Verification metrics={metrics} />
        <Moderation metrics={metrics} />
      </div>

      <AiUsage metrics={metrics} from={from} to={to} rangeError={rangeError} onFrom={setFrom} onTo={setTo} onApply={apply} onClear={clear} />
    </div>
  )
}

function formatWhen(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return new Intl.DateTimeFormat('en', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}

function Card({ title, href, link, children }: { title: string; href: string; link: string; children: ReactNode }) {
  const id = title.toLowerCase().replace(/[^a-z]+/g, '-')
  return (
    <section aria-labelledby={id} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex items-start justify-between gap-3">
        <h2 id={id} className="text-sm font-semibold text-muted">
          {title}
        </h2>
        <Link href={href} className="shrink-0 text-sm font-medium text-accent">
          {link}
        </Link>
      </div>
      {children}
    </section>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="min-w-0">
      <dt className="text-xs text-muted">{label}</dt>
      <dd className="truncate text-lg font-semibold tracking-tight">{value}</dd>
    </div>
  )
}

function Users({ metrics }: { metrics: Metrics }) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  const n = (v: number) => format.number(v)
  return (
    <Card title={t('users')} href="/admin/settings#accounts" link={t('usersLink')}>
      <p className="text-3xl font-extrabold tracking-tight">{n(metrics.users.total)}</p>
      <dl className="grid grid-cols-3 gap-2">
        <Stat label={t('new7')} value={n(metrics.users.newLast7Days)} />
        <Stat label={t('new30')} value={n(metrics.users.newLast30Days)} />
        <Stat label={t('activeUsers')} value={n(metrics.users.active)} />
      </dl>
    </Card>
  )
}

function Content({ metrics }: { metrics: Metrics }) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  const n = (v: number) => format.number(v)
  const c = metrics.content
  return (
    <Card title={t('content')} href="/admin/moderation" link={t('contentLink')}>
      <dl className="grid grid-cols-2 gap-2">
        <Stat label={t('notes')} value={n(c.notes)} />
        <Stat label={t('publicNotes')} value={n(c.publicNotes)} />
        <Stat label={t('subjects')} value={n(c.subjects)} />
        <Stat label={t('topics')} value={n(c.topics)} />
        <Stat label={t('groups')} value={n(c.groups)} />
        <Stat label={t('classrooms')} value={n(c.classrooms)} />
      </dl>
    </Card>
  )
}

function Storage({ metrics }: { metrics: Metrics }) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  return (
    <Card title={t('storage')} href="/admin/settings#uploads" link={t('storageLink')}>
      <p className="text-3xl font-extrabold tracking-tight">{formatBytes(metrics.storage.bytes)}</p>
      <p className="text-sm text-muted">{t('files', { count: format.number(metrics.storage.files) })}</p>
    </Card>
  )
}

function Verification({ metrics }: { metrics: Metrics }) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  const n = (v: number) => format.number(v)
  const v = metrics.verification
  return (
    <Card title={t('verification')} href="/admin/verification" link={t('verificationLink')}>
      <dl className="grid grid-cols-3 gap-2">
        <Stat label={t('studentIdQueue')} value={n(v.studentIdQueue)} />
        <Stat label={t('pendingRequests')} value={n(v.pendingRequests)} />
        <Stat label={t('domainReviews')} value={n(v.domainReviews)} />
      </dl>
    </Card>
  )
}

function Moderation({ metrics }: { metrics: Metrics }) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  return (
    <Card title={t('moderation')} href="/admin/moderation" link={t('moderationLink')}>
      <dl className="grid grid-cols-2 gap-2">
        <Stat label={t('openReports')} value={format.number(metrics.moderation.openReports)} />
        <Stat label={t('openAppeals')} value={format.number(metrics.moderation.openAppeals)} />
      </dl>
    </Card>
  )
}

function AiUsage({
  metrics,
  from,
  to,
  rangeError,
  onFrom,
  onTo,
  onApply,
  onClear,
}: {
  metrics: Metrics
  from: string
  to: string
  rangeError: string | null
  onFrom: (v: string) => void
  onTo: (v: string) => void
  onApply: () => void
  onClear: () => void
}) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  const ai = metrics.ai
  const rate = failureRate(ai.failures, ai.tasksRun)
  return (
    <section aria-labelledby="admin-ai-usage" className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 id="admin-ai-usage" className="text-lg font-semibold">
            {t('ai')}
          </h2>
          <p className="text-sm text-muted">{t('showing', { from: formatWhen(ai.from), to: formatWhen(ai.to) })}</p>
        </div>
        <Link href="/admin/ai" className="text-sm font-medium text-accent">
          {t('aiLink')}
        </Link>
      </div>

      <form
        className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end"
        onSubmit={(e) => {
          e.preventDefault()
          onApply()
        }}
      >
        <Field label={t('from')}>
          <Input type="date" value={from} onChange={(e) => onFrom(e.target.value)} />
        </Field>
        <Field label={t('to')}>
          <Input type="date" value={to} onChange={(e) => onTo(e.target.value)} />
        </Field>
        <div className="flex gap-2">
          <Button type="submit" variant="secondary">
            {t('apply')}
          </Button>
          <Button type="button" variant="ghost" onClick={onClear}>
            {t('clear')}
          </Button>
        </div>
      </form>
      {rangeError ? <Alert tone="error">{rangeError}</Alert> : null}
      {!from && !to ? <p className="text-xs text-muted">{t('last30')}</p> : null}

      <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Stat label={t('tasks')} value={format.number(ai.tasksRun)} />
        <Stat label={t('failures')} value={format.number(ai.failures)} />
        <Stat label={t('failureRate')} value={format.number(rate, { style: 'percent', maximumFractionDigits: 1 })} />
        <Stat label={t('cost')} value={usd(ai.costMicroUsd, format)} />
      </dl>
      <dl className="grid gap-3 sm:grid-cols-2">
        <Stat label={t('promptTokens')} value={formatDecimal(ai.promptTokens)} />
        <Stat label={t('completionTokens')} value={formatDecimal(ai.completionTokens)} />
      </dl>

      <UsageTable title={t('byProvider')} rows={ai.byProvider.map((row) => ({ ...row, name: providerLabel(row.provider) }))} />
      <UsageTable title={t('byModel')} rows={ai.byModel.map((row) => ({ ...row, name: `${providerLabel(row.provider)} · ${row.model}` }))} />
      <UsageTable title={t('byTask')} rows={ai.byTask.map((row) => ({ ...row, name: row.task }))} />
    </section>
  )
}

function usd(micro: string, format: ReturnType<typeof useFormatter>): string {
  const dollars = microUsdToUsd(micro)
  if (dollars == null) return micro
  const abs = Math.abs(dollars)
  return format.number(dollars, { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: abs > 0 && abs < 0.01 ? 6 : 2 })
}

function UsageTable({ title, rows }: { title: string; rows: (UsageRow & { name: string })[] }) {
  const t = useTranslations('adminOverview')
  const format = useFormatter()
  const max = Math.max(1, ...rows.map((row) => row.tasksRun))
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-sm font-semibold">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-muted">{t('noUsage')}</p>
      ) : (
        <div className="overflow-x-auto" tabIndex={0} aria-label={title}>
          <table className="w-full min-w-[36rem] border-collapse text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted">
                <th scope="col" className="py-2 pr-3 font-medium">{t('name')}</th>
                <th scope="col" className="py-2 pr-3 font-medium">{t('tasks')}</th>
                <th scope="col" className="py-2 pr-3 font-medium">{t('failures')}</th>
                <th scope="col" className="py-2 pr-3 font-medium">{t('failureRate')}</th>
                <th scope="col" className="py-2 pr-3 font-medium">{t('tokens')}</th>
                <th scope="col" className="py-2 font-medium">{t('cost')}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => {
                const width = Math.round((row.tasksRun / max) * 100)
                return (
                  <tr key={row.name} className="border-b border-border last:border-0">
                    <th scope="row" className="py-2 pr-3 font-medium">
                      <span className="block">{row.name}</span>
                      <span className="mt-1 block h-1.5 overflow-hidden rounded-full bg-surface-2" role="img" aria-label={t('bar', { name: row.name, count: format.number(row.tasksRun) })}>
                        <span className="block h-full rounded-full bg-accent" style={{ width: `${width}%` }} />
                      </span>
                    </th>
                    <td className="py-2 pr-3">{format.number(row.tasksRun)}</td>
                    <td className="py-2 pr-3">{format.number(row.failures)}</td>
                    <td className="py-2 pr-3">{format.number(failureRate(row.failures, row.tasksRun), { style: 'percent', maximumFractionDigits: 1 })}</td>
                    <td className="py-2 pr-3">{formatDecimal(row.promptTokens)} + {formatDecimal(row.completionTokens)}</td>
                    <td className="py-2">{usd(row.costMicroUsd, format)}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
