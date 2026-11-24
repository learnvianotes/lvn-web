import { getTranslations } from 'next-intl/server'
import { Highlights } from './Highlights'

/**
 * The side of the sign-in pages from `lg`: what LearnViaNotes is, on paper, with the highlighter on the phrase that
 * matters (ADR-0114). Phones show the form alone, so signing in is one screen. Not a heading: each page's title is its h1.
 */
export async function AuthHero() {
  const t = await getTranslations('auth.welcome')
  return (
    <aside className="hidden lg:sticky lg:top-20 lg:flex lg:min-h-[32rem] lg:flex-col lg:justify-center lg:gap-6 lg:py-12 lg:pe-8">
      <p className="text-4xl leading-[1.1] font-medium text-balance tracking-[-0.02em]">
        {t('headlineLead')} <span className="lvn-marker">{t('headlineMark')}</span>
      </p>
      <p className="max-w-md text-lg text-pretty text-muted">{t('lead')}</p>
      <Highlights className="mt-2" />
    </aside>
  )
}
