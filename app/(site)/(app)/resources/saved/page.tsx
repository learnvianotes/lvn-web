import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { SavedResources } from '@/features/resources/SavedResources'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('resources.savedList'))('title'), robots: { index: false } }
}

/** The viewer's Saved resources (lvn-backend ADR-0075). */
export default function SavedResourcesPage() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6">
      <SavedResources />
    </div>
  )
}
