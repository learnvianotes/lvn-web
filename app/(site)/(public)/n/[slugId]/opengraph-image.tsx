import logo from '@/branding/logo-paths.json'
import { ImageResponse } from 'next/og'
import { getPublicNote } from '@/features/public-notes/data'
import { parsePublicNoteSegment } from '@/features/public-notes/paths'

/** The picture shared links show (Open Graph): the note's title and author on paper, with the LVN mark and the highlighter stroke. */
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
      <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: 72, color: '#1c1b18', background: '#f8f7f4' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: 32, fontWeight: 600 }}>
          <svg width="56" height="56" viewBox="0 0 1024 1024">
            <rect width="1024" height="1024" rx={logo.tileRadius} fill={logo.colors.tile} />
            {logo.letters.map((d) => (
              <path key={d} d={d} fill={logo.colors.letter} />
            ))}
            <path d={logo.marker} fill={logo.colors.marker} />
          </svg>
          <span>LearnViaNotes</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <div style={{ display: 'flex', fontSize: title.length > 60 ? 56 : 68, fontWeight: 500, lineHeight: 1.08, letterSpacing: -1.5 }}>{title.slice(0, 120)}</div>
          <div style={{ display: 'flex', width: 220, height: 14, borderRadius: 7, background: '#f2c230' }} />
        </div>
        <div style={{ display: 'flex', fontSize: 28, color: '#66625b' }}>{note ? `by ${note.owner.displayName}` : 'Notes that help you learn'}</div>
      </div>
    ),
    size,
  )
}
