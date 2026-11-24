'use client'

import { useEffect, useState } from 'react'
import { useTranslations } from 'next-intl'
import { loadAnalyticsOptOut, saveAnalyticsOptOut } from '@/lib/platform-api'
import { setUsageOptOut } from '@/lib/analytics'
import { cn } from '@/lib/cn'

/** Profile switch for the first-party usage log. Errors are still recorded. */
export function AnalyticsOptOut({ className }: { className?: string }) {
  const t = useTranslations('profile.analytics')
  const [optedOut, setOptedOut] = useState<boolean | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  useEffect(() => {
    let gone = false
    void loadAnalyticsOptOut()
      .then((value) => {
        if (gone) return
        setOptedOut(value)
        setUsageOptOut(value)
      })
      .catch(() => {
        if (!gone) setError(t('failed'))
      })
    return () => {
      gone = true
    }
  }, [t])
  const toggle = async () => {
    if (optedOut == null) return
    const next = !optedOut
    setBusy(true)
    setError(null)
    try {
      const problem = await saveAnalyticsOptOut(next)
      if (problem) setError(problem)
      else {
        setOptedOut(next)
        setUsageOptOut(next)
      }
    } catch {
      setError(t('failed'))
    } finally {
      setBusy(false)
    }
  }
  return (
    <section className={className} aria-labelledby="analytics-choice">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 id="analytics-choice" className="text-lg font-semibold">{t('title')}</h2>
          <p className="text-sm text-muted">{t('lead')}</p>
        </div>
        <button type="button" role="switch" aria-checked={optedOut === true} aria-label={t('title')} disabled={optedOut == null || busy} onClick={() => void toggle()} className={cn('relative h-7 w-12 shrink-0 rounded-full transition-colors disabled:opacity-50', optedOut ? 'bg-accent' : 'bg-border')}>
          <span className={cn('absolute top-0.5 size-6 rounded-full bg-bg shadow', optedOut ? 'left-5' : 'left-0.5')} />
        </button>
      </div>
      {error ? <p role="alert" className="text-sm text-bad">{error}</p> : null}
    </section>
  )
}
