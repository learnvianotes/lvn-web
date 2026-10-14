import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { listSubjects } from '@/features/subjects/data'
import { SubjectGrid } from '@/features/subjects/SubjectGrid'

export const revalidate = 3600

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('subjects')
  return { title: t('title'), description: t('lead'), alternates: { canonical: '/subjects' } }
}

/** Every subject LearnViaNotes organises notes by (owner, 2026-10-14: the app's own, not /core). */
export default async function SubjectsPage() {
  const t = await getTranslations('subjects')
  const subjects = await listSubjects().catch(() => [])
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10">
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="max-w-2xl text-muted">{t('lead')}</p>
      </header>
      {subjects.length ? <SubjectGrid subjects={subjects} /> : <p className="text-muted">{t('unavailable')}</p>}
    </div>
  )
}
