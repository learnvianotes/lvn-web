'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState, type ReactNode } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { AdminSettingsDocument, ResetAdminSettingDocument, UpdateAdminSettingDocument, type AdminSettingsQuery } from '@/graphql/generated/graphql'
import { microUsdToUsd } from '@/features/admin/metrics'
import { effectiveIntegerMin, groupSettings, isRiskyChange, validateSetting, type SettingIssue, type SettingShape } from '@/features/admin/settings-model'
import { cn } from '@/lib/cn'

type Setting = AdminSettingsQuery['adminSettings'][number]

export function AdminSettings() {
  const t = useTranslations('adminSettings')
  const { data, error, previousData, refetch } = useQuery(AdminSettingsDocument, { fetchPolicy: 'cache-and-network' })
  if (CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')) return <p className="text-muted">{t('notAllowed')}</p>
  // Keep the last list while a save refetches, so a draft in another row is not thrown away.
  const settings = data?.adminSettings ?? previousData?.adminSettings
  if (!settings) return error ? <Alert tone="error">{t('failed')}</Alert> : <p className="text-muted">{t('loading')}</p>

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>
      {groupSettings(settings).map((group) => (
        <section key={group.category} id={group.category} aria-labelledby={`settings-${group.category}`} className="flex scroll-mt-24 flex-col gap-3">
          <h2 id={`settings-${group.category}`} className="text-lg font-semibold">
            {t.has(`categories.${group.category}`) ? t(`categories.${group.category}`) : group.category}
          </h2>
          <ul className="flex flex-col gap-3">
            {group.settings.map((setting) => (
              <li key={setting.key}>
                <SettingRow setting={setting} onSaved={() => void refetch()} />
              </li>
            ))}
          </ul>
        </section>
      ))}
    </div>
  )
}

