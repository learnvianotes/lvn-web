'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useSyncExternalStore } from 'react'
import { Button } from '@/components/ui/button'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'
import { createAnalytics } from '@/lib/analytics'
import { getAnalyticsConsent, setAnalyticsConsent, subscribeConsent, type AnalyticsChoice } from '@/lib/consent'
import { env } from '@/lib/env'

/** This deployment's Google Analytics, or an inert stand-in when NEXT_PUBLIC_GA_MEASUREMENT_ID is unset (ADR-0092). */
const analytics = createAnalytics(env.NEXT_PUBLIC_GA_MEASUREMENT_ID)

/** The visitor's choice; 'pending' until hydrated, so nobody sees the banner flash who has already chosen. */
function useAnalyticsChoice(): AnalyticsChoice | null | 'pending' {
  return useSyncExternalStore(subscribeConsent, () => getAnalyticsConsent(), () => 'pending' as const)
}

/** Runs analytics as the visitor allows, sends path-only page views, and asks once (lvn-backend ADR-0092). */
export function Analytics() {
  const path = usePathname()
  const choice = useAnalyticsChoice()
  useEffect(() => analytics.start(), [])
  useEffect(() => {
    if (choice === 'granted') analytics.pageView(path)
  }, [path, choice])
  return analytics.available && choice === null ? <ConsentBanner /> : null
}

/** Both answers weigh the same; the Privacy Policy is one click away. */
function ConsentBanner() {
  const t = useTranslations('consent')
  return (
    <section
      aria-label={t('region')}
      className="fixed inset-x-3 bottom-[calc(0.75rem+env(safe-area-inset-bottom))] z-50 mx-auto flex max-w-3xl flex-col gap-3 rounded-2xl border border-border bg-surface p-4 text-sm shadow-2xl sm:flex-row sm:items-center"
    >
      <p className="flex-1 text-muted">
        {t.rich('text', {
          strong: (chunks) => <strong className="font-semibold text-fg">{chunks}</strong>,
          privacy: (chunks) => (
            <Link href={LEGAL_DOCUMENTS.privacy.path} className="font-medium text-accent underline underline-offset-2">
              {chunks}
            </Link>
          ),
        })}
      </p>
      <div className="flex shrink-0 gap-2">
        <Button variant="secondary" size="sm" className="flex-1 sm:min-w-24" onClick={() => setAnalyticsConsent('denied')}>
          {t('deny')}
        </Button>
        <Button variant="secondary" size="sm" className="flex-1 sm:min-w-24" onClick={() => setAnalyticsConsent('granted')}>
          {t('allow')}
        </Button>
      </div>
    </section>
  )
}

/** In the footer of every page where analytics exists: forgets the choice, so the banner asks again. */
export function AnalyticsChoiceButton() {
  const t = useTranslations('consent')
  if (!analytics.available) return null
  return (
    <button type="button" onClick={() => setAnalyticsConsent(null)} className="hover:text-fg hover:underline">
      {t('change')}
    </button>
  )
}
