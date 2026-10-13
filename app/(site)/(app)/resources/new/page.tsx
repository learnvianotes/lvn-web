import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ResourceForm } from '@/features/resources/ResourceForm'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('resources.form'))('title'), robots: { index: false } }
}

/** Adding a resource to the catalogue (lvn-backend ADR-0074). */
export default function NewResourcePage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <ResourceForm />
    </div>
  )
}
