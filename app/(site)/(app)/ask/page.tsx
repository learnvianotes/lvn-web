import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AskPage } from '@/features/ai/AskAi'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('ai.ask'))('title'), robots: { index: false } }
}

export default async function Ask({ searchParams }: { searchParams: Promise<{ q?: string | string[] }> }) {
  const { q } = await searchParams
  return <AskPage question={typeof q === 'string' ? q.slice(0, 500) : undefined} />
}
