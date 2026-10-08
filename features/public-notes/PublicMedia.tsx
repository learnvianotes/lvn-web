'use client'

import { useEffect, useState, type ReactNode } from 'react'
import { env } from '@/lib/env'
import { MediaMapProvider, type MediaInfo } from '@/features/notes/media'

/**
 * Media read URLs live 15 minutes, longer than a cached public page, so the browser asks for fresh ones after the page
 * loads (anonymously, as any visitor may read a public note). Pages without media cards skip the request.
 */
export function PublicMedia({ noteId, hasMedia, children }: { noteId: string; hasMedia: boolean; children: ReactNode }) {
  const [media, setMedia] = useState(() => new Map<string, MediaInfo>())
  const [loading, setLoading] = useState(hasMedia)
  useEffect(() => {
    if (!hasMedia) return
    const controller = new AbortController()
    void fetch(env.NEXT_PUBLIC_API_URL, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ query: 'query PublicNoteMedia($id: UUID!) { note(id: $id) { cards(first: 100) { edges { node { media { id url mimeType fileName sizeBytes } } } } } }', variables: { id: noteId } }),
      signal: controller.signal,
    })
      .then((r) => r.json() as Promise<{ data?: { note: { cards: { edges: { node: { media: (MediaInfo & { id: string }) | null } }[] } } | null } }>)
      .then((body) => {
        const found = (body.data?.note?.cards.edges ?? []).flatMap(({ node }) => (node.media ? [[node.media.id, node.media] as const] : []))
        setMedia(new Map(found))
      })
      .catch(() => undefined)
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [noteId, hasMedia])
  return (
    <MediaMapProvider media={media} loading={loading}>
      {children}
    </MediaMapProvider>
  )
}
