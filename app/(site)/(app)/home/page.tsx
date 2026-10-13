import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Home } from '@/features/learning/Home'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('homeDashboard'))('title'), robots: { index: false } }
}

/** A signed-in learner's Home (P6h). */
export default function HomeRoute() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Home />
    </div>
  )
}
