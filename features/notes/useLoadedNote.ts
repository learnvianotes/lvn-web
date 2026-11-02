'use client'

import { useApolloClient } from '@apollo/client/react'
import { useEffect, useState } from 'react'
import type { CardFieldsFragment } from '@/graphql/generated/graphql'
import { isNotThere } from '@/lib/query'
import { loadNote, sendSave, type NoteMeta } from './api'
import { readMirror, removeMirror, savedFromMirror } from './editor/mirror'
import { docToCards, type StoredCard } from './model/doc'
import { planSave } from './model/save'

export type LoadedNote =
  | { state: 'loading' }
  | { state: 'missing' }
  /** It could not be asked for (no connection, a server error) and this browser has no copy: the page offers a retry. */
  | { state: 'failed' }
  | { state: 'ready'; meta: NoteMeta; cards: StoredCard[]; media: CardFieldsFragment[]; mirror: Awaited<ReturnType<typeof readMirror>>; offline: boolean }

/**
 * A note to show or edit (the note page, the PDF reader). Edits a previous visit left in this browser (the IndexedDB
 * mirror) are sent first; when that is impossible (offline), the editor opens on them. `generation` reloads.
 */
export function useLoadedNote(id: string, userId: string | undefined, generation: number) {
  const client = useApolloClient()
  const [loaded, setLoaded] = useState<LoadedNote>({ state: 'loading' })

  useEffect(() => {
    if (!userId) return
    let cancelled = false
    void (async () => {
      setLoaded({ state: 'loading' })
      const mirror = await readMirror(userId, id)
      let offline = false
      // Kept when it could not be sent: the editor opens on it and its autosave tries again.
      let keep = false
      if (mirror) {
        const plan = planSave(savedFromMirror(mirror), mirror.title, docToCards(mirror.doc))
        try {
          const res = plan.ops.length || plan.title !== undefined ? await sendSave(client, () => {})({ noteId: id, ...(plan.title !== undefined ? { title: plan.title } : {}), ops: plan.ops }) : null
          if (res?.userErrors.length) keep = true
          else await removeMirror(userId, id)
        } catch {
          offline = true
          keep = true
        }
      }
      let note: Awaited<ReturnType<typeof loadNote>> = null
      let failure: unknown = null
      try {
        note = await loadNote(client, id)
      } catch (e) {
        offline = true
        failure = e
      }
      if (cancelled) return
      if (!note && mirror && offline) {
        // Offline with a local copy: open the editor on it; the autosave sends it when the connection is back.
        setLoaded({ state: 'ready', meta: mirrorMeta(id, mirror.title), cards: [], media: [], mirror, offline: true })
        return
      }
      // Not found only when the API said so (null, or not there for you); a failure to ask is not a missing note.
      if (!note) return setLoaded(failure && !isNotThere(failure) ? { state: 'failed' } : { state: 'missing' })
      setLoaded({ state: 'ready', meta: note.meta, cards: note.cards, media: note.media, mirror: keep ? mirror : null, offline })
    })()
    return () => {
      cancelled = true
    }
  }, [client, id, userId, generation])

  return [loaded, setLoaded] as const
}

/** What the page shows about a note while offline with only its local copy. */
function mirrorMeta(id: string, title: string): NoteMeta {
  return {
    id,
    title,
    slug: '',
    kind: 'NOTE',
    visibility: 'PRIVATE',
    viewerAccess: 'OWNER',
    viewerCan: { edit: true, publish: false, changeVisibility: false, delete: false, share: false, fork: false },
    owner: { id: '', displayName: '', handle: '' },
    folder: null,
    tags: [],
    topics: [],
    draftRevision: null,
    draftUpdatedAt: null,
    publishedAt: null,
    publishedVersion: null,
    allowForks: true,
    forkCount: 0,
    moderation: null,
    forkedFrom: null,
    cardCount: 0,
    deletedAt: null,
  }
}
