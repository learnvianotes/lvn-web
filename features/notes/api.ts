'use client'

import type { ApolloClient } from '@apollo/client'
import {
  NoteToEditDocument,
  type NoteToEditQuery,
  UpdateNoteDraftDocument,
  type CardFieldsFragment,
  type NoteMetaFragment,
} from '@/graphql/generated/graphql'
import type { SendSave } from './editor/autosave'
import type { StoredCard } from './model/doc'

export type NoteMeta = NoteMetaFragment

/** A note with all its cards (editors load the whole draft; at most 1,000 cards, 100 a page). */
export async function loadNote(client: ApolloClient, id: string): Promise<{ meta: NoteMeta; cards: StoredCard[] } | null> {
  const cards: CardFieldsFragment[] = []
  let after: string | null = null
  let meta: NoteMeta | null = null
  do {
    const res: { data?: NoteToEditQuery } = await client.query({ query: NoteToEditDocument, variables: { id, after }, fetchPolicy: 'network-only' })
    const note: NoteToEditQuery['note'] | undefined = res.data?.note
    if (!note) return null
    meta = note
    cards.push(...note.cards.edges.map((e) => e.node))
    after = note.cards.pageInfo.hasNextPage ? note.cards.pageInfo.endCursor : null
  } while (after)
  return { meta: meta!, cards: cards.map((c) => ({ id: c.id, type: c.type, position: c.position, revision: c.revision, content: c.content })) }
}

/** The autosave's transport: one updateNoteDraft. Network and server failures throw, so the save is retried. */
export const sendSave =
  (client: ApolloClient, onNote: (meta: NoteMeta) => void): SendSave =>
  async ({ noteId, title, ops }) => {
    const res = await client.mutate({ mutation: UpdateNoteDraftDocument, variables: { input: { noteId, ...(title !== undefined ? { title } : {}), ops } } })
    const payload = res.data?.updateNoteDraft
    if (!payload) throw new Error('no answer')
    if (payload.note) onNote(payload.note)
    return {
      results: payload.results.map((r) => ({ id: r.id, status: r.status, revision: r.revision })),
      conflictVersionId: payload.conflictVersion?.id ?? null,
      userErrors: payload.userErrors,
    }
  }
