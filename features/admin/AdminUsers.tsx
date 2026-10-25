'use client'

import { useCallback, useEffect, useState } from 'react'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { canSeeSection } from '@/features/admin/AdminNav'
import { useViewerRole } from '@/features/admin/useViewerRole'
import {
  deleteAdminAccount,
  isUnknownFieldError,
  loadAdminAccount,
  loadAdminAccounts,
  PlatformError,
  setAccountBlocked,
  updateAdminAccount,
  type AccountStanding,
  type AdminAccount,
  type AdminAccountDetail,
  type AgeRecheck,
} from '@/lib/platform-api'

const FILTERS: AccountStanding[] = ['AGE_BLOCKED', 'BLOCKED', 'ACTIVE']

/** Platform admins: search accounts, correct details, block, unblock, or delete, each with a reason. */
export function AdminUsers() {
  const t = useTranslations('adminUsers')
  const { role, ready } = useViewerRole()
  const [status, setStatus] = useState<AccountStanding>('AGE_BLOCKED')
  const [search, setSearch] = useState('')
  const [rows, setRows] = useState<AdminAccount[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [openId, setOpenId] = useState<string | null>(null)
  const load = useCallback(async () => {
    try {
      setRows(await loadAdminAccounts({ status, search }))
      setError(null)
    } catch (e) {
      setRows([])
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
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
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
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {rows && !rows.length && !error ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {(rows ?? []).map((account) => (
          <li key={account.id}>
            <article className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-surface p-4">
              <div className="min-w-0">
                <p className="font-semibold">{account.displayName}</p>
                <p className="text-sm text-muted">{account.email} · {t(`status.${account.status}`)}</p>
              </div>
              <Button size="sm" variant="secondary" onClick={() => setOpenId(account.id)}>{t('open')}</Button>
            </article>
          </li>
        ))}
      </ul>
      <UserDrawer
        id={openId}
        onClose={() => setOpenId(null)}
        onChanged={() => void load()}
      />
    </div>
  )
}

function UserDrawer({ id, onClose, onChanged }: { id: string | null; onClose: () => void; onChanged: () => void }) {
  const t = useTranslations('adminUsers')
  const format = useFormatter()
  const [account, setAccount] = useState<AdminAccountDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [dob, setDob] = useState('')
  const [reason, setReason] = useState('')
  const [blockReason, setBlockReason] = useState('')
  const [deleteReason, setDeleteReason] = useState('')
  const [confirmEmail, setConfirmEmail] = useState('')
  const [recheck, setRecheck] = useState<AgeRecheck | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    if (!id) return
    let gone = false
    setAccount(null)
    setError(null)
    setRecheck(null)
    setNotice(null)
    setReason('')
    setBlockReason('')
    setDeleteReason('')
    setConfirmEmail('')
    void loadAdminAccount(id)
      .then((detail) => {
        if (gone) return
        setAccount(detail)
        setName(detail.displayName)
        setEmail(detail.email)
        setDob(detail.dateOfBirth ?? '')
      })
      .catch((e) => {
        if (!gone) setError(e instanceof PlatformError ? e.message : t('failed'))
      })
    return () => {
      gone = true
    }
  }, [id, t])
  const save = async () => {
    if (!account) return
    if (!reason.trim()) return setError(t('reasonNeeded'))
    setBusy(true)
    setError(null)
    try {
      const result = await updateAdminAccount({ userId: account.id, displayName: name.trim(), email: email.trim(), dateOfBirth: dob, reason: reason.trim() })
      if (result.problem) setError(result.problem)
      else {
        setRecheck(result.recheck)
        setNotice(t('saved'))
        if (result.account) setAccount({ ...account, ...result.account, audit: account.audit })
        onChanged()
      }
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const block = async (blocked: boolean) => {
    if (!account) return
    if (!blockReason.trim()) return setError(t('reasonNeeded'))
    setBusy(true)
    setError(null)
    try {
      const result = await setAccountBlocked({ userId: account.id, blocked, reason: blockReason.trim() })
      if (result.problem) setError(result.problem)
      else if (result.status) {
        setAccount({ ...account, status: result.status })
        onChanged()
      }
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const remove = async () => {
    if (!account) return
    if (confirmEmail.trim() !== account.email || !deleteReason.trim()) return setError(t('reasonNeeded'))
    setBusy(true)
    setError(null)
    try {
      const problem = await deleteAdminAccount({ userId: account.id, confirmEmail: confirmEmail.trim(), reason: deleteReason.trim() })
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
  const blocked = account?.status === 'BLOCKED' || account?.status === 'AGE_BLOCKED'
  return (
    <Dialog open={id !== null} onClose={onClose} title={account?.displayName ?? t('title')} side>
      {!account && !error ? <p className="text-sm text-muted">{t('loading')}</p> : null}
      {error ? <p role="alert" className="mb-3 text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {account ? (
        <div className="flex flex-col gap-6">
          <p className="text-sm text-muted">{t(`status.${account.status}`)} · {account.globalRole}</p>
          <form className="flex flex-col gap-3" onSubmit={(e) => { e.preventDefault(); void save() }}>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('name')}</span>
              <Input value={name} onChange={(e) => setName(e.target.value)} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('email')}</span>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('dob')}</span>
              <Input type="date" value={dob} onChange={(e) => setDob(e.target.value)} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('reason')}</span>
              <Input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonHint')} />
            </label>
            <Button type="submit" disabled={busy}>{busy ? t('saving') : t('save')}</Button>
            {recheck ? <p role="status" className="text-sm font-medium">{recheck === 'unblocked' ? t('unblocked') : t('stillUnderAge')}</p> : null}
            {notice && !recheck ? <p className="text-sm text-muted">{notice}</p> : null}
          </form>
          <form className="flex flex-col gap-3 border-t border-border pt-4" onSubmit={(e) => { e.preventDefault(); void block(!blocked) }}>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('reason')}</span>
              <Input value={blockReason} onChange={(e) => setBlockReason(e.target.value)} placeholder={t('reasonHint')} />
            </label>
            <Button type="submit" variant="secondary" disabled={busy}>{blocked ? t('unblock') : t('block')}</Button>
          </form>
          <form className="flex flex-col gap-3 rounded-xl border border-red-300 p-3 dark:border-red-900" onSubmit={(e) => { e.preventDefault(); void remove() }}>
            <h3 className="font-semibold text-red-700 dark:text-red-300">{t('delete')}</h3>
            <p className="text-sm text-muted">{t('deleteLead')}</p>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('deleteConfirm')}</span>
              <Input value={confirmEmail} onChange={(e) => setConfirmEmail(e.target.value)} autoComplete="off" />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium">{t('reason')}</span>
              <Input value={deleteReason} onChange={(e) => setDeleteReason(e.target.value)} placeholder={t('reasonHint')} />
            </label>
            <Button type="submit" className="bg-red-600 text-white hover:bg-red-700" disabled={busy || confirmEmail.trim() !== account.email || !deleteReason.trim()}>{t('deleteDo')}</Button>
          </form>
          <section aria-labelledby="account-audit" className="flex flex-col gap-2">
            <h3 id="account-audit" className="font-semibold">{t('audit')}</h3>
            {!account.audit.length ? <p className="text-sm text-muted">{t('noAudit')}</p> : null}
            <ol className="flex flex-col gap-2">
              {account.audit.map((entry) => (
                <li key={entry.id} className="rounded-xl bg-surface px-3 py-2 text-sm">
                  <p className="font-medium">{entry.action}</p>
                  <p>{entry.reason}</p>
                  <p className="text-muted">{entry.actorName ? `${entry.actorName} · ` : ''}{entry.at ? format.dateTime(new Date(entry.at), { dateStyle: 'medium', timeStyle: 'short' }) : ''}</p>
                </li>
              ))}
            </ol>
          </section>
        </div>
      ) : null}
    </Dialog>
  )
}
