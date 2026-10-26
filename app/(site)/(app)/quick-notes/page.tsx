import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { QuickNotesPage } from '@/features/studio/QuickNotesPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('studio.quick'))('title'), robots: { index: false } }
}

export default function QuickNotes() {
  return <QuickNotesPage />
}
