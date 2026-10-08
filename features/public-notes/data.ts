import 'server-only'
import { cache } from 'react'
import type { CardType } from '@/lib/contracts/domain/enums'
import { serverEnv } from '@/lib/server-env'

/**
 * What public pages read from the API on the server, cached by Next.js for an hour and dropped earlier when the API
 * says a note changed (tags `note:<id>` and `public-notes`, app/api/revalidate). Anonymous: only notes anyone may read.
 */

export const PAGE_REVALIDATE_SECONDS = 3600

export interface PublicNote {
  id: string
  title: string
  slug: string
  kind: string
  publishedAt: string | null
  owner: { displayName: string; handle: string }
  topics: { id: string; title: string; subject: { title: string } }[]
  forkedFrom: { title: string | null; author: { displayName: string } } | null
  cards: { id: string; type: CardType; content: unknown; hasMedia: boolean }[]
}

async function query<T>(source: string, variables: Record<string, unknown>, tags: string[]): Promise<T> {
  const res = await fetch(serverEnv.apiUrl, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: source, variables }),
    next: { revalidate: PAGE_REVALIDATE_SECONDS, tags },
  })
  if (!res.ok) throw new Error(`API answered HTTP ${res.status}`)
  const body = (await res.json()) as { data?: T; errors?: { message: string }[] }
  if (body.errors?.length || !body.data) throw new Error(`API error: ${body.errors?.[0]?.message ?? 'no data'}`)
  return body.data
}

const NOTE = `query PublicNote($id: UUID!, $after: String) {
  note(id: $id) {
    id title slug kind publishedAt
    owner { displayName handle }
    topics { id title subject { title } }
    forkedFrom { title author { displayName } }
    cards(first: 100, after: $after) { edges { node { id type content media { id } } } pageInfo { hasNextPage endCursor } }
  }
}`

type NoteAnswer = {
  note:
    | (Omit<PublicNote, 'cards'> & {
        cards: { edges: { node: { id: string; type: CardType; content: unknown; media: { id: string } | null } }[]; pageInfo: { hasNextPage: boolean; endCursor: string | null } }
      })
    | null
}

/** A note anyone may read, with all its cards (the published version); null when there is none. */
export const getPublicNote = cache(async (id: string): Promise<PublicNote | null> => {
  const cards: PublicNote['cards'] = []
  let after: string | null = null
  let first: NoteAnswer['note'] = null
  do {
    const data: NoteAnswer = await query<NoteAnswer>(NOTE, { id, after }, [`note:${id}`])
    if (!data.note) return null
    first ??= data.note
    cards.push(...data.note.cards.edges.map(({ node }) => ({ id: node.id, type: node.type, content: node.content, hasMedia: !!node.media })))
    after = data.note.cards.pageInfo.hasNextPage ? data.note.cards.pageInfo.endCursor : null
  } while (after)
  const { cards: _paged, ...note } = first!
  return { ...note, cards }
})

const LIST = `query PublicNotes($after: String) {
  publicNotes(first: 100, after: $after) { edges { node { id slug publishedAt } } pageInfo { hasNextPage endCursor } }
}`

type ListAnswer = { publicNotes: { edges: { node: { id: string; slug: string; publishedAt: string | null } }[]; pageInfo: { hasNextPage: boolean; endCursor: string | null } } }

/** Public notes for the sitemap, newest first. */
export async function listPublicNotes(limit = 5_000) {
  const out: ListAnswer['publicNotes']['edges'][number]['node'][] = []
  let after: string | null = null
  do {
    const data: ListAnswer = await query<ListAnswer>(LIST, { after }, ['public-notes'])
    out.push(...data.publicNotes.edges.map((e) => e.node))
    after = data.publicNotes.pageInfo.hasNextPage ? data.publicNotes.pageInfo.endCursor : null
  } while (after && out.length < limit)
  return out.slice(0, limit)
}
