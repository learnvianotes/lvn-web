'use client'

import { useCallback, useEffect, useId, useState } from 'react'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { AGE_INPUT, AGE_MAX, AGE_MIN, birthDateLimits } from '@/lib/age'
import {
  ageEditOf,
  deleteAdminUser,
  isUnknownFieldError,
  loadAdminUsers,
  PlatformError,
  setAccountStanding,
  updateAdminUser,
  type AdminManagedUser,
  type AdminUserStatusFilter,
  type AgeOutcome,
} from '@/lib/platform-api'

const FILTERS: AdminUserStatusFilter[] = ['AGE_BLOCKED', 'BLOCKED_OR_SUSPENDED', 'ACTIVE']
const DELETE_WORD = 'DELETE'

/**
 * Platform admins: search accounts, correct an age (or the date of birth of an account that has one, lvn-backend
 * ADR-0104), block, suspend, unblock, or delete.
 */
export function AdminUsers() {
  const t = useTranslations('adminUsers')
  const { role, ready } = useViewerRole()
  const [status, setStatus] = useState<AdminUserStatusFilter>('AGE_BLOCKED')
  const [search, setSearch] = useState('')
  const [rows, setRows] = useState<AdminManagedUser[] | null>(null)
  const [total, setTotal] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [openUser, setOpenUser] = useState<AdminManagedUser | null>(null)
  const load = useCallback(async () => {
    try {
      const list = await loadAdminUsers({ status, search })
      setRows(list.users)
      setTotal(list.total)
      setError(null)
    } catch (e) {
      setRows([])
      setTotal(null)
      setError(isUnknownFieldError(e) ? t('unavailable') : e instanceof PlatformError && e.forbidden ? t('notAllowed') : t('failed'))
    }
  }, [status, search, t])
  useEffect(() => {
    if (ready && canSeeSection(role, 'users')) void load()
  }, [ready, role, load])
  if (!ready) return <p className="text-muted">{t('loading')}</p>
  if (!canSeeSection(role, 'users')) return <p className="text-muted">{t('notAllowed')}</p>
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
        <label className="flex min-w-0 flex-1 flex-col gap-1">
          <span className="text-sm font-medium">{t('search')}</span>
          <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={t('searchHint')} />
        </label>
        <div role="group" aria-label={t('filters')} className="flex flex-wrap gap-2">
          {FILTERS.map((filter) => (
            <Button key={filter} type="button" size="sm" variant={status === filter ? 'primary' : 'secondary'} aria-pressed={status === filter} onClick={() => setStatus(filter)}>
              {t(`status.${filter}`)}
            </Button>
          ))}
        </div>
      </div>
      {total !== null ? <p className="text-sm text-muted">{t('count', { count: total })}</p> : null}
      {error ? <p role="alert" className="text-sm text-bad">{error}</p> : null}
      {rows && !rows.length && !error ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {(rows ?? []).map((user) => (
          <li key={user.id}>
            <article className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-surface p-4">
              <div className="min-w-0">
                <p className="font-semibold">{user.displayName}</p>
                <p className="text-sm text-muted">
                  {user.email} · {t(`status.${user.accountStatus}`)}
                  {user.age !== null ? ` · ${t('ageInList', { age: user.age })}` : null}
                </p>
              </div>
              <Button size="sm" variant="secondary" onClick={() => setOpenUser(user)}>{t('open')}</Button>
            </article>
          </li>
        ))}
      </ul>
      <UserDialog
        user={openUser}
        onClose={() => setOpenUser(null)}
        onUser={setOpenUser}
        onChanged={() => void load()}
      />
    </div>
  )
}

