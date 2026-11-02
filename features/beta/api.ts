import type { ApolloClient } from '@apollo/client'
import { parse, type DocumentNode } from 'graphql'
import { ChangeNoteVisibilityDocument, CompleteNoteUploadDocument, CreateNoteUploadDocument, ForkNoteDocument, type Visibility } from '@/graphql/generated/graphql'
import { publicNotePath } from '@/features/public-notes/paths'
import type { NotePage } from '@/features/notes/pages/model'
import { pagesFromUnknown } from '@/features/notes/pages/model'
import { type ShareAudience, wireVisibility } from '@/features/notes/share/visibility'

/**
 * Beta operations against lvn-backend contracts 0.74.0 (PR #47, branch
 * cursor/sharing-quizzes-pages-voice-3455). Existing schema operations are the
 * generated documents. Fields that 0.74.0 adds and this repo's vendored schema
 * does not list yet are one document each, named as that contract names them.
 *
 * This agent cannot read the private lvn-backend repository, so the documents
 * below follow the operation names in that PR and this repo's payload style
 * (userErrors, UUID, relative paths). Shapes the PR summary did not spell out
 * are called out in GAPS.
 */
export const ASSUMPTIONS = [
  'setNoteVisibility calls changeNoteVisibility. Visibility is PRIVATE | SHARED | UNLISTED | PUBLIC. UNLISTED is its own value.',
  'Public is gated by the platform setting public_notes_require_verification, read as the query publicNotesRequireVerification.',
  'forkNote is the existing mutation. Opt-out is allowForks (forkingEnabled remains the fallback while a note payload still sends it). forkCount is the number of copies.',
  'sharedQuiz(noteId), sharedQuizByLink(token), myQuizzes, and publicQuizzes are the quiz reads. Attempts and the owner aggregate sit on the owned quiz.',
  'Quiz and note share paths are relative (/q/{token}, /n/{slug}-{id}). The web joins them to its origin.',
  'Note.pages returns pages with strokes and drawing side by side, plus image placements. Pictures are uploaded with createUploadIntent purpose PAGE_IMAGE.',
  'saveNotePages writes the page list, including drawing, so a round trip does not drop it.',
  'Voice notes upload with purpose VOICE_NOTE, then voiceCapture. transcribeCaptionClip takes the live captions, transcribeAudio the file, and makeNotesFromTranscript writes the notes.',
] as const

/**
 * Names this client still has to assume because PR #47's summary did not include
 * a field list. Replace them if the schema spells a different write.
 */
export const GAPS = [
  'Submit for a shared quiz is submitSharedQuizAttempt. The summary names the reads (sharedQuizByLink, attempts, aggregates) and not this write.',
  'Saving ink is saveNotePages. The summary names the Note.pages read (strokes beside drawing, PAGE_IMAGE placements) and not the write.',
  'publicNotesRequireVerification is the client read of the public_notes_require_verification setting. Admins already have adminSettings; a learner cannot use that query.',
  'voiceCapture, transcribeCaptionClip, transcribeAudio, and makeNotesFromTranscript inputs are { noteId, fileId?, captions? | transcript? } with userErrors. The summary names the operations, not the input fields.',
] as const

const PublicNotesRequireVerificationDocument = op(`
  query PublicNotesRequireVerification {
    publicNotesRequireVerification
  }
`)

const NoteForksDocument = op(`
  query NoteForks($id: UUID!) {
    note(id: $id) {
      allowForks
      forkCount
    }
  }
`)

const ShareQuizDocument = op(`
  mutation ShareQuiz($noteId: UUID!) {
    shareQuiz(input: { noteId: $noteId }) {
      quiz { id token path title }
      userErrors { message }
    }
  }
`)

const SharedQuizDocument = op(`
  query SharedQuiz($noteId: UUID!) {
    sharedQuiz(noteId: $noteId) {
      id
      token
      path
      title
      aggregate { attempts averageScore total }
      attempts { id score total submittedAt }
    }
  }
`)

const SharedQuizByLinkDocument = op(`
  query SharedQuizByLink($token: String!) {
    sharedQuizByLink(token: $token) {
      title
      ownerName
      questions { id prompt choices { id text } }
    }
  }
`)

const SubmitSharedQuizAttemptDocument = op(`
  mutation SubmitSharedQuizAttempt($token: String!, $answers: JSON!) {
    submitSharedQuizAttempt(input: { token: $token, answers: $answers }) {
      score
      total
      userErrors { message }
    }
  }
`)

const MyQuizzesDocument = op(`
  query MyQuizzes {
    myQuizzes { id title path token }
  }
`)

const PublicQuizzesDocument = op(`
  query PublicQuizzes {
    publicQuizzes { id title path token ownerName }
  }
`)

