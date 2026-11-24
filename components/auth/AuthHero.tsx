import { getTranslations } from 'next-intl/server'
import { NightSky } from '@/components/brand/NightSky'
import { Highlights } from './Highlights'

/**
 * The night-sky side of the sign-in pages: a banner above the form on phones, a panel beside it from `lg`. The
 * headline is not a heading — each page's own title is its h1.
 */
export async function AuthHero() {
  const t = await getTranslations('auth.welcome')
  return (
    <NightSky className="px-6 pb-14 pt-8 sm:px-8 lg:sticky lg:top-20 lg:flex lg:min-h-[34rem] lg:flex-col lg:justify-center lg:rounded-3xl lg:p-12">
      <div className="flex animate-rise flex-col gap-3 lg:gap-5">
        <p className="text-2xl font-semibold leading-tight tracking-tight text-balance sm:text-3xl lg:text-4xl">{t('headline')}</p>
        <p className="max-w-md text-pretty text-inverse-muted">{t('lead')}</p>
        <Highlights className="mt-3 hidden sm:flex" />
      </div>
    </NightSky>
  )
}
