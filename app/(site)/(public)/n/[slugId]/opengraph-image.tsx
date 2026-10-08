import { ImageResponse } from 'next/og'
import { getPublicNote } from '@/features/public-notes/data'
import { parsePublicNoteSegment } from '@/features/public-notes/paths'

/** The picture shared links show (Open Graph): the note's title and author on the night sky of the brand. */
export const size = { width: 1200, height: 630 }
export const contentType = 'image/png'
export const alt = 'A note on LearnViaNotes'
// A literal: Next reads segment config without running the module (an hour, as data.ts caches the API).
export const revalidate = 3600

export default async function Image({ params }: { params: Promise<{ slugId: string }> }) {
  const parsed = parsePublicNoteSegment((await params).slugId)
  const note = parsed ? await getPublicNote(parsed.id) : null
  const title = note?.title || 'A note on LearnViaNotes'
  return new ImageResponse(
    (
      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: 72, color: 'white', background: 'radial-gradient(circle at 80% 10%, #6366F1 0%, transparent 45%), linear-gradient(160deg, #1C1A3A 0%, #312E81 100%)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: 34, fontWeight: 700 }}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: 'linear-gradient(135deg, #818CF8, #4F46E5)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30 }}>📘</div>
          <span>
            LearnVia<span style={{ color: '#A5B4FC' }}>Notes</span>
          </span>
        </div>
        <div style={{ display: 'flex', fontSize: title.length > 60 ? 56 : 72, fontWeight: 800, lineHeight: 1.1, letterSpacing: -1.5 }}>{title.slice(0, 120)}</div>
        <div style={{ display: 'flex', fontSize: 30, color: '#C7D2FE' }}>{note ? `by ${note.owner.displayName}` : 'Notes that help you learn'}</div>
      </div>
    ),
    size,
  )
}