const NotePagesDocument = op(`
  query NotePages($noteId: UUID!) {
    note(id: $noteId) {
      pages {
        id
        strokes { id tool color width points { x y p } }
        drawing
        images { id fileId href name x y w h rotation }
      }
    }
  }
`)

const SaveNotePagesDocument = op(`
  mutation SaveNotePages($noteId: UUID!, $pages: JSON!) {
    saveNotePages(input: { noteId: $noteId, pages: $pages }) {
      userErrors { message }
    }
  }
`)

const CreatePageImageDocument = op(`
  mutation CreatePageImage($input: CreateUploadIntentInput!) {
    createUploadIntent(input: $input) {
      intent { fileId uploadUrl uploadHeaders { name value } }
      userErrors { message }
    }
  }
`)

const VoiceCaptureDocument = op(`
  mutation VoiceCapture($noteId: UUID!, $fileId: UUID!, $captions: String!) {
    voiceCapture(input: { noteId: $noteId, fileId: $fileId, captions: $captions }) {
      userErrors { message }
    }
  }
`)

const TranscribeCaptionClipDocument = op(`
  mutation TranscribeCaptionClip($noteId: UUID!, $captions: String!) {
    transcribeCaptionClip(input: { noteId: $noteId, captions: $captions }) {
      transcript
      userErrors { message }
    }
  }
`)

const TranscribeAudioDocument = op(`
  mutation TranscribeAudio($noteId: UUID!, $fileId: UUID!) {
    transcribeAudio(input: { noteId: $noteId, fileId: $fileId }) {
      transcript
      userErrors { message }
    }
  }
`)

const MakeNotesFromTranscriptDocument = op(`
  mutation MakeNotesFromTranscript($noteId: UUID!, $transcript: String!) {
    makeNotesFromTranscript(input: { noteId: $noteId, transcript: $transcript }) {
      markdown
      note { id }
      userErrors { message }
    }
  }
`)

export interface UserProblem {
  message: string
}

export interface QuizShareStats {
  attempts: number
  averageScore: number
  total: number
}

export interface QuizAttemptRow {
  id: string
  score: number
  total: number
  submittedAt: string
}

export interface OwnedQuiz {
  id: string
  token: string
  path: string
  title: string
  aggregate: QuizShareStats | null
  attempts: QuizAttemptRow[]
}

export interface QuizListItem {
  id: string
  title: string
  path: string
  token: string
  ownerName?: string | null
}

export interface SharedQuizChoice {
  id: string
  text: string
}

export interface SharedQuizQuestion {
  id: string
  prompt: string
  choices: SharedQuizChoice[]
}

export interface SharedQuiz {
  title: string
  ownerName: string
  questions: SharedQuizQuestion[]
}

export interface ForkState {
  allowForks: boolean
  forkCount: number
}

type Payload<T> = T & { userErrors?: UserProblem[] }

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
  return (res.data as { publicNotesRequireVerification?: boolean }).publicNotesRequireVerification === true
}

export async function forkNote(client: ApolloClient, noteId: string) {
  const res = await client.mutate({ mutation: ForkNoteDocument, variables: { noteId } })
  return res.data?.forkNote ?? null
}

export async function loadForkState(client: ApolloClient, noteId: string): Promise<ForkState | null> {
  const res = await client.query({ query: NoteForksDocument, variables: { id: noteId }, fetchPolicy: 'network-only' })
  const note = (res.data as { note?: { allowForks?: boolean; forkCount?: number } | null }).note
  if (!note || typeof note.allowForks !== 'boolean') return null
  return { allowForks: note.allowForks, forkCount: note.forkCount ?? 0 }
}

export async function shareQuiz(client: ApolloClient, noteId: string): Promise<Payload<{ quiz: { id: string; token: string; path: string; title: string } | null }>> {
  const res = await client.mutate({ mutation: ShareQuizDocument, variables: { noteId } })
  const payload = (res.data as { shareQuiz?: Payload<{ quiz: { id: string; token: string; path: string; title: string } | null }> } | null)?.shareQuiz
  if (!payload) throw new Error('no answer')
  return payload
}

export async function loadOwnedQuiz(client: ApolloClient, noteId: string): Promise<OwnedQuiz | null> {
  const res = await client.query({ query: SharedQuizDocument, variables: { noteId }, fetchPolicy: 'network-only' })
  return (res.data as { sharedQuiz?: OwnedQuiz | null }).sharedQuiz ?? null
}

export async function loadMyQuizzes(client: ApolloClient): Promise<QuizListItem[]> {
  const res = await client.query({ query: MyQuizzesDocument, fetchPolicy: 'network-only' })
  return (res.data as { myQuizzes?: QuizListItem[] }).myQuizzes ?? []
}

export async function loadPublicQuizzes(client: ApolloClient): Promise<QuizListItem[]> {
  const res = await client.query({ query: PublicQuizzesDocument, fetchPolicy: 'network-only' })
  return (res.data as { publicQuizzes?: QuizListItem[] }).publicQuizzes ?? []
}

