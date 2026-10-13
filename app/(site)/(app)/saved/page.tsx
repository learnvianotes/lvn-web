import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { SavedPage } from '@/features/saved/SavedPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('saved'))('title'), robots: { index: false } }
}

/** Bookmarks: saved notes and resources (lvn-backend ADR-0076). */
export default function Saved() {
  return <SavedPage />
}
