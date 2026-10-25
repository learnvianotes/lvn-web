'use client'

import { Info } from 'lucide-react'
import { useState } from 'react'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'

/**
 * Shown when sign-up returns AGE_RESTRICTED, or when an AGE_BLOCKED account signs in.
 * The person can write to the admin and copy the address. It is not the day-long sign-up block.
 */
export function AgeBlocked({ supportEmail }: { supportEmail: string }) {
  const t = useTranslations('auth.age')
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    if (!supportEmail) return
    try {
      await navigator.clipboard.writeText(supportEmail)
      setCopied(true)
    } catch {
      setCopied(false)
    }
  }
  return (
    <section role="status" aria-labelledby="age-blocked" className="flex flex-col gap-4">
      <h1 id="age-blocked" className="flex items-center gap-2 text-2xl font-bold tracking-tight">
        <Info className="size-6 shrink-0 text-accent" aria-hidden />
        {t('blockedTitle')}
      </h1>
      <p className="text-sm">{t('blockedLead')}</p>
      <p className="text-sm text-muted">{supportEmail ? t('blockedWrong', { email: supportEmail }) : t('blockedNoEmail')}</p>
      {supportEmail ? (
        <div className="flex flex-wrap items-center gap-2">
          <a href={`mailto:${supportEmail}`} className="font-medium text-accent hover:underline">
            {supportEmail}
          </a>
          <Button type="button" size="sm" variant="secondary" onClick={() => void copy()}>
            {copied ? t('copied') : t('copyEmail')}
          </Button>
        </div>
      ) : null}
    </section>
  )
}
