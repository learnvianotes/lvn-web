import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { Highlights } from '@/components/auth/Highlights'
import { WelcomeCard } from '@/components/auth/WelcomeCard'
import { NightSky } from '@/components/brand/NightSky'
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
      {/* The night-sky hero of the mobile welcome screen: what LearnViaNotes is, and one tap in with Google. */}
      <NightSky as="section">
        {/* Phones: the pitch, then the way in, then the notes. From lg the card sits beside both. */}
        <div className="mx-auto grid max-w-6xl gap-8 px-4 py-10 sm:py-20 lg:grid-cols-[minmax(0,1fr)_26rem] lg:items-center lg:gap-x-16 lg:gap-y-8">
          <div className="animate-rise">
            <p className="text-sm font-semibold uppercase tracking-wider text-[#C7D2FE]">{t('eyebrow')}</p>
            <h1 className="mt-3 max-w-3xl text-4xl font-extrabold tracking-tight text-balance sm:text-5xl">{t('title')}</h1>
            <p className="mt-4 max-w-2xl text-base text-white/80 text-pretty sm:text-lg">
              {t('lead', { subjects: catalog.subjects.length, topics, problems })}
            </p>
            <Highlights className="mt-8 hidden sm:flex" />
          </div>
          <div className="lg:col-start-2 lg:row-span-2 lg:row-start-1">
            <AuthProvider>
              <WelcomeCard />
            </AuthProvider>
          </div>
          <div className="lg:-mt-4">
            <Link href="/core" className="inline-flex h-11 items-center gap-2 rounded-full border border-white/30 px-5 text-sm font-semibold text-white transition-colors hover:bg-white/10">
              {t('cta')} <i className="ti ti-arrow-right" aria-hidden />
            </Link>
          </div>
        </div>
      </NightSky>
      <div className="mx-auto max-w-6xl px-4 py-12">
        <h2 className="sr-only">{t('categories')}</h2>
        <CategorySections catalog={catalog} headingLevel="h3" />
      </div>
    </>
  )
}
