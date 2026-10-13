import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Rhythm } from '@/features/learning/Rhythm'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('rhythm'))('title'), robots: { index: false } }
}

/** The signed-in person's Rhythm (lvn-backend ADR-0030, ADR-0069). */
export default function RhythmPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Rhythm />
    </div>
  )
}
