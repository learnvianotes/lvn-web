import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { NotePage } from '@/features/notes/NotePage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('notes'))('pageTitle'), robots: { index: false } }
}

export default async function NoteRoute({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return <NotePage id={id} />
}
