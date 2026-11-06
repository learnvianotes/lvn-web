import type { ApolloClient } from '@apollo/client'
import {
  ChangeNoteVisibilityDocument,
  CompleteNoteUploadDocument,
  CreateNoteUploadDocument,
  ForkNoteDocument,
  NoteForksDocument,
  PublicNotesRequireVerificationDocument,
  type Visibility,
} from '@/graphql/generated/graphql'
import { publicNotePath } from '@/features/public-notes/paths'
import { type ShareAudience, wireVisibility } from '@/features/notes/share/visibility'
import { env } from '@/lib/env'
import { STORAGE_PUT_REFUSED, storagePutRequest } from '@/lib/upload-target'

/**
 * Helpers around the generated beta operations (graphql/operations/beta.graphql).
 * Sharing a quiz is createSharedQuiz, not shareQuiz. voiceCapture is a query that
 * describes the browser speech API. Page ink is saveNotePages with SaveNotePageInput.
 */
export const ASSUMPTIONS = [
  'setNoteVisibility calls changeNoteVisibility. Visibility is PRIVATE | SHARED | UNLISTED | PUBLIC.',
  'Public is gated by publicNotesRequireVerification.',
  'forkNote is the existing mutation. Opt-out is Note.allowForks. forkCount is the number of copies. The boolean query is forkingEnabled(noteId).',
  'A shared quiz is createSharedQuiz, then sharedQuiz(id) for sharePath, owner, myAttempts and stats. The take link is sharedQuizByLink(token). Lists are myQuizzes and publicQuizzes.',
  'submitSharedQuizAttempt takes quizId, clientOpId and answers of questionId plus choiceIds.',
  'Quiz and note share paths are relative (/q/{linkToken} inside sharePath, /n/{slug}-{id}). The web joins them to its origin.',
  'Note.pages returns strokes (points are x and y) and images. Pictures upload with createUploadIntent purpose PAGE_IMAGE.',
  'saveNotePages takes noteId and pages of drawing, index and images.',
  'Voice notes upload with purpose VOICE_NOTE. voiceCapture is a query. transcribeCaptionClip and transcribeAudio return transcript { text cut }. makeNotesFromTranscript returns notes { noteId title summary }.',
] as const

/**
 * What the schema does not offer, so the UI does not pretend those fields exist.
 */
export const GAPS = [
  'There is no shareQuiz and createSharedQuiz has no noteId. The share control sends the note’s quiz-card JSON. The quiz is not stored on the note.',
  'SharedQuiz has sharePath, not token or path. sharePath is null while the quiz is private, and for a public quiz it is owner-only, so other people open /q/{id}.',
  'stats.averageScore is a fraction of the questions. The attempt count is scoredAttempts. There is no aggregate.total.',
  'Questions are rich text (question, choice content), not prompt and text.',
  'voiceCapture does not store audio or captions. A recording is a VOICE_NOTE upload. Captions go to the transcribe mutations.',
  'makeNotesFromTranscript returns notes.title and notes.summary, not markdown.',
  'StrokePoint is x and y. Pressure is used while drawing and is not sent.',
] as const

export interface UserProblem {
  message: string
}

export interface QuizShareStats {
  attempts: number
  averageScore: number
  total: number
}

export interface ForkState {
  allowForks: boolean
  forkCount: number
}

