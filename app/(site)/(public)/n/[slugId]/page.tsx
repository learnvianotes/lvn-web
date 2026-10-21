import type { Metadata } from 'next'
import { notFound, permanentRedirect } from 'next/navigation'
import { cardPlainText } from '@/lib/contracts/validation'
import { env } from '@/lib/env'
import { getPublicNote } from '@/features/public-notes/data'
import { parsePublicNoteSegment, publicNotePath } from '@/features/public-notes/paths'
import { PublicNoteView } from '@/features/public-notes/PublicNoteView'
import { templated } from '@/lib/page-title'

/**
 * A public note (P2d): rendered on the server the first time it is asked for, then served from the cache; the API asks
 * for a fresh render when the note changes (app/api/revalidate), and every page refreshes within an hour anyway.
 */
// A literal: Next reads segment config without running the module (an hour, as data.ts caches the API).
export const revalidate = 3600

/** No note is built ahead of time; each is rendered on its first visit and cached (ISR). */
export function generateStaticParams() {
  return []
}

type Props = { params: Promise<{ slugId: string }> }

async function load(segment: string) {
  const parsed = parsePublicNoteSegment(segment)
  return parsed ? { parsed, note: await getPublicNote(parsed.id) } : null
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const found = await load((await params).slugId)
  if (!found?.note) return { title: 'Note not found', robots: { index: false } }
  const { note } = found
  const description = note.cards.map((c) => cardPlainText(c.type, c.content)).join(' ').replace(/\s+/g, ' ').trim().slice(0, 160)
  const url = `${env.NEXT_PUBLIC_SITE_URL}${publicNotePath(note)}`
  return {
    title: templated(note.title || 'Untitled note'),
    description,
    alternates: { canonical: url },
    authors: [{ name: note.owner.displayName }],
    openGraph: { type: 'article', url, title: note.title, description, siteName: 'LearnViaNotes', authors: [note.owner.displayName], ...(note.publishedAt ? { publishedTime: note.publishedAt } : {}) },
    twitter: { card: 'summary_large_image', title: note.title, description },
  }
}

export default async function PublicNotePage({ params }: Props) {
  const found = await load((await params).slugId)
  if (!found?.note) notFound()
  // One address per note: an old or missing slug moves to the current one.
  if (found.parsed.slug !== (found.note.slug || 'note')) permanentRedirect(publicNotePath(found.note))
  return <PublicNoteView note={found.note} />
}
