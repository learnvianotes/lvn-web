'use client'

import { Info, UserCheck } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useSyncExternalStore, type ReactNode } from 'react'
import { z } from 'zod'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { AGE_MAX, AGE_MIN, ageRefusedAt, parseAge, subscribeAgeRefusal, type AgeProblem } from '@/lib/age'

/** Whether this device was refused an account in the last day (lvn-backend ADR-0091); false while rendering on the server. */
export function useAgeRefused(): boolean {
  return useSyncExternalStore(subscribeAgeRefusal, () => ageRefusedAt() !== null, () => false)
}

/**
 * The sign-up forms' age field (lvn-backend ADR-0104): the text typed in, whole years out. When it is not an age, the
 * error's message is the AgeProblem, which useAgeMessage puts into words.
 */
export const ageField = z.string().transform((text, ctx) => {
  const parsed = parseAge(text)
  if ('problem' in parsed) {
    ctx.addIssue({ code: 'custom', message: parsed.problem })
    return z.NEVER
  }
  return parsed.age
})

const PROBLEMS: readonly AgeProblem[] = ['required', 'whole', 'range']

/** The age field's error in words: the API's own message as it is, else what the form's check found. */
export function useAgeMessage(): (error: { type?: string; message?: string } | undefined) => string | undefined {
  const t = useTranslations('auth.age')
  return (error) => {
    if (!error) return undefined
    if (error.type === 'server' && error.message) return error.message
    const problem = PROBLEMS.find((p) => p === error.message) ?? 'required'
    return t(`problems.${problem}`, { min: AGE_MIN, max: AGE_MAX })
  }
}

/**
 * "Is this right?" — asked before every age is sent, whatever the answer, so no answer stands out and one mistyped
 * number can't refuse or hold an account (lvn-backend ADR-0091, ADR-0104).
 */
export function ConfirmAge({ age, busy, onConfirm, onChange }: { age: number | null; busy: boolean; onConfirm: () => void; onChange: () => void }) {
  const t = useTranslations('auth.age')
  return (
    <Dialog open={age !== null} onClose={onChange} title={t('confirmTitle')}>
      <div className="flex flex-col gap-4">
        <p className="flex items-center gap-3 text-sm">
          <UserCheck className="size-5 shrink-0 text-accent" aria-hidden />
          <span>{age !== null ? t.rich('confirmAge', { age, strong: (chunks) => <strong className="text-base">{chunks}</strong> }) : null}</span>
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
