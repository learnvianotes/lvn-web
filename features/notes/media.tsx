'use client'

import type { ApolloClient } from '@apollo/client'
import { useApolloClient } from '@apollo/client/react'
import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react'
import { CompleteNoteUploadDocument, CreateNoteUploadDocument, type CardFieldsFragment, type MediaFieldsFragment } from '@/graphql/generated/graphql'
import type { CardType } from '@/lib/contracts/domain/enums'

/**
 * Pictures, video, audio and files on notes (lvn-backend §8.1): uploads go straight to storage with a pre-signed PUT,
 * then the API checks them; media cards hold only the file id, and the note's cards come with short-lived read URLs
 * (Card.media). This module keeps those URLs for the page, uploads files, and says what each media card accepts.
 */

export type MediaCardType = Extract<CardType, 'image' | 'video' | 'audio' | 'file'>
export const MEDIA_TYPES: MediaCardType[] = ['image', 'video', 'audio', 'file']
export const isMediaType = (type: string): type is MediaCardType => (MEDIA_TYPES as string[]).includes(type)

/** What the API accepts for notes, by card type (a file card takes any of them). */
const ACCEPT: Record<Exclude<MediaCardType, 'file'>, string[]> = {
  image: ['image/jpeg', 'image/png', 'image/webp', 'image/gif'],
  video: ['video/mp4', 'video/webm', 'video/quicktime'],
  audio: ['audio/mpeg', 'audio/mp4', 'audio/ogg', 'audio/wav', 'audio/webm'],
}
const ALL = [...ACCEPT.image, ...ACCEPT.video, ...ACCEPT.audio, 'application/pdf']
export const acceptFor = (type: MediaCardType) => (type === 'file' ? ALL : ACCEPT[type]).join(',')

/** Browsers leave some types empty or use other names; the API wants these. */
const BY_EXTENSION: Record<string, string> = { mov: 'video/quicktime', m4a: 'audio/mp4', mp3: 'audio/mpeg', wav: 'audio/wav', oga: 'audio/ogg', ogg: 'audio/ogg', pdf: 'application/pdf', jpg: 'image/jpeg', jpeg: 'image/jpeg', png: 'image/png', webp: 'image/webp', gif: 'image/gif', mp4: 'video/mp4', webm: 'video/webm' }
export function mimeOf(file: File): string {
  const type = file.type === 'audio/x-m4a' ? 'audio/mp4' : file.type === 'audio/wave' || file.type === 'audio/x-wav' ? 'audio/wav' : file.type
  return ALL.includes(type) ? type : (BY_EXTENSION[file.name.split('.').pop()?.toLowerCase() ?? ''] ?? type)
}

/** The card a dropped or pasted file becomes, or null when notes do not take it. */
export function cardTypeFor(file: File): MediaCardType | null {
  const mime = mimeOf(file)
  if (ACCEPT.image.includes(mime)) return 'image'
  if (ACCEPT.video.includes(mime)) return 'video'
  if (ACCEPT.audio.includes(mime)) return 'audio'
  return mime === 'application/pdf' ? 'file' : null
}

export interface MediaInfo {
  url: string
  mimeType: string
  fileName: string
  sizeBytes: number
}

export class UploadError extends Error {}

