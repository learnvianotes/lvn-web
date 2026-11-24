'use client'

import { useMutation } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ResendVerificationDocument } from '@/graphql/generated/graphql'
import { isKnownGatedAction } from '@/lib/auth/gates'
import { resendVerificationNotice } from '@/lib/auth/resend'
import { useUnverifiedGates } from './useUnverifiedGates'

/**
 * On every signed-in page while the sign-in email is unconfirmed, except for platform admins.
 * Resend calls resendVerification. A RATE_LIMITED answer shows retryAfter.
 */
export function VerifyEmailBanner() {
  const t = useTranslations('auth.verify')
  const tg = useTranslations('auth.gates')
  const te = useTranslations('auth.errors')
  const { viewer, held, actions } = useUnverifiedGates()
  const [resend, pending] = useMutation(ResendVerificationDocument)
  const [note, setNote] = useState<string | null>(null)
  const [problem, setProblem] = useState<string | null>(null)
  if (!viewer || !held) return null
  const heldBack = actions.map((action) => (isKnownGatedAction(action) ? tg(`features.${action}`) : tg('unknown', { action })))

  const again = async () => {
    setNote(null)
    setProblem(null)
    try {
      const { data } = await resend()
      const payload = data?.resendVerification
      if (payload?.ok) {
        setNote(t('resentLink'))
        return
      }
      const notice = resendVerificationNotice(payload?.userErrors, (seconds) => t('retryAfter', { seconds }))
      setProblem(notice.tone === 'error' && notice.message ? notice.message : te('generic'))
    } catch {
      setProblem(te('generic'))
    }
  }

  return (
    <section id="verify-email" role="region" aria-labelledby="verify-email-title" className="scroll-mt-20 border-b border-accent/30 bg-accent-soft px-4 py-3 text-sm text-fg">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="min-w-0 flex-1">
          <h2 id="verify-email-title" className="font-semibold">
            {t('bannerTitle')}
          </h2>
          <p className="text-muted">{viewer.email ? t('bannerLead', { email: viewer.email }) : t('bannerLeadNoEmail')}</p>
          <p>{heldBack.length ? tg('held', { features: heldBack.join(', ') }) : tg('open')}</p>
          {note ? (
            <p role="status" className="mt-1 font-medium">
              {note}
            </p>
          ) : null}
          {problem ? (
            <p role="alert" className="mt-1 text-bad">
              {problem}
            </p>
          ) : null}
        </div>
        <Button type="button" size="sm" className="w-full sm:w-auto" disabled={pending.loading} onClick={() => void again()}>
          {t('resendLink')}
        </Button>
      </div>
    </section>
  )
}