function UserDialog({ user, onClose, onUser, onChanged }: { user: AdminManagedUser | null; onClose: () => void; onUser: (user: AdminManagedUser) => void; onChanged: () => void }) {
  const t = useTranslations('adminUsers')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [dob, setDob] = useState('')
  const [age, setAge] = useState('')
  const [reason, setReason] = useState('')
  const [blockReason, setBlockReason] = useState('')
  const [until, setUntil] = useState('')
  const [deleteReason, setDeleteReason] = useState('')
  const [confirmText, setConfirmText] = useState('')
  // After a save: the age check unblocked the account, or left it under age; otherwise 'saved'.
  const [outcome, setOutcome] = useState<AgeOutcome | 'saved' | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const ageHintId = useId()
  useEffect(() => {
    setName(user?.displayName ?? '')
    setEmail(user?.email ?? '')
    setDob(user?.dateOfBirth ?? '')
    setAge(user?.age != null ? String(user.age) : '')
    setReason('')
    setBlockReason('')
    setUntil('')
    setDeleteReason('')
    setConfirmText('')
    setOutcome(null)
    setError(null)
    // Fill the form when a different account is opened. A later save updates these fields itself, so a list refresh must not wipe them.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id])
  const save = async () => {
    if (!user) return
    if (!reason.trim()) return setError(t('reasonNeeded'))
    // Only a changed age, or a changed date of birth on an account that has one (lvn-backend ADR-0104).
    const ageEdit = ageEditOf(user, { age, dateOfBirth: dob })
    if (ageEdit === 'invalid') return setError(t('ageInvalid', { min: AGE_MIN, max: AGE_MAX }))
    // The API runs the age check on a new age or date, and on any save of an age-blocked account.
    const wasBlocked = user.accountStatus === 'AGE_BLOCKED'
    const ageChecked = 'age' in ageEdit || 'dateOfBirth' in ageEdit || wasBlocked
    setBusy(true)
    setError(null)
    setOutcome(null)
    try {
      const result = await updateAdminUser({ userId: user.id, reason: reason.trim(), displayName: name.trim(), email: email.trim(), ...ageEdit })
      if (result.problem) setError(result.problem)
      else {
        if (result.user) {
          setName(result.user.displayName)
          setEmail(result.user.email)
          setDob(result.user.dateOfBirth ?? '')
          setAge(result.user.age != null ? String(result.user.age) : '')
          onUser(result.user)
        }
        setOutcome(ageChecked && result.outcome === 'still_under_age' ? 'still_under_age' : wasBlocked && result.outcome === 'unblocked' ? 'unblocked' : 'saved')
        onChanged()
      }
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const standing = async (status: 'ACTIVE' | 'BLOCKED' | 'SUSPENDED') => {
    if (!user) return
    if (!blockReason.trim()) return setError(t('reasonNeeded'))
    if (status === 'SUSPENDED' && !until) return setError(t('untilNeeded'))
    setBusy(true)
    setError(null)
    try {
      const result = await setAccountStanding({
        userId: user.id,
        status,
        reason: blockReason.trim(),
        until: status === 'SUSPENDED' ? new Date(until).toISOString() : null,
      })
      if (result.problem) setError(result.problem)
      else {
        if (result.user) onUser(result.user)
        onChanged()
      }
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const remove = async () => {
    if (!user) return
    if (confirmText !== DELETE_WORD || !deleteReason.trim()) return setError(t('reasonNeeded'))
    setBusy(true)
    setError(null)
    try {
      const problem = await deleteAdminUser({ userId: user.id, confirm: confirmText, reason: deleteReason.trim() })
      if (problem) setError(problem)
      else {
        onChanged()
        onClose()
      }
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const held = user?.accountStatus === 'BLOCKED' || user?.accountStatus === 'SUSPENDED'
  return (
    <Dialog open={user !== null} onClose={onClose} title={user?.displayName ?? t('title')} side>
      {error ? <p role="alert" className="mb-3 text-sm text-bad">{error}</p> : null}
      {user ? (
        <div className="flex flex-col gap-6">
          <p className="text-sm text-muted">{t(`status.${user.accountStatus}`)} · {user.globalRole}</p>
          {user.statusReason ? (
            <p className="text-sm">
              <span className="font-medium">{t('statusReason')}. </span>
              {user.statusReason}
            </p>
          ) : null}
          <form className="flex flex-col gap-3" onSubmit={(e) => { e.preventDefault(); void save() }}>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('name')}</span>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('email')}</span>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            {/* A stored date of birth decides the age, so it is what gets corrected; other accounts give an age. */}
            {user.dateOfBirth !== null ? (
              <div className="flex flex-col gap-1 text-sm">
                <label className="flex flex-col gap-1">
                  <span className="font-medium">{t('dob')}</span>
                  <Input type="date" min={birthDateLimits().min} max={birthDateLimits().max} value={dob} onChange={(e) => setDob(e.target.value)} aria-describedby={user.age !== null ? ageHintId : undefined} />
                </label>
                {user.age !== null ? <p id={ageHintId} className="text-xs text-muted">{t('dobHint', { age: user.age })}</p> : null}
              </div>
            ) : (
              <div className="flex flex-col gap-1 text-sm">
                <label className="flex flex-col gap-1">
                  <span className="font-medium">{t('age')}</span>
                  <Input {...AGE_INPUT} className="max-w-32" value={age} onChange={(e) => setAge(e.target.value)} aria-describedby={ageHintId} />
                </label>
                <p id={ageHintId} className="text-xs text-muted">{t('ageHint')}</p>
              </div>
            )}
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('reason')}</span>
              <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonHint')} />
            </label>
            <Button type="submit" disabled={busy}>{busy ? t('saving') : t('save')}</Button>
            {outcome ? <p role="status" className="text-sm font-medium">{outcome === 'unblocked' ? t('unblocked') : outcome === 'still_under_age' ? t('stillUnderAge') : t('saved')}</p> : null}
          </form>
          <form className="flex flex-col gap-3 border-t border-border pt-4" onSubmit={(e) => e.preventDefault()}>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('reason')}</span>
              <Input value={blockReason} onChange={(e) => setBlockReason(e.target.value)} placeholder={t('reasonHint')} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('until')}</span>
              <Input type="datetime-local" value={until} onChange={(e) => setUntil(e.target.value)} />
            </label>
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="secondary" disabled={busy} onClick={() => void standing('BLOCKED')}>{t('block')}</Button>
              <Button type="button" variant="secondary" disabled={busy} onClick={() => void standing('SUSPENDED')}>{t('suspend')}</Button>
              {held ? <Button type="button" variant="secondary" disabled={busy} onClick={() => void standing('ACTIVE')}>{t('unblock')}</Button> : null}
            </div>
          </form>
          <form className="flex flex-col gap-3 rounded-xl border border-bad/30 p-3" onSubmit={(e) => { e.preventDefault(); void remove() }}>
            <h3 className="font-semibold text-bad">{t('delete')}</h3>
            <p className="text-sm text-muted">{t('deleteLead')}</p>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('deleteConfirm')}</span>
              <Input value={confirmText} onChange={(e) => setConfirmText(e.target.value)} autoComplete="off" />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('reason')}</span>
              <Input value={deleteReason} onChange={(e) => setDeleteReason(e.target.value)} placeholder={t('reasonHint')} />
            </label>
            <Button type="submit" className="bg-red-600 text-white hover:bg-red-700" disabled={busy || confirmText !== DELETE_WORD || !deleteReason.trim()}>{t('deleteDo')}</Button>
          </form>
        </div>
      ) : null}
    </Dialog>
  )
}