function SettingRow({ setting, onSaved }: { setting: Setting; onSaved: () => void }) {
  const t = useTranslations('adminSettings')
  const [draft, setDraft] = useState<string | null>(null)
  const [issue, setIssue] = useState<string | null>(null)
  const [confirming, setConfirming] = useState(false)
  const [update, updating] = useMutation(UpdateAdminSettingDocument)
  const [reset, resetting] = useMutation(ResetAdminSettingDocument)
  const value = draft ?? setting.value
  const dirty = value !== setting.value
  const clientIssue = validateSetting(setting, value)
  const shownIssue = issue ?? (clientIssue ? issueText(t, setting, clientIssue) : null)
  const label = t.has(`keys.${setting.key}`) ? t(`keys.${setting.key}`) : setting.key
  const hint = describe(setting, value, t)
  const busy = updating.loading || resetting.loading

  const send = async (next: string) => {
    setIssue(null)
    const problem = validateSetting(setting, next)
    if (problem) {
      setIssue(issueText(t, setting, problem))
      return
    }
    try {
      const res = await update({ variables: { input: { key: setting.key, value: next } } })
      const userError = res.data?.updateAdminSetting.userErrors[0]
      if (userError) {
        setIssue(userError.message)
        return
      }
      setDraft(null)
      setConfirming(false)
      onSaved()
    } catch (err) {
      setIssue(CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  const save = () => {
    if (clientIssue) {
      setIssue(issueText(t, setting, clientIssue))
      return
    }
    if (isRiskyChange(setting, setting.value, value)) {
      setConfirming(true)
      return
    }
    void send(value)
  }

  const restore = async () => {
    setIssue(null)
    try {
      const res = await reset({ variables: { key: setting.key } })
      const userError = res.data?.resetAdminSetting.userErrors[0]
      if (userError) {
        setIssue(userError.message)
        return
      }
      setDraft(null)
      onSaved()
    } catch (err) {
      setIssue(CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  return (
    <article aria-label={label} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-semibold">{label}</h3>
          <p className="text-xs text-muted">{setting.key}</p>
        </div>
        <p className="flex flex-wrap gap-2">
          <Badge muted={!setting.overridden}>{setting.overridden ? t('custom') : t('default')}</Badge>
          {dirty ? <Badge>{t('unsaved')}</Badge> : null}
        </p>
      </div>
      {setting.type === 'BOOLEAN' ? (
        <Switch id={`setting-${setting.key}`} label={label} hint={hint} checked={value === 'true'} invalid={!!shownIssue} onChange={(on) => { setDraft(on ? 'true' : 'false'); setIssue(null) }} />
      ) : (
        <div className="flex flex-col gap-1.5">
          <label htmlFor={`setting-${setting.key}`} className="sr-only">
            {label}
          </label>
          <Input
            id={`setting-${setting.key}`}
            type={setting.type === 'INTEGER' ? 'number' : 'text'}
            inputMode={setting.type === 'INTEGER' ? 'numeric' : undefined}
            step={setting.type === 'INTEGER' ? 1 : undefined}
            min={setting.type === 'INTEGER' ? (effectiveIntegerMin(setting) ?? undefined) : undefined}
            max={setting.type === 'INTEGER' ? (setting.constraints.max ?? undefined) : undefined}
            maxLength={setting.constraints.maxLength ?? undefined}
            pattern={setting.constraints.pattern ?? undefined}
            value={value}
            aria-invalid={shownIssue ? true : undefined}
            aria-describedby={`setting-${setting.key}-hint`}
            onChange={(e) => { setDraft(e.target.value); setIssue(null) }}
          />
          <p id={`setting-${setting.key}-hint`} className="text-xs text-muted">
            {hint}
          </p>
        </div>
      )}
      {shownIssue ? (
        <p role="alert" className="text-sm font-medium text-red-600 dark:text-red-400">
          {shownIssue}
        </p>
      ) : null}
      <div className="flex flex-wrap gap-2">
        <Button type="button" size="sm" disabled={!dirty || !!clientIssue || busy} aria-label={t('saveNamed', { name: label })} onClick={save}>
          {updating.loading ? t('saving') : t('save')}
        </Button>
        {setting.overridden ? (
          <Button type="button" size="sm" variant="secondary" disabled={busy} aria-label={t('resetNamed', { name: label })} onClick={() => void restore()}>
            {resetting.loading ? t('resetting') : t('reset')}
          </Button>
        ) : null}
      </div>
      <Dialog open={confirming} onClose={() => setConfirming(false)} title={t('confirmTitle')}>
        <div className="flex flex-col gap-4">
          <p className="text-sm">{riskyCopy(t, setting, value)}</p>
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setConfirming(false)}>
              {t('confirmCancel')}
            </Button>
            <Button type="button" disabled={busy} onClick={() => void send(value)}>
              {t('confirmSave')}
            </Button>
          </div>
        </div>
      </Dialog>
    </article>
  )
}

function Switch({ id, label, hint, checked, invalid, onChange }: { id: string; label: string; hint: string; checked: boolean; invalid: boolean; onChange: (on: boolean) => void }) {
  const hintId = `${id}-hint`
  return (
    <div className="flex items-start justify-between gap-4">
      <p id={hintId} className="text-sm text-muted">
        {hint}
      </p>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={label}
        aria-describedby={hintId}
        aria-invalid={invalid || undefined}
        onClick={() => onChange(!checked)}
        className={cn('relative mt-0.5 h-7 w-12 shrink-0 rounded-full transition-colors', checked ? 'bg-accent' : 'bg-border')}
      >
        <span aria-hidden className={cn('absolute top-0.5 size-6 rounded-full bg-white shadow', checked ? 'left-5' : 'left-0.5')} />
      </button>
    </div>
  )
}

function Badge({ children, muted }: { children: ReactNode; muted?: boolean }) {
  return <span className={muted ? 'rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted' : 'rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent'}>{children}</span>
}

function describe(setting: Setting, value: string, t: ReturnType<typeof useTranslations<'adminSettings'>>): string {
  const parts = [setting.description]
  if (setting.type === 'INTEGER') {
    const min = effectiveIntegerMin(setting)
    const max = setting.constraints.max
    if (min != null && max != null) parts.push(t('between', { min, max }))
    else if (min != null) parts.push(t('atLeast', { min }))
    else if (max != null) parts.push(t('atMost', { max }))
    if (setting.constraints.nullable) parts.push(t('emptyClears'))
    if (setting.key === 'ai_monthly_budget_micro_usd' && value.trim()) {
      const usd = microUsdToUsd(value)
      if (usd != null) parts.push(t('budgetUsd', { amount: new Intl.NumberFormat('en', { style: 'currency', currency: 'USD' }).format(usd) }))
    }
  }
  if (setting.type === 'STRING' && setting.constraints.maxLength != null) parts.push(t('maxLength', { max: setting.constraints.maxLength }))
  return parts.filter(Boolean).join(' ')
}

function issueText(t: ReturnType<typeof useTranslations<'adminSettings'>>, setting: SettingShape, issue: SettingIssue): string {
  const min = effectiveIntegerMin(setting)
  if (issue === 'min' || issue === 'minimumAge') return issue === 'minimumAge' ? t('issues.minimumAge') : t('issues.min', { min: min ?? 0 })
  if (issue === 'max') return t('issues.max', { max: setting.constraints.max ?? 0 })
  if (issue === 'maxLength') return t('issues.maxLength', { max: setting.constraints.maxLength ?? 0 })
  return t(`issues.${issue}`)
}

function riskyCopy(t: ReturnType<typeof useTranslations<'adminSettings'>>, setting: Setting, value: string): string {
  if (setting.key === 'account_minimum_age') return t('risky.account_minimum_age', { value })
  if (setting.key === 'digital_consent_age') return t('risky.digital_consent_age', { value })
  if (t.has(`risky.${setting.key}`)) return t(`risky.${setting.key}`)
  return t('risky.generic', { name: setting.key })
}
