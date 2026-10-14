import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ContestsPage } from '@/features/contests/ContestsPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('contests'))('title'), robots: { index: false } }
}

/** Weekly contests (lvn-backend ADR-0082). */
export default function Contests() {
  return (
    <div className="mx-auto w-full max-w-3xl">
      <ContestsPage />
    </div>
  )
}
