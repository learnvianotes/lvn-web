import { getTranslations } from 'next-intl/server'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { HomeLink } from '@/components/brand/HomeLink'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'
import { Button } from '@/components/ui/button'

export default async function NotFound() {
  const t = await getTranslations('notFound')
  return (
    <AuthProvider>
      <SiteHeader />
      <main id="main" className="mx-auto flex min-h-[60dvh] max-w-xl flex-col items-start justify-center gap-4 px-4 py-16">
        <h1 className="text-3xl font-semibold tracking-tight">{t('title')}</h1>
        <p className="text-muted">{t('lead')}</p>
        <Button asChild>
          <HomeLink label={t('home')}>{t('home')}</HomeLink>
        </Button>
      </main>
      <SiteFooter />
    </AuthProvider>
  )
}
