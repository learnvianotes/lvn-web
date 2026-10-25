'use client'

import { useCallback, useEffect, useState } from 'react'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { loadErrorGroups, lookupUsers, PlatformError, type ErrorGroup, type LookupUser } from '@/lib/platform-api'

/** Errors grouped by type, with a trend and the people who hit each one. */
export function AdminErrors() {
  const t = useTranslations('adminErrors')
  const { role, ready } = useViewerRole()
  const [groups, setGroups] = useState<ErrorGroup[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [open, setOpen] = useState<string | null>(null)
  const load = useCallback(async () => {
    try {
      setGroups(await loadErrorGroups())
      setError(null)
    } catch (e) {
      setGroups([])
      setError(e instanceof PlatformError && e.forbidden ? t('notAllowed') : t('failed'))
    }
  }, [t])
  useEffect(() => {
    if (ready && canSeeSection(role, 'errors')) void load()
  }, [ready, role, load])
  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!canSeeSection(role, 'errors')) return <p className="text-muted">{t('notAllowed')}</p>
  const selected = groups?.find((group) => group.fingerprint === open) ?? null
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {groups && !groups.length && !error ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {(groups ?? []).map((group) => (
          <li key={group.fingerprint}>
            <GroupRow group={group} open={open === group.fingerprint} onOpen={() => setOpen(group.fingerprint)} />
          </li>
        ))}
      </ul>
      {selected ? <AffectedUsers group={selected} onClose={() => setOpen(null)} /> : null}
    </div>
  )
}

function GroupRow({ group, open, onOpen }: { group: ErrorGroup; open: boolean; onOpen: () => void }) {
  const t = useTranslations('adminErrors')
  const format = useFormatter()
  const when = (value: string) => format.dateTime(new Date(value), { dateStyle: 'medium', timeStyle: 'short' })
  return (
    <article className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted">{group.type}</p>
          <h2 className="text-base font-semibold break-words">{group.message}</h2>
        </div>
        <p className="text-2xl font-extrabold tracking-tight">{format.number(group.count)}</p>
      </div>
      <p className="text-sm text-muted">{t('seen', { first: when(group.firstSeen), last: when(group.lastSeen) })}</p>
      <Trend values={group.trend} label={t('trend')} />
      <Button size="sm" variant="secondary" className="w-fit" aria-expanded={open} onClick={onOpen}>
        {t('people', { count: group.affectedUserIds.length })}
      </Button>
    </article>
  )
}

function Trend({ values, label }: { values: number[]; label: string }) {
  const max = Math.max(1, ...values)
  if (!values.length) return null
  return (
    <div className="flex items-end gap-1" role="img" aria-label={label}>
      {values.map((value, index) => (
        <span key={index} className="w-2 rounded-sm bg-accent" style={{ height: `${Math.max(4, Math.round((value / max) * 32))}px` }} />
      ))}
    </div>
  )
}

function AffectedUsers({ group, onClose }: { group: ErrorGroup; onClose: () => void }) {
  const t = useTranslations('adminErrors')
  const format = useFormatter()
  const [users, setUsers] = useState<LookupUser[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    let gone = false
    void lookupUsers(group.affectedUserIds)
      .then((rows) => {
        if (!gone) setUsers(rows)
      })
      .catch(() => {
        if (!gone) setError(t('failed'))
      })
    return () => {
      gone = true
    }
  }, [group, t])
  const last = new Map(group.affectedUsers.map((row) => [row.userId, row.lastSeen]))
  return (
    <section aria-labelledby="affected-users" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex items-center justify-between gap-3">
        <h2 id="affected-users" className="text-lg font-semibold">{t('affected')}</h2>
        <Button size="sm" variant="secondary" onClick={onClose}>{t('close')}</Button>
      </div>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {!users && !error ? <p className="text-sm text-muted">{t('loading')}</p> : null}
      <ul className="flex flex-col gap-2">
        {(users ?? []).map((user) => {
          const at = last.get(user.id) ?? group.lastSeen
          return (
            <li key={user.id} className="flex flex-wrap items-baseline justify-between gap-2 rounded-xl bg-bg px-3 py-2 text-sm">
              <span>
                <span className="font-medium">{user.displayName}</span>
                <span className="text-muted"> · {user.email ?? '—'} · {user.globalRole}</span>
              </span>
              <span className="text-muted">{format.dateTime(new Date(at), { dateStyle: 'medium', timeStyle: 'short' })}</span>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
