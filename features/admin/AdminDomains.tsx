'use client'

import { useCallback, useEffect, useState } from 'react'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { decideInstitutionDomain, listInstitutionDomains, PlatformError, type InstitutionDomain } from '@/lib/platform-api'

/** Institution email domains waiting for a decision, and the ones already allowed. */
export function AdminDomains() {
  const t = useTranslations('adminDomains')
  const format = useFormatter()
  const { role, ready } = useViewerRole()
  const [rows, setRows] = useState<InstitutionDomain[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const load = useCallback(async () => {
    try {
      setRows(await listInstitutionDomains())
      setError(null)
    } catch (e) {
      setRows([])
      setError(e instanceof PlatformError && e.forbidden ? t('notAllowed') : t('failed'))
    }
  }, [t])
  useEffect(() => {
    if (ready && canSeeSection(role, 'domains')) void load()
  }, [ready, role, load])
  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!canSeeSection(role, 'domains')) return <p className="text-muted">{t('notAllowed')}</p>
  const queue = (rows ?? []).filter((row) => row.status === 'NEEDS_REVIEW' || row.status === 'ACADEMIC_QUEUED')
  const approved = (rows ?? []).filter((row) => row.status === 'APPROVED')
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      <section aria-labelledby="domain-queue" className="flex flex-col gap-3">
        <h2 id="domain-queue" className="text-lg font-semibold">{t('queue')}</h2>
        {rows && !queue.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
        <ul className="flex flex-col gap-3">
          {queue.map((row) => (
            <DomainRow key={row.domain} row={row} when={format.dateTime(new Date(row.firstSeenAt), { dateStyle: 'medium' })} onDone={() => void load()} />
          ))}
        </ul>
      </section>
      <section aria-labelledby="domain-approved" className="flex flex-col gap-3">
        <h2 id="domain-approved" className="text-lg font-semibold">{t('approved')}</h2>
        {rows && !approved.length ? <p className="text-sm text-muted">{t('noApproved')}</p> : null}
        <ul className="flex flex-col gap-2">
          {approved.map((row) => (
            <li key={row.domain} className="rounded-xl border border-border bg-surface px-4 py-3 text-sm">
              <span className="font-medium">{row.domain}</span>
              <span className="text-muted"> · {t('requests', { count: row.requests })}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

function DomainRow({ row, when, onDone }: { row: InstitutionDomain; when: string; onDone: () => void }) {
  const t = useTranslations('adminDomains')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const decide = async (approve: boolean) => {
    setBusy(true)
    setError(null)
    try {
      const problem = await decideInstitutionDomain(row.domain, approve)
      if (problem) setError(problem)
      else onDone()
    } catch {
      setError(t('failed'))
    } finally {
      setBusy(false)
    }
  }
  return (
    <li className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p className="font-semibold">{row.domain}</p>
        <p className="text-xs text-muted">{when}</p>
      </div>
      <p className="text-sm text-muted">{t('requests', { count: row.requests })} · {t(`status.${row.status}`)}</p>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={busy} onClick={() => void decide(true)}>{t('approve')}</Button>
        <Button size="sm" variant="secondary" disabled={busy} onClick={() => void decide(false)}>{t('reject')}</Button>
      </div>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
    </li>
  )
}
