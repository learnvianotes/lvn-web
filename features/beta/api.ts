import type { ApolloClient } from '@apollo/client'
import { parse, type DocumentNode } from 'graphql'
import { ChangeNoteVisibilityDocument, ForkNoteDocument } from '@/graphql/generated/graphql'
import type { NotePage } from '@/features/notes/pages/model'
import { pagesFromUnknown } from '@/features/notes/pages/model'
import { type ShareAudience, wireVisibility } from '@/features/notes/share/visibility'

/**
 * Beta operations for the notes editor, sharing, quizzes and voice notes.
 * Existing GraphQL is used when the contract is already in the schema.
 * New operations are one document each, named the way the backend agent is adding them.
 *
 * Assumptions (the parallel lvn-backend work is not in this repo yet):
 * - setNoteVisibility is the client name. The wire mutation is still changeNoteVisibility.
 *   Unlisted links are stored as SHARED until a UNLISTED enum value exists. Anyone with
 *   the note link can read a SHARED note; it is not listed on public pages. PUBLIC stays
 *   the listed audience. Person-shares still use shareNote.
 * - forkNote is the existing forkNote mutation. The author's opt-out is forkingEnabled
 *   via setNoteForking. When it is false the client hides Fork for everyone but the owner.
 * - shareQuiz(input: { noteId }) returns { share: { token, url }, stats: { attempts, averageScore, total }, userErrors }.
 *   The take page reads sharedQuiz(token) and submits submitSharedQuiz. Taking a quiz
 *   does not require the classroom the note was written in.
 * - notePages(noteId) returns { pages }, JSON of NotePage[]. saveNotePages writes that JSON.
 * - transcribeVoiceNote(input: { noteId, captions }) returns { transcript, userErrors }.
 *   captions are the live Web Speech line; the recording itself stays on the note as audio.
 * - notesFromTranscript(input: { noteId, transcript }) returns { markdown, note { id }, userErrors }.
 */
export const ASSUMPTIONS = [
  'setNoteVisibility calls changeNoteVisibility. UNLISTED is stored as SHARED (link, not listed).',
  'forkNote is the existing forkNote mutation. Opt-out is forkingEnabled; the client hides Fork when it is off.',
  'shareQuiz returns { share: { token, url }, stats: { attempts, averageScore, total }, userErrors }.',
  'sharedQuiz(token) returns the questions without answers. submitSharedQuiz returns { score, total, userErrors }.',
  'notePages(noteId) returns { pages } JSON. saveNotePages(input: { noteId, pages }) writes it.',
  'transcribeVoiceNote accepts the live captions and returns { transcript }. The recording is kept separately.',
  'notesFromTranscript returns { markdown, note { id } } for Make notes from this.',
] as const

const ShareQuizDocument = op(`
  mutation ShareQuiz($noteId: UUID!) {
    shareQuiz(input: { noteId: $noteId }) {
      share { token url }
      stats { attempts averageScore total }
      userErrors { message }
    }
  }
`)

const SharedQuizDocument = op(`
  query SharedQuiz($token: String!) {
    sharedQuiz(token: $token) {
      title
      ownerName
      questions { id prompt choices { id text } }
    }
  }
`)

const SubmitSharedQuizDocument = op(`
  mutation SubmitSharedQuiz($token: String!, $answers: JSON!) {
    submitSharedQuiz(input: { token: $token, answers: $answers }) {
      score
      total
      userErrors { message }
    }
  }
`)

const NotePagesDocument = op(`
  query NotePages($noteId: UUID!) {
    notePages(noteId: $noteId) { pages }
  }
`)

const SaveNotePagesDocument = op(`
  mutation SaveNotePages($noteId: UUID!, $pages: JSON!) {
    saveNotePages(input: { noteId: $noteId, pages: $pages }) {
      userErrors { message }
    }
  }
`)

const TranscribeVoiceNoteDocument = op(`
  mutation TranscribeVoiceNote($noteId: UUID!, $captions: String!) {
    transcribeVoiceNote(input: { noteId: $noteId, captions: $captions }) {
      transcript
      userErrors { message }
    }
  }
`)

