import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AskPage } from '@/features/ai/AskAi'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('ai.ask'))('title'), robots: { index: false } }
}

export default function Ask() {
  return <AskPage />
}