export function absoluteUrl(pathOrUrl: string, origin: string): string {
  if (pathOrUrl.startsWith('http://') || pathOrUrl.startsWith('https://')) return pathOrUrl
  const path = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`
  return `${origin}${path}`
}

/** Relative share path. Unlisted and public notes are /n/{slug}-{id}. */
export function noteSharePath(note: { id: string; slug?: string | null; visibility: string }): string {
  if (note.visibility === 'PUBLIC' || note.visibility === 'UNLISTED') return publicNotePath(note)
  return `/notes/${note.id}`
}

/** Owner links are sharePath. This is only the fallback when a token is all we have. */
export function quizPath(token: string, serverPath?: string | null): string {
  if (serverPath && serverPath.startsWith('/')) return serverPath
  return `/q/${token}`
}

export async function setNoteVisibility(client: ApolloClient, noteId: string, audience: ShareAudience) {
  const res = await client.mutate({ mutation: ChangeNoteVisibilityDocument, variables: { noteId, visibility: wireVisibility(audience) as Visibility } })
  return res.data?.changeNoteVisibility ?? null
}

export async function publicNotesRequireVerification(client: ApolloClient): Promise<boolean> {
  const res = await client.query({ query: PublicNotesRequireVerificationDocument, fetchPolicy: 'network-only' })
  return res.data?.publicNotesRequireVerification === true
}

export async function forkNote(client: ApolloClient, noteId: string) {
  const res = await client.mutate({ mutation: ForkNoteDocument, variables: { noteId } })
  return res.data?.forkNote ?? null
}

export async function loadForkState(client: ApolloClient, noteId: string): Promise<ForkState | null> {
  const res = await client.query({ query: NoteForksDocument, variables: { id: noteId }, fetchPolicy: 'network-only' })
  const data = res.data
  if (!data) return null
  const allow = data.forkingEnabled
  if (typeof allow !== 'boolean') return null
  return { allowForks: data.note?.allowForks ?? allow, forkCount: data.note?.forkCount ?? 0 }
}

/** A picture on a page. purpose PAGE_IMAGE, then completeUpload. */
export async function createPageImage(client: ApolloClient, noteId: string, file: File) {
  const res = await client.mutate({
    mutation: CreateNoteUploadDocument,
    variables: { input: { fileName: file.name || 'page.png', mimeType: file.type || 'image/png', sizeBytes: file.size, purpose: 'PAGE_IMAGE', parentId: noteId } },
  })
  const payload = res.data?.createUploadIntent
  if (!payload?.intent) throw new Error(payload?.userErrors[0]?.message ?? 'upload refused')
  return payload.intent
}

/** PUT the picture, then complete the upload. The placement keeps its preview if this fails. */
export async function uploadPageImage(client: ApolloClient, noteId: string, file: File): Promise<string> {
  const intent = await createPageImage(client, noteId, file)
  await putFile(intent, file)
  const done = await completeUpload(client, intent.fileId)
  if (!done?.ok) throw new Error(done?.userErrors[0]?.message ?? 'upload not accepted')
  return intent.fileId
}

export async function completeUpload(client: ApolloClient, fileId: string) {
  const res = await client.mutate({ mutation: CompleteNoteUploadDocument, variables: { fileId } })
  return res.data?.completeUpload ?? null
}

/** Stores the recording as a VOICE_NOTE. voiceCapture does not register it. */
export async function uploadVoiceNote(client: ApolloClient, noteId: string, file: File) {
  const res = await client.mutate({
    mutation: CreateNoteUploadDocument,
    variables: { input: { fileName: file.name || 'voice.webm', mimeType: file.type || 'audio/webm', sizeBytes: file.size, purpose: 'VOICE_NOTE', parentId: noteId } },
  })
  const intent = res.data?.createUploadIntent.intent
  const problem = res.data?.createUploadIntent.userErrors[0]?.message
  if (!intent) throw new Error(problem ?? 'upload refused')
  await putFile(intent, file)
  const done = await completeUpload(client, intent.fileId)
  if (!done?.ok) throw new Error(done?.userErrors[0]?.message ?? 'upload not accepted')
  return intent.fileId
}

function putFile(intent: { uploadUrl: string; uploadHeaders: { name: string; value: string }[] }, file: Blob): Promise<void> {
  const target = storagePutRequest(intent, { appEnv: env.NEXT_PUBLIC_APP_ENV, storageOrigins: env.NEXT_PUBLIC_STORAGE_ORIGINS })
  if (!target) return Promise.reject(new Error(STORAGE_PUT_REFUSED))
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', target.url)
    for (const header of target.headers) xhr.setRequestHeader(header.name, header.value)
    xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`upload ${xhr.status}`)))
    xhr.onerror = () => reject(new Error('upload failed'))
    xhr.send(file)
  })
}
