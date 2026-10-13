import { getTranslations } from 'next-intl/server'
import { PublicFrame } from '@/components/shell/PublicFrame'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

export default async function PublicLayout({ children }: { children: React.ReactNode }) {
  const t = await getTranslations('site')
  return (
    <PublicFrame skip={t('skip')} header={<SiteHeader />} footer={<SiteFooter />}>
      {children}
    </PublicFrame>
  )
}
