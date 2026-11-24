import { ArrowRight } from 'lucide-react'
import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { FeatureTiles } from '@/components/landing/FeatureTiles'
import { HeroActions } from '@/components/landing/HeroActions'
import { HeroPreview } from '@/components/landing/HeroPreview'
import { RedirectSignedInHome } from '@/components/landing/RedirectSignedInHome'
import { listSubjects } from '@/features/subjects/data'
import { SubjectGrid } from '@/features/subjects/SubjectGrid'
import { env } from '@/lib/env'

/** The site's own title (not "… · LearnViaNotes"), the layout's description, and its canonical address. */
export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('site')
  return { title: { absolute: t('homeTitle') }, alternates: { canonical: '/' } }
}

/**
 * The landing page (lvn-backend ADR-0076, restyled by ADR-0114): a split hero that says what the product does, with the
 * product itself as the visual, the six ways in, then the subjects notes are organised by (the app's own, not /core).
 */
// Rendered on request, never at build time (the API is not there while images build); the subjects are cached an hour.
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  const [t, site] = await Promise.all([getTranslations('home'), getTranslations('site')])
  const subjects = await listSubjects().catch(() => [])
  const url = `${env.NEXT_PUBLIC_SITE_URL}/`
  // schema.org: the site and who runs it, for search results (escaped so no "<" closes the script early).
  const jsonLd = [
    { '@context': 'https://schema.org', '@type': 'WebSite', name: site('name'), url },
    { '@context': 'https://schema.org', '@type': 'Organization', name: site('name'), url, logo: `${env.NEXT_PUBLIC_SITE_URL}/icons/icon-512.png` },
  ]
  return (
    <>
      <RedirectSignedInHome />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
      <section className="border-b border-border bg-bg">
        <div className="mx-auto grid max-w-6xl items-center gap-12 px-4 py-12 sm:py-20 lg:grid-cols-[minmax(0,1fr)_minmax(0,30rem)] lg:py-24">
          <div className="flex animate-rise flex-col gap-5">
            <h1 className="text-4xl leading-[1.08] font-medium text-balance sm:text-5xl sm:tracking-[-0.02em] lg:text-6xl lg:tracking-[-0.03em]">
              {t('hero.titleLead')} <span className="lvn-marker">{t('hero.titleAccent')}</span>
            </h1>
            <p className="max-w-[36rem] text-base text-muted text-pretty sm:text-lg">{t('hero.lead')}</p>
            <HeroActions />
            <Link href="/subjects" className="inline-flex w-fit items-center gap-2 text-sm font-semibold text-accent hover:underline">
              {t('cta')} <ArrowRight className="size-4" aria-hidden />
            </Link>
          </div>
          <HeroPreview className="mx-auto w-full max-w-md lg:max-w-none" />
        </div>
      </section>
      <FeatureTiles />
      {subjects.length ? (
        <div id="subjects" className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-12">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="text-2xl font-semibold">{t('categories')}</h2>
            <Link href="/subjects" className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:underline">
              {t('allSubjects')} <ArrowRight className="size-4" aria-hidden />
            </Link>
          </div>
          <SubjectGrid subjects={subjects.slice(0, 9)} headingLevel="h3" />
        </div>
      ) : null}
    </>
  )
}
