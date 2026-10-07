import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { Button } from '@/components/ui/button'
import { CategorySections } from '@/features/core-content/components/CategorySections'
import { getCatalog } from '@/features/core-content/source'

export default async function HomePage() {
  const t = await getTranslations('home')
  const catalog = getCatalog()
  const notes = catalog.subjects.filter((s) => s.kind === 'notes')
  const problems = catalog.subjects.filter((s) => s.kind === 'problems').reduce((n, s) => n + s.itemCount, 0)
  const topics = notes.reduce((n, s) => n + s.topics.length, 0)

  return (
    <>
      <section className="border-b border-border bg-surface">
        <div className="mx-auto max-w-6xl px-4 py-14 sm:py-20">
          <p className="text-sm font-semibold uppercase tracking-wider text-accent">{t('eyebrow')}</p>
          <h1 className="mt-3 max-w-3xl text-4xl font-bold tracking-tight text-balance sm:text-5xl">{t('title')}</h1>
          <p className="mt-4 max-w-2xl text-lg text-muted text-pretty">
            {t('lead', { subjects: catalog.subjects.length, topics, problems })}
          </p>
          <Button asChild className="mt-8">
            <Link href="/core">
              {t('cta')} <i className="ti ti-arrow-right" aria-hidden />
            </Link>
          </Button>
        </div>
      </section>
      <div className="mx-auto max-w-6xl px-4 py-12">
        <h2 className="sr-only">{t('categories')}</h2>
        <CategorySections catalog={catalog} headingLevel="h3" />
      </div>
    </>
  )
}
