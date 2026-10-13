import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { EditResource } from '@/features/resources/EditResource'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('resources.form'))('editTitle'), robots: { index: false } }
}

/** Editing one's own resource before it is approved, or sending a rejected one again (lvn-backend ADR-0074). */
export default async function EditResourcePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <EditResource id={id} />
    </div>
  )
}
