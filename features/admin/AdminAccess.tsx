'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import Link from 'next/link'
import { useEffect, useState, type FormEvent } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { formatAddedOn, parseAllowlistEmails } from '@/features/admin/access-model'
import {
  AddAccessAllowlistEntryDocument,
  AdminAccessAllowlistDocument,
  AdminSettingsDocument,
  RemoveAccessAllowlistEntryDocument,
  UpdateAccessAllowlistEntryDocument,
  UpdateAdminSettingDocument,
  type AccessAllowlistFieldsFragment,
  type GlobalRole,
} from '@/graphql/generated/graphql'
import { refusalMessage } from '@/lib/limit-error'
import { cn } from '@/lib/cn'

const ALLOWLIST_KEY = 'access_allowlist_enabled'
const ROLES = ['STUDENT', 'TEACHER', 'PLATFORM_ADMIN'] as const satisfies readonly GlobalRole[]
const SELECT = 'h-11 w-full min-w-0 rounded-xl border border-border bg-surface px-3 text-[15px] text-fg'

type Entry = AccessAllowlistFieldsFragment

export function AdminAccess() {
  const t = useTranslations('adminAccess')
  const [search, setSearch] = useState('')
  const trimmed = search.trim()
  const list = useQuery(AdminAccessAllowlistDocument, {
    variables: { search: trimmed || null },
    fetchPolicy: 'cache-and-network',
  })
  const settings = useQuery(AdminSettingsDocument, { fetchPolicy: 'cache-and-network' })
  const forbidden =
    (CombinedGraphQLErrors.is(list.error) && list.error.errors.some((error) => error.extensions?.code === 'FORBIDDEN')) ||
    (CombinedGraphQLErrors.is(settings.error) && settings.error.errors.some((error) => error.extensions?.code === 'FORBIDDEN'))
  if (forbidden) return <p className="text-muted">{t('notAllowed')}</p>
  const entries = list.data?.adminAccessAllowlist
  const setting = settings.data?.adminSettings.find((item) => item.key === ALLOWLIST_KEY) ?? null

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      <AllowlistSwitch setting={setting} failed={!!settings.error && !settings.data} onSaved={() => void settings.refetch()} />
      <AddForm onAdded={() => void list.refetch()} />
      <form
        className="flex flex-col gap-2 sm:max-w-md"
        onSubmit={(event) => {
          event.preventDefault()
        }}
      >
        <label htmlFor="allowlist-search" className="text-sm font-medium">
          {t('search')}
        </label>
        <Input id="allowlist-search" type="search" value={search} placeholder={t('searchPlaceholder')} onChange={(event) => setSearch(event.target.value)} />
      </form>
      {entries ? (
        entries.length ? (
          <ul className="flex flex-col gap-3">
            {entries.map((entry) => (
              <li key={entry.id}>
                <EntryRow entry={entry} onChanged={() => void list.refetch()} />
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{trimmed ? t('noneSearch') : t('none')}</p>
        )
      ) : list.error ? (
        <Alert tone="error">{t('failed')}</Alert>
      ) : (
        <p className="text-muted">{t('loading')}</p>
      )}
    </div>
  )
}

function AllowlistSwitch({
  setting,
  failed,
  onSaved,
}: {
  setting: { value: string; description: string } | null
  failed: boolean
  onSaved: () => void
}) {
  const t = useTranslations('adminAccess')
  const [update, updating] = useMutation(UpdateAdminSettingDocument)
  const [pending, setPending] = useState<boolean | null>(null)
  const [issue, setIssue] = useState<string | null>(null)
  const enabled = setting?.value === 'true'
  const save = async (next: boolean) => {
    setIssue(null)
    try {
      const res = await update({ variables: { input: { key: ALLOWLIST_KEY, value: next ? 'true' : 'false' } } })
      const userError = res.data?.updateAdminSetting.userErrors[0]
      if (userError) {
        setIssue(userError.message)
        return
      }
      setPending(null)
      onSaved()
    } catch (error) {
      setIssue(refusalMessage(error) ?? (CombinedGraphQLErrors.is(error) ? (error.errors[0]?.message ?? t('failed')) : t('failed')))
    }
  }
  return (
    <section aria-label={t('settingTitle')} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="min-w-0">
          <h2 className="font-semibold">{t('settingTitle')}</h2>
          <p className="text-sm text-muted">{setting ? (enabled ? t('settingOn') : t('settingOff')) : failed ? t('settingFailed') : t('settingMissing')}</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          {setting ? (
            <button
              type="button"
              role="switch"
              aria-checked={enabled}
              aria-label={t('settingTitle')}
              disabled={updating.loading}
              onClick={() => setPending(!enabled)}
              className="relative h-11 w-14 shrink-0 self-start"
            >
              <span aria-hidden className={cn('absolute left-1 top-2 h-7 w-12 rounded-full transition-colors', enabled ? 'bg-accent' : 'bg-border')}>
                <span className={cn('absolute top-0.5 size-6 rounded-full bg-white shadow', enabled ? 'left-5' : 'left-0.5')} />
              </span>
            </button>
          ) : null}
          <Link href="/admin/settings#auth" className="inline-flex min-h-11 items-center text-sm font-medium text-accent hover:underline">
            {t('settingLink')}
          </Link>
        </div>
      </div>
      {issue ? <Alert tone="error">{issue}</Alert> : null}
      <Dialog open={pending !== null} onClose={() => setPending(null)} title={t('settingConfirmTitle')} sheet>
        <div className="flex flex-col gap-4">
          <p className="text-sm">{pending ? t('settingOnConfirm') : t('settingOffConfirm')}</p>
          {issue ? <Alert tone="error">{issue}</Alert> : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" onClick={() => setPending(null)}>
              {t('cancel')}
            </Button>
            <Button type="button" className="h-11 w-full sm:w-auto" disabled={updating.loading || pending === null} onClick={() => pending !== null && void save(pending)}>
              {updating.loading ? t('saving') : t('settingConfirm')}
            </Button>
          </div>
        </div>
      </Dialog>
    </section>
  )
}

function AddForm({ onAdded }: { onAdded: () => void }) {
  const t = useTranslations('adminAccess')
  const [add, adding] = useMutation(AddAccessAllowlistEntryDocument)
  const [emails, setEmails] = useState('')
  const [role, setRole] = useState<GlobalRole>('STUDENT')
  const [note, setNote] = useState('')
  const [issue, setIssue] = useState<string | null>(null)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    const parsed = parseAllowlistEmails(emails)
    if (!parsed.ok.length) {
      setIssue(parsed.invalid.length ? t('invalidEmails', { emails: parsed.invalid.join(', ') }) : t('emailRequired'))
      return
    }
    if (parsed.invalid.length) {
      setIssue(t('invalidEmails', { emails: parsed.invalid.join(', ') }))
      return
    }
    setIssue(null)
    const problems: string[] = []
    for (const email of parsed.ok) {
      try {
        const res = await add({ variables: { input: { email, role, note: note.trim() || null } } })
        const userErrors = res.data?.addAccessAllowlistEntry.userErrors ?? []
        if (userErrors.length) problems.push(`${email}: ${userErrors.map((error) => error.message).join(' ')}`)
      } catch (error) {
        problems.push(`${email}: ${refusalMessage(error) ?? t('failed')}`)
      }
    }
    if (problems.length) setIssue(problems.join('\n'))
    else {
      setEmails('')
      setNote('')
    }
    onAdded()
  }

  return (
    <form onSubmit={(event) => void submit(event)} className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-4">
      <h2 className="font-semibold">{t('addTitle')}</h2>
      {issue ? (
        <Alert tone="error">
          <span className="whitespace-pre-wrap">{issue}</span>
        </Alert>
      ) : null}
      <Field label={t('emails')} hint={t('emailsHint')}>
        <textarea
          value={emails}
          rows={3}
          required
          onChange={(event) => setEmails(event.target.value)}
          className="min-h-24 w-full rounded-xl border border-border bg-bg px-3 py-2 text-[15px] text-fg"
        />
      </Field>
      <div className="grid gap-4 sm:grid-cols-2">
        <Field label={t('role')}>
          <select className={SELECT} value={role} onChange={(event) => setRole(event.target.value as GlobalRole)}>
            {ROLES.map((item) => (
              <option key={item} value={item}>
                {t(`roles.${item}`)}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t('note')} hint={t('noteHint')}>
          <Input value={note} onChange={(event) => setNote(event.target.value)} />
        </Field>
      </div>
      <Button type="submit" className="h-11 w-full sm:w-auto sm:self-start" disabled={adding.loading}>
        {adding.loading ? t('adding') : t('add')}
      </Button>
    </form>
  )
}

function EntryRow({ entry, onChanged }: { entry: Entry; onChanged: () => void }) {
  const t = useTranslations('adminAccess')
  const [update, updating] = useMutation(UpdateAccessAllowlistEntryDocument)
  const [remove, removing] = useMutation(RemoveAccessAllowlistEntryDocument)
  const [confirming, setConfirming] = useState(false)
  const [issue, setIssue] = useState<string | null>(null)
  const [role, setRole] = useState(entry.role)
  useEffect(() => setRole(entry.role), [entry.role])
  const busy = updating.loading || removing.loading

  const changeRole = async (next: GlobalRole) => {
    if (next === entry.role) return
    setRole(next)
    setIssue(null)
    try {
      const res = await update({ variables: { input: { id: entry.id, role: next } } })
      const userError = res.data?.updateAccessAllowlistEntry.userErrors[0]
      if (userError) {
        setRole(entry.role)
        setIssue(userError.message)
        return
      }
      onChanged()
    } catch (error) {
      setRole(entry.role)
      setIssue(refusalMessage(error) ?? t('failed'))
    }
  }

  const drop = async () => {
    setIssue(null)
    try {
      const res = await remove({ variables: { id: entry.id } })
      const userError = res.data?.removeAccessAllowlistEntry.userErrors[0]
      if (userError) {
        setIssue(userError.message)
        return
      }
      setConfirming(false)
      onChanged()
    } catch (error) {
      setIssue(refusalMessage(error) ?? t('failed'))
    }
  }

  return (
    <article aria-label={entry.email} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <h3 className="break-all font-semibold">{entry.email}</h3>
          {entry.note ? <p className="text-sm text-muted">{entry.note}</p> : null}
          <p className="mt-2 flex flex-wrap gap-2 text-xs">
            <span className={entry.hasAccount ? 'rounded-[4px] bg-accent-soft px-2 py-0.5 font-medium text-accent' : 'rounded-full bg-surface-2 px-2 py-0.5 text-muted'}>
              {entry.hasAccount ? t('hasAccount') : t('noAccount')}
            </span>
            <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{t('added', { date: formatAddedOn(entry.createdAt) })}</span>
            {entry.addedByEmail ? <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{t('addedBy', { email: entry.addedByEmail })}</span> : null}
          </p>
        </div>
        <div className="flex w-full flex-col gap-2 sm:flex-row lg:w-auto lg:min-w-72">
          <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
            <span className="sr-only">{t('roleFor', { email: entry.email })}</span>
            <select
              aria-label={t('roleFor', { email: entry.email })}
              className={SELECT}
              value={role}
              disabled={busy}
              onChange={(event) => void changeRole(event.target.value as GlobalRole)}
            >
              {ROLES.map((item) => (
                <option key={item} value={item}>
                  {t(`roles.${item}`)}
                </option>
              ))}
            </select>
          </label>
          <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" aria-label={t('removeNamed', { email: entry.email })} disabled={busy} onClick={() => { setIssue(null); setConfirming(true) }}>
            {t('remove')}
          </Button>
        </div>
      </div>
      {issue && !confirming ? <Alert tone="error">{issue}</Alert> : null}
      <Dialog open={confirming} onClose={() => setConfirming(false)} title={t('removeTitle', { email: entry.email })} sheet>
        <div className="flex flex-col gap-4">
          <p className="break-all text-sm">{t('removeConfirm', { email: entry.email })}</p>
          {issue ? <Alert tone="error">{issue}</Alert> : null}
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" onClick={() => setConfirming(false)}>
              {t('cancel')}
            </Button>
            <Button type="button" className="h-11 w-full sm:w-auto" disabled={removing.loading} onClick={() => void drop()}>
              {removing.loading ? t('removing') : t('remove')}
            </Button>
          </div>
        </div>
      </Dialog>
    </article>
  )
}
