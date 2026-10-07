import { getTranslations } from 'next-intl/server'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

export default async function PublicLayout({ children }: { children: React.ReactNode }) {
  const t = await getTranslations('site')
  return (
    <>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2">
        {t('skip')}
      </a>
      <SiteHeader />
      <main id="main" className="min-h-[70dvh]">{children}</main>
      <SiteFooter />
    </>
  )
}
