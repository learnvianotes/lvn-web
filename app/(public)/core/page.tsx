import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { CategorySections } from '@/features/core-content/components/CategorySections'
import { getCatalog } from '@/features/core-content/source'

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('core')
  return { title: t('title'), description: t('lead'), alternates: { canonical: '/core' } }
}

export default async function CorePage() {
  const t = await getTranslations('core')
  return (
    <div className="mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight">{t('title')}</h1>
      <p className="mt-2 max-w-2xl text-muted">{t('lead')}</p>
      <div className="mt-10">
        <CategorySections catalog={getCatalog()} />
      </div>
    </div>
  )
}
