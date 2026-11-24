import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Home } from '@/features/learning/Home'
import { listSubjects } from '@/features/subjects/data'
import { SubjectSpotlight } from '@/features/subjects/SubjectSpotlight'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('homeDashboard'))('title'), robots: { index: false } }
}

/** A signed-in learner's Home (P6h), with subjects in reach. */
export default async function HomeRoute() {
  const subjects = await listSubjects().catch(() => [])
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Home />
      <SubjectSpotlight subjects={subjects} />
    </div>
  )
}