const NotesFromTranscriptDocument = op(`
  mutation NotesFromTranscript($noteId: UUID!, $transcript: String!) {
    notesFromTranscript(input: { noteId: $noteId, transcript: $transcript }) {
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

export interface QuizShare {
  token: string
  url: string
  stats: QuizShareStats
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

type Payload<T> = T & { userErrors?: UserProblem[] }

export async function setNoteVisibility(client: ApolloClient, noteId: string, audience: ShareAudience) {
  const res = await client.mutate({ mutation: ChangeNoteVisibilityDocument, variables: { noteId, visibility: wireVisibility(audience) } })
  return res.data?.changeNoteVisibility ?? null
}

export async function forkNote(client: ApolloClient, noteId: string) {
  const res = await client.mutate({ mutation: ForkNoteDocument, variables: { noteId } })
  return res.data?.forkNote ?? null
}

export async function shareQuiz(client: ApolloClient, noteId: string): Promise<Payload<{ share: { token: string; url: string } | null; stats: QuizShareStats | null }>> {
  const res = await client.mutate({ mutation: ShareQuizDocument, variables: { noteId } })
  const payload = (res.data as { shareQuiz?: Payload<{ share: { token: string; url: string } | null; stats: QuizShareStats | null }> } | null)?.shareQuiz
  if (!payload) throw new Error('no answer')
  return payload
}

export function quizLink(share: { token: string; url: string }, origin: string): string {
  if (share.url.startsWith('http')) return share.url
  if (share.url.startsWith('/')) return `${origin}${share.url}`
  return `${origin}/quiz/${share.token}`
}

export async function loadSharedQuiz(client: ApolloClient, token: string): Promise<SharedQuiz | null> {
  const res = await client.query({ query: SharedQuizDocument, variables: { token }, fetchPolicy: 'network-only' })
  return (res.data as { sharedQuiz?: SharedQuiz | null }).sharedQuiz ?? null
}

export async function submitSharedQuiz(client: ApolloClient, token: string, answers: { questionId: string; choiceId: string }[]) {
  const res = await client.mutate({ mutation: SubmitSharedQuizDocument, variables: { token, answers } })
  const payload = (res.data as { submitSharedQuiz?: Payload<{ score: number | null; total: number | null }> } | null)?.submitSharedQuiz
  if (!payload) throw new Error('no answer')
  return payload
}

export async function notePages(client: ApolloClient, noteId: string): Promise<NotePage[]> {
  const res = await client.query({ query: NotePagesDocument, variables: { noteId }, fetchPolicy: 'network-only' })
  const pages = pagesFromUnknown((res.data as { notePages?: { pages?: unknown } | null }).notePages?.pages)
  return pages ?? []
}

export async function saveNotePages(client: ApolloClient, noteId: string, pages: NotePage[]) {
  const res = await client.mutate({ mutation: SaveNotePagesDocument, variables: { noteId, pages } })
  const payload = (res.data as { saveNotePages?: { userErrors?: UserProblem[] } } | null)?.saveNotePages
  if (!payload) throw new Error('no answer')
  return payload
}

export async function transcribeVoiceNote(client: ApolloClient, noteId: string, captions: string) {
  const res = await client.mutate({ mutation: TranscribeVoiceNoteDocument, variables: { noteId, captions } })
  const payload = (res.data as { transcribeVoiceNote?: Payload<{ transcript: string | null }> } | null)?.transcribeVoiceNote
  if (!payload) throw new Error('no answer')
  return payload
}

export async function notesFromTranscript(client: ApolloClient, noteId: string, transcript: string) {
  const res = await client.mutate({ mutation: NotesFromTranscriptDocument, variables: { noteId, transcript } })
  const payload = (res.data as { notesFromTranscript?: Payload<{ markdown: string | null; note: { id: string } | null }> } | null)?.notesFromTranscript
  if (!payload) throw new Error('no answer')
  return payload
}

function op(source: string): DocumentNode {
  return parse(source)
}
