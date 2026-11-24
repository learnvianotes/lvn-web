'use client'

import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'

/** A server render that threw (the API did not answer, or something else broke). Not a 404. */
export default function SiteError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const t = useTranslations('states')
  return (
    <main id="main" className="mx-auto flex min-h-[50dvh] max-w-lg flex-col items-start justify-center gap-4 px-4 py-16">
      <h1 className="text-2xl font-semibold">{t('loadFailed')}</h1>
      <p className="text-sm text-muted">{t('offline')}</p>
      <Button type="button" onClick={() => reset()}>
        {t('retry')}
      </Button>
    </main>
  )
}