export async function loadSharedQuiz(client: ApolloClient, token: string): Promise<SharedQuiz | null> {
  const res = await client.query({ query: SharedQuizByLinkDocument, variables: { token }, fetchPolicy: 'network-only' })
  return (res.data as { sharedQuizByLink?: SharedQuiz | null }).sharedQuizByLink ?? null
}

export async function submitSharedQuiz(client: ApolloClient, token: string, answers: { questionId: string; choiceId: string }[]) {
  const res = await client.mutate({ mutation: SubmitSharedQuizAttemptDocument, variables: { token, answers } })
  const payload = (res.data as { submitSharedQuizAttempt?: Payload<{ score: number | null; total: number | null }> } | null)?.submitSharedQuizAttempt
  if (!payload) throw new Error('no answer')
  return payload
}

export async function notePages(client: ApolloClient, noteId: string): Promise<NotePage[]> {
  const res = await client.query({ query: NotePagesDocument, variables: { noteId }, fetchPolicy: 'network-only' })
  const raw = (res.data as { note?: { pages?: unknown } | null }).note?.pages
  return pagesFromUnknown(raw) ?? []
}

export async function saveNotePages(client: ApolloClient, noteId: string, pages: NotePage[]) {
  const res = await client.mutate({ mutation: SaveNotePagesDocument, variables: { noteId, pages } })
  const payload = (res.data as { saveNotePages?: { userErrors?: UserProblem[] } } | null)?.saveNotePages
  if (!payload) throw new Error('no answer')
  return payload
}

/** A picture on a page. purpose PAGE_IMAGE is not on the vendored FilePurpose enum yet. */
export async function createPageImage(client: ApolloClient, noteId: string, file: File) {
  const res = await client.mutate({
    mutation: CreatePageImageDocument,
    variables: { input: { fileName: file.name || 'page.png', mimeType: file.type || 'image/png', sizeBytes: file.size, purpose: 'PAGE_IMAGE', parentId: noteId } },
  })
  const payload = (res.data as { createUploadIntent?: Payload<{ intent: { fileId: string; uploadUrl: string; uploadHeaders: { name: string; value: string }[] } | null }> } | null)?.createUploadIntent
  if (!payload?.intent) throw new Error(payload?.userErrors?.[0]?.message ?? 'upload refused')
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

/** Keeps the recording as a VOICE_NOTE, then registers it with voiceCapture. */
export async function uploadVoiceNote(client: ApolloClient, noteId: string, file: File, captions: string) {
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
  const captured = await client.mutate({ mutation: VoiceCaptureDocument, variables: { noteId, fileId: intent.fileId, captions } })
  const captureProblem = (captured.data as { voiceCapture?: { userErrors?: UserProblem[] } } | null)?.voiceCapture?.userErrors?.[0]?.message
  if (captureProblem) throw new Error(captureProblem)
  return intent.fileId
}

export async function transcribeCaptionClip(client: ApolloClient, noteId: string, captions: string) {
  const res = await client.mutate({ mutation: TranscribeCaptionClipDocument, variables: { noteId, captions } })
  const payload = (res.data as { transcribeCaptionClip?: Payload<{ transcript: string | null }> } | null)?.transcribeCaptionClip
  if (!payload) throw new Error('no answer')
  return payload
}

export async function transcribeAudio(client: ApolloClient, noteId: string, fileId: string) {
  const res = await client.mutate({ mutation: TranscribeAudioDocument, variables: { noteId, fileId } })
  const payload = (res.data as { transcribeAudio?: Payload<{ transcript: string | null }> } | null)?.transcribeAudio
  if (!payload) throw new Error('no answer')
  return payload
}

export async function makeNotesFromTranscript(client: ApolloClient, noteId: string, transcript: string) {
  const res = await client.mutate({ mutation: MakeNotesFromTranscriptDocument, variables: { noteId, transcript } })
  const payload = (res.data as { makeNotesFromTranscript?: Payload<{ markdown: string | null; note: { id: string } | null }> } | null)?.makeNotesFromTranscript
  if (!payload) throw new Error('no answer')
  return payload
}

function op(source: string): DocumentNode {
  return parse(source)
}

function putFile(intent: { uploadUrl: string; uploadHeaders: { name: string; value: string }[] }, file: Blob): Promise<void> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', intent.uploadUrl)
    for (const header of intent.uploadHeaders) if (header.name.toLowerCase() !== 'content-length') xhr.setRequestHeader(header.name, header.value)
    xhr.onload = () => (xhr.status >= 200 && xhr.status < 300 ? resolve() : reject(new Error(`upload ${xhr.status}`)))
    xhr.onerror = () => reject(new Error('upload failed'))
    xhr.send(file)
  })
}
