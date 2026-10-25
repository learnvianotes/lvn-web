'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation } from '@apollo/client/react'
import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { UpdateAdminSettingDocument } from '@/graphql/generated/graphql'
import {
  STUDENT_ID_AI_AUTO_APPROVE,
  STUDENT_ID_AI_CHECK,
  STUDENT_ID_AI_CONFIDENCE_THRESHOLD,
  STUDENT_ID_IMAGE_RETENTION_DAYS,
} from '@/lib/platform-api'
import { cn } from '@/lib/cn'

type CatalogSetting = {
  key: string
  type: string
  value: string
  description: string
  constraints: { min: number | null; max: number | null; nullable: boolean }
}

/** The college-ID check, saved with `updateAdminSetting` under the catalog keys. */
export function AiCheckSettingsCard({ settings, onSaved }: { settings: CatalogSetting[]; onSaved: () => void }) {
  const t = useTranslations('adminAiCheck')
  const [update, updating] = useMutation(UpdateAdminSettingDocument)
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)
  const byKey = new Map(settings.map((setting) => [setting.key, setting]))
  if (!byKey.size) return null

  const valueOf = (key: string) => drafts[key] ?? byKey.get(key)?.value ?? ''
  const save = async (key: string, value: string) => {
    setError(null)
    try {
      const res = await update({ variables: { input: { key, value } } })
      const problem = res.data?.updateAdminSetting.userErrors[0]?.message
      if (problem) {
        setError(problem)
        return
      }
      setDrafts((current) => ({ ...current, [key]: value }))
      onSaved()
    } catch (err) {
      setError(CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  const check = byKey.get(STUDENT_ID_AI_CHECK)
  const auto = byKey.get(STUDENT_ID_AI_AUTO_APPROVE)
  const threshold = byKey.get(STUDENT_ID_AI_CONFIDENCE_THRESHOLD)
  const retention = byKey.get(STUDENT_ID_IMAGE_RETENTION_DAYS)

  return (
    <section aria-labelledby="ai-check" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <h2 id="ai-check" className="text-lg font-semibold">{t('title')}</h2>
      <p className="text-sm text-muted">{t('lead')}</p>
      {check ? (
        <Toggle label={t('check')} hint={check.description || t('checkHint')} on={valueOf(check.key) === 'true'} disabled={updating.loading} onClick={() => void save(check.key, valueOf(check.key) === 'true' ? 'false' : 'true')} />
      ) : null}
      {auto ? (
        <Toggle label={t('auto')} hint={auto.description || t('autoHint')} on={valueOf(auto.key) === 'true'} disabled={updating.loading} onClick={() => void save(auto.key, valueOf(auto.key) === 'true' ? 'false' : 'true')} />
      ) : null}
      {threshold ? <NumberRow setting={threshold} label={t('threshold')} value={valueOf(threshold.key)} busy={updating.loading} onChange={(value) => setDrafts((current) => ({ ...current, [threshold.key]: value }))} onSave={() => void save(threshold.key, valueOf(threshold.key))} /> : null}
      {retention ? <NumberRow setting={retention} label={t('retention')} value={valueOf(retention.key)} busy={updating.loading} onChange={(value) => setDrafts((current) => ({ ...current, [retention.key]: value }))} onSave={() => void save(retention.key, valueOf(retention.key))} /> : null}
      {error ? <Alert tone="error">{error}</Alert> : null}
    </section>
  )
}

function Toggle({ label, hint, on, disabled, onClick }: { label: string; hint: string; on: boolean; disabled: boolean; onClick: () => void }) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="font-medium">{label}</p>
        <p className="text-sm text-muted">{hint}</p>
      </div>
      <button type="button" role="switch" aria-checked={on} aria-label={label} disabled={disabled} onClick={onClick} className={cn('relative h-7 w-12 shrink-0 rounded-full transition-colors disabled:opacity-50', on ? 'bg-accent' : 'bg-border')}>
        <span className={cn('absolute top-0.5 size-6 rounded-full bg-bg shadow', on ? 'left-5' : 'left-0.5')} />
      </button>
    </div>
  )
}

function NumberRow({ setting, label, value, busy, onChange, onSave }: { setting: CatalogSetting; label: string; value: string; busy: boolean; onChange: (value: string) => void; onSave: () => void }) {
  const t = useTranslations('adminAiCheck')
  const dirty = value !== setting.value
  return (
    <div className="flex flex-col gap-2 sm:flex-row sm:items-end">
      <label className="flex min-w-0 flex-1 flex-col gap-1">
        <span className="font-medium">{label}</span>
        <span className="text-sm text-muted">{setting.description}</span>
        <Input type="number" inputMode="numeric" min={setting.constraints.min ?? undefined} max={setting.constraints.max ?? undefined} value={value} aria-label={label} onChange={(e) => onChange(e.target.value)} />
      </label>
      <Button type="button" size="sm" disabled={!dirty || busy} onClick={onSave}>{t('save')}</Button>
    </div>
  )
}
