'use client'

import { CalendarCheck, Info } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useSyncExternalStore, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { ageRefusedAt, birthDateInWords, subscribeAgeRefusal } from '@/lib/age'

/** Whether this device was refused an account in the last day (lvn-backend ADR-0091); false while rendering on the server. */
export function useAgeRefused(): boolean {
  return useSyncExternalStore(subscribeAgeRefusal, () => ageRefusedAt() !== null, () => false)
}

/** The date of birth field's hint: the chosen date in words, then the usual hint. */
export function BirthDateHint({ value, hint }: { value: string; hint: string }) {
  const words = birthDateInWords(value)
  return words ? (
    <>
      <strong className="font-semibold text-fg">{words}</strong> · {hint}
    </>
  ) : (
    hint
  )
}

/**
 * "Is this right?" — asked before every date of birth is sent, whatever the answer, so no answer stands out and one
 * mis-picked year can't refuse or erase an account (lvn-backend ADR-0091).
 */
export function ConfirmBirthDate({ value, busy, onConfirm, onChange }: { value: string | null; busy: boolean; onConfirm: () => void; onChange: () => void }) {
  const t = useTranslations('auth.age')
  return (
    <Dialog open={value !== null} onClose={onChange} title={t('confirmTitle')}>
      <div className="flex flex-col gap-4">
        <p className="flex items-center gap-3 text-sm">
          <CalendarCheck className="size-5 shrink-0 text-accent" aria-hidden />
          <span>
            {t('confirmLead')} <strong className="text-base">{value ? birthDateInWords(value) : ''}</strong>
          </span>
        </p>
        <div className="flex flex-wrap justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onChange} disabled={busy}>
            {t('change')}
          </Button>
          <Button type="button" onClick={onConfirm} disabled={busy}>
            {t('confirm')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

/** Shown instead of the sign-up forms on a device refused in the last day. It deletes nothing and signs nobody out. */
export function AgeRefused({ action }: { action?: ReactNode }) {
  const t = useTranslations('auth.age')
  return (
    <section role="status" aria-labelledby="age-refused" className="flex flex-col gap-4">
      <h1 id="age-refused" className="flex items-center gap-2 text-2xl font-bold tracking-tight">
        <Info className="size-6 text-accent" aria-hidden />
        {t('refusedTitle')}
      </h1>
      <p className="text-sm text-muted">{t('refusedLead')}</p>
      <div className="flex flex-wrap gap-2">
        <Button asChild>
          <Link href="/subjects">{t('browse')}</Link>
        </Button>
        {action}
      </div>
    </section>
  )
}
