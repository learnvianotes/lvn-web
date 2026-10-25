'use client'

import { useEffect, useState } from 'react'
import { useTranslations } from 'next-intl'
import { Alert } from '@/components/ui/alert'
import { loadAiCheckSettings, saveAiCheckSettings, type AiCheckSettings } from '@/lib/platform-api'
import { cn } from '@/lib/cn'

/** The two verification switches from the platform API: run the ID-card check, and auto-approve a confident match. */
export function AiCheckSettingsCard() {
  const t = useTranslations('adminAiCheck')
  const [settings, setSettings] = useState<AiCheckSettings | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    let gone = false
    void loadAiCheckSettings()
      .then((next) => {
        if (!gone) setSettings(next)
      })
      .catch(() => {
        if (!gone) setError(t('failed'))
      })
    return () => {
      gone = true
    }
  }, [t])

  const toggle = async (key: keyof AiCheckSettings) => {
    if (!settings) return
    const next = { ...settings, [key]: !settings[key] }
    setBusy(true)
    setError(null)
    setSettings(next)
    try {
      const problem = await saveAiCheckSettings(next)
      if (problem) {
        setSettings(settings)
        setError(problem)
      }
    } catch {
      setSettings(settings)
      setError(t('failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section aria-labelledby="ai-check" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <h2 id="ai-check" className="text-lg font-semibold">{t('title')}</h2>
      <p className="text-sm text-muted">{t('lead')}</p>
      <Toggle label={t('check')} hint={t('checkHint')} on={settings?.aiCheckEnabled === true} disabled={!settings || busy} onClick={() => void toggle('aiCheckEnabled')} />
      <Toggle label={t('auto')} hint={t('autoHint')} on={settings?.autoApproveOnHighConfidence === true} disabled={!settings || busy} onClick={() => void toggle('autoApproveOnHighConfidence')} />
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
