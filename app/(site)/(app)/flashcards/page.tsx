import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { FlashcardsPage } from '@/features/studio/FlashcardsPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('studio.cards'))('title'), robots: { index: false } }
}

export default function Flashcards() {
  return <FlashcardsPage />
}
