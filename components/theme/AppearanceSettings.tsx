'use client'

import { useTranslations } from 'next-intl'
import { AppearanceControls } from './AppearanceControls'

/** Account settings card. Same controls as the header panel, always visible. */
export function AppearanceSettings() {
  const t = useTranslations('site.theme')
  return (
    <section aria-labelledby="account-appearance" className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-5">
      <div>
        <h2 id="account-appearance" className="text-base font-semibold">{t('appearance')}</h2>
        <p className="mt-1 text-sm text-muted">{t('hint')}</p>
      </div>
      <AppearanceControls />
    </section>
  )
}
