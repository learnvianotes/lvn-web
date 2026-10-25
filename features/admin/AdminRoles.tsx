'use client'

import { useQuery } from '@apollo/client/react'
import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { SearchDocument } from '@/graphql/generated/graphql'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { PlatformError, setStaffRole, type AssignableRole } from '@/lib/platform-api'

/**
 * Platform admins assign or remove the manager and teacher roles. Removing a role sets the person back to student.
 * Teacher applications are still approved from the verification queue, not from here.
 */
export function AdminRoles() {
  const t = useTranslations('adminRoles')
  const { role, ready } = useViewerRole()
  const [query, setQuery] = useState('')
  const term = query.trim()
  const search = useQuery(SearchDocument, { variables: { query: term, scopes: ['PEOPLE'], first: 8 }, skip: !ready || role !== 'PLATFORM_ADMIN' || term.length < 2, fetchPolicy: 'no-cache' })
  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!canSeeSection(role, 'roles')) return <p className="text-muted">{t('notAllowed')}</p>
  const people = search.data?.search.people ?? []
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      <label className="flex max-w-md flex-col gap-1">
        <span className="text-sm font-medium">{t('find')}</span>
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('findHint')} />
      </label>
      {term.length >= 2 && search.data && !people.length ? <p className="text-sm text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {people.map((person) => (
          <li key={person.id}>
            <PersonRow id={person.id} name={person.displayName} handle={person.handle} role={person.globalRole} />
          </li>
        ))}
      </ul>
    </div>
  )
}

function PersonRow({ id, name, handle, role }: { id: string; name: string; handle: string; role: string }) {
  const t = useTranslations('adminRoles')
  const [current, setCurrent] = useState(role)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const assign = async (next: AssignableRole) => {
    setBusy(true)
    setError(null)
    try {
      const problem = await setStaffRole(id, next)
      if (problem) setError(problem)
      else setCurrent(next)
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const staff = current === 'MANAGER' || current === 'TEACHER'
  return (
    <article aria-label={name} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="font-semibold">{name}</p>
        <p className="text-sm text-muted">@{handle} · {t(`roles.${current}` as 'roles.STUDENT')}</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant={current === 'MANAGER' ? 'secondary' : 'primary'} disabled={busy || current === 'MANAGER' || current === 'PLATFORM_ADMIN'} onClick={() => void assign('MANAGER')}>{t('makeManager')}</Button>
        <Button size="sm" variant="secondary" disabled={busy || current === 'TEACHER' || current === 'PLATFORM_ADMIN'} onClick={() => void assign('TEACHER')}>{t('makeTeacher')}</Button>
        {staff ? <Button size="sm" variant="secondary" disabled={busy} onClick={() => void assign('STUDENT')}>{t('remove')}</Button> : null}
      </div>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400 sm:basis-full">{error}</p> : null}
    </article>
  )
}
