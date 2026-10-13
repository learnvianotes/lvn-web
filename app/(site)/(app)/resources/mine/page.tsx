import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { MyResources } from '@/features/resources/MyResources'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('resources'))('title'), robots: { index: false } }
}

/** The resources a person sent, with their state (lvn-backend ADR-0074). */
export default function MyResourcesPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <MyResources />
    </div>
  )
}
