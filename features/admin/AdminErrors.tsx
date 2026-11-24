'use client'

import { useCallback, useEffect, useState } from 'react'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { loadErrorGroups, lookupUsers, PlatformError, type ErrorGroup, type LookupUser } from '@/lib/platform-api'

/** Errors grouped by code, and the people who hit each one. */
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
  const selected = groups?.find((group) => group.code === open) ?? null
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {groups && !groups.length && !error ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {(groups ?? []).map((group) => (
          <li key={group.code}>
            <GroupRow group={group} open={open === group.code} onOpen={() => setOpen(group.code)} />
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
          <p className="text-xs font-semibold text-muted">{group.code}</p>
          <h2 className="text-base font-semibold break-words">{group.sampleMessage}</h2>
        </div>
        <p className="text-2xl font-semibold tracking-tight">{format.number(group.count)}</p>
      </div>
      <p className="text-sm text-muted">{t('seen', { first: when(group.firstSeen), last: when(group.lastSeen) })}</p>
      <Button size="sm" variant="secondary" className="w-fit" aria-expanded={open} onClick={onOpen}>
        {t('people', { count: group.userIds.length })}
      </Button>
    </article>
  )
}

function AffectedUsers({ group, onClose }: { group: ErrorGroup; onClose: () => void }) {
  const t = useTranslations('adminErrors')
  const format = useFormatter()
  const [users, setUsers] = useState<LookupUser[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    let gone = false
    void lookupUsers(group.userIds)
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
  return (
    <section aria-labelledby="affected-users" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex items-center justify-between gap-3">
        <h2 id="affected-users" className="text-lg font-semibold">{t('affected')}</h2>
        <Button size="sm" variant="secondary" onClick={onClose}>{t('close')}</Button>
      </div>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {!users && !error ? <p className="text-sm text-muted">{t('loading')}</p> : null}
      <ul className="flex flex-col gap-2">
        {(users ?? []).map((user) => (
          <li key={user.id} className="flex flex-wrap items-baseline justify-between gap-2 rounded-xl bg-bg px-3 py-2 text-sm">
            <span>
              <span className="font-medium">{user.displayName}</span>
              <span className="text-muted"> · {user.email} · {user.globalRole}</span>
            </span>
            <span className="text-muted">{format.dateTime(new Date(group.lastSeen), { dateStyle: 'medium', timeStyle: 'short' })}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
