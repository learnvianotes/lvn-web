import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { History } from '@/features/learning/History'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('history'))('title'), robots: { index: false } }
}

/** The signed-in person's learning history (lvn-backend ADR-0067). */
export default function HistoryPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <History />
    </div>
  )
}
