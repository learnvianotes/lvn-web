/** Public note URLs (P2d): `/n/<slug>-<id>`; the id decides, the slug is for people and search engines. */
const UUID = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'

export const publicNotePath = (note: { id: string; slug?: string | null }) => `/n/${note.slug || 'note'}-${note.id}`

/** The id and slug of a `/n/…` segment, or null when it holds no note id. */
export function parsePublicNoteSegment(segment: string): { id: string; slug: string } | null {
  const m = new RegExp(`^(?:(.*)-)?(${UUID})$`, 'i').exec(decodeURIComponent(segment))
  return m ? { slug: m[1] ?? '', id: m[2]!.toLowerCase() } : null
}
