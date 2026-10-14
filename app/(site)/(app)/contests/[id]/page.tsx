import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ContestPage } from '@/features/contests/ContestPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('contests'))('title'), robots: { index: false } }
}

/** One weekly contest: start, the timed attempt, and the answers after (lvn-backend ADR-0082). */
export default async function Contest({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className="mx-auto w-full max-w-3xl">
      <ContestPage id={id} />
    </div>
  )
}