/** Uploads a file to a note and returns its id once the API has checked it. Progress is 0–1. */
export async function uploadToNote(client: ApolloClient, noteId: string, file: File, onProgress: (p: number) => void): Promise<string> {
  const res = await client.mutate({ mutation: CreateNoteUploadDocument, variables: { input: { fileName: file.name || 'file', mimeType: mimeOf(file), sizeBytes: file.size, purpose: 'ATTACHMENT', parentId: noteId } } })
  const intent = res.data?.createUploadIntent.intent
  if (!intent) throw new UploadError(res.data?.createUploadIntent.userErrors[0]?.message ?? 'upload refused')
  await new Promise<void>((resolve, reject) => {
    // XMLHttpRequest, not fetch: it reports upload progress.
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', intent.uploadUrl)
    // Browsers set Content-Length themselves and refuse to have it set.
    for (const h of intent.uploadHeaders) if (h.name.toLowerCase() !== 'content-length') xhr.setRequestHeader(h.name, h.value)
    xhr.upload.onprogress = (e) => e.lengthComputable && onProgress(e.loaded / e.total)
    xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new UploadError(`storage answered ${xhr.status}`)))
    xhr.onerror = () => reject(new UploadError('network'))
    xhr.send(file)
  })
  const done = await client.mutate({ mutation: CompleteNoteUploadDocument, variables: { fileId: intent.fileId } })
  if (!done.data?.completeUpload.ok) throw new UploadError(done.data?.completeUpload.userErrors[0]?.message ?? 'upload not accepted')
  return intent.fileId
}

/** Read URLs by file id, from the loaded cards. */
export function mediaOf(cards: { media?: MediaFieldsFragment | null }[]): Map<string, MediaInfo> {
  return new Map(cards.flatMap((c) => (c.media ? [[c.media.id, { url: c.media.url, mimeType: c.media.mimeType, fileName: c.media.fileName, sizeBytes: c.media.sizeBytes }] as const] : [])))
}

interface MediaStore {
  noteId: string | null
  /** Read URLs are still on their way (public pages ask for them after loading) */
  loading?: boolean
  get: (fileId: string | undefined | null) => MediaInfo | undefined
  /** Uploads a file to the note; the card can show it right away from this device. */
  upload: (file: File, onProgress: (p: number) => void) => Promise<string>
}

const MediaContext = createContext<MediaStore>({ noteId: null, get: () => undefined, upload: () => Promise.reject(new UploadError('no note')) })
export const useMedia = () => useContext(MediaContext)

/** Read URLs only, for pages without the signed-in app around them (public note pages). */
export function MediaMapProvider({ media, loading = false, children }: { media: Map<string, MediaInfo>; loading?: boolean; children: ReactNode }) {
  const store = useMemo<MediaStore>(() => ({ noteId: null, loading, get: (fileId) => (fileId ? media.get(fileId) : undefined), upload: () => Promise.reject(new UploadError('read only')) }), [media, loading])
  return <MediaContext.Provider value={store}>{children}</MediaContext.Provider>
}

/** Files dropped or pasted into the editor, waiting for the media card made for them to upload them. */
export const pendingFiles = new Map<string, File>()

export function MediaProvider({ noteId, cards, children }: { noteId: string | null; cards: CardFieldsFragment[] | { media?: MediaFieldsFragment | null }[]; children: ReactNode }) {
  const client = useApolloClient()
  const loaded = useMemo(() => mediaOf(cards), [cards])
  const local = useRef(new Map<string, MediaInfo>())
  const [, rerender] = useState(0)
  const get = useCallback((fileId: string | undefined | null) => (fileId ? (local.current.get(fileId) ?? loaded.get(fileId)) : undefined), [loaded])
  const upload = useCallback(
    async (file: File, onProgress: (p: number) => void) => {
      if (!noteId) throw new UploadError('no note')
      const fileId = await uploadToNote(client, noteId, file, onProgress)
      local.current.set(fileId, { url: URL.createObjectURL(file), mimeType: mimeOf(file), fileName: file.name, sizeBytes: file.size })
      rerender((n) => n + 1)
      return fileId
    },
    [client, noteId],
  )
  const store = useMemo(() => ({ noteId, get, upload }), [noteId, get, upload])
  return <MediaContext.Provider value={store}>{children}</MediaContext.Provider>
}

export function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`
  if (n < 1024 ** 2) return `${Math.round(n / 1024)} KB`
  return `${(n / 1024 ** 2).toFixed(n < 10 * 1024 ** 2 ? 1 : 0)} MB`
}
