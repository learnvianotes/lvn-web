'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useUnverifiedGates } from './useUnverifiedGates'

/** Why a control is closed, and where to confirm the sign-in email. Hidden unless the public list names this action. */
export function GatedNotice({ feature, when = true }: { feature: string; when?: boolean }) {
  const t = useTranslations('auth.gates')
  const { gated } = useUnverifiedGates()
  if (!when || !gated(feature)) return null
  return (
    <p className="text-sm text-muted">
      {t('why')}{' '}
      <Link href="/profile#verify-email" className="font-semibold text-accent hover:underline">
        {t('how')}
      </Link>
    </p>
  )
}
