import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ReaderPage } from '@/features/reader/ReaderPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('reader'))('title'), robots: { index: false } }
}

/** A PDF of a note in the reader, beside the note (lvn-backend ADR-0040). */
export default async function ReaderRoute({ params }: { params: Promise<{ id: string; fileId: string }> }) {
  const { id, fileId } = await params
  return <ReaderPage noteId={id} fileId={fileId} />
}
