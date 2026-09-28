/* ============================================================
   DATA SCHEMA — the single source of truth for every document
   the app stores, shared by the web app (import from
   '@schema/firestore') and the Cloud Functions backend (copied
   into functions/src/schema at build time).

   Firestore layout (enforced by firestore.rules):

     users/{uid}                       UserDoc
     users/{uid}/days/{YYYY-MM-DD}     DayDoc       per-day study log
     users/{uid}/notes/{noteId}        NoteDoc      personal notes
     users/{uid}/events/{batchId}      EventBatchDoc  raw activity events (append-only)
     topicStats/{topicId}              TopicStatsDoc  aggregated by the backend
     trending/current                  TrendingDoc    aggregated by the backend

   Keys: a topic is 'subjectId/topicId'. Firestore ids can't
   contain '/', so ids use '~' instead (see docId()).
   Bump SCHEMA_VERSION on breaking changes and migrate on read.
   ============================================================ */

export const SCHEMA_VERSION = 1

export const docId = (key: string) => key.replace(/\//g, '~')

/* ── users/{uid} ─────────────────────────────────────────── */

export type ProblemMark = 'solved' | 'revisit'

export interface ProgressData {
  /** problemId → mark */
  problems: Record<string, ProblemMark>
  /** topic key → read to the end */
  topics: Record<string, true>
  /** topic key → learner asked to revisit */
  revisitTopics: Record<string, true>
  /** 'YYYY-MM-DD' → items completed that day */
  studied: Record<string, number>
}

export type SubjectSort = 'default' | 'custom' | 'az' | 'progress' | 'recent'

export interface Prefs {
  /** subject ids in the learner's own order (sort 'custom') */
  subjectOrder: string[]
  sort: SubjectSort
  /** upcoming course ids the learner wants ("Notify me") */
  interests: string[]
  /** daily study goal in minutes */
  dailyGoal: number
  updatedAt: number
}

export interface UserDoc {
  progress: ProgressData
  prefs?: Prefs
  schema: number
  updatedAt: number
}

/* ── users/{uid}/days/{day} ──────────────────────────────── */

export interface TopicVisit {
  title: string
  subject: string
  /** seconds actively studied that day */
  sec: number
  visits: number
  /** epoch ms of the latest visit */
  last: number
}

export interface DayDoc {
  /** topic key → visit */
  topics: Record<string, TopicVisit>
  /** seconds of focus-timer sessions */
  focus: number
  updatedAt: number
}

/* ── users/{uid}/notes/{noteId} ──────────────────────────── */

export interface NoteDoc {
  key: string
  text: string
  updatedAt: number
}

/* ── users/{uid}/events/{batchId} ────────────────────────────
   Raw, append-only activity log — the input for analytics and
   the future recommendation system. Events are batched on the
   client (one document per batch) to keep writes cheap.        */

export const EVENT_TYPES = [
  'session_start',
  'page_view',
  'topic_view',
  'topic_time',
  'topic_complete',
  'topic_revisit',
  'problem_status',
  'search',
  'listen',
  'focus_complete',
  'kit_open',
  'note_save',
  'subject_filter',
  'subject_sort',
  'course_interest',
] as const

export type EventType = (typeof EVENT_TYPES)[number]

export interface StudyEvent {
  /** epoch ms */
  t: number
  type: EventType
  /** subject id */
  s?: string
  /** topic / category id */
  k?: string
  /** item id: problem id, course id, path, … */
  i?: string
  /** numeric value: seconds, result count, … */
  v?: number
  /** short label: status, tab, query, sort, … (≤ 80 chars) */
  l?: string
}

export const EVENT_BATCH_MAX = 100

export interface EventBatchDoc {
  day: string
  createdAt: number
  session: string
  client: { app: string; platform: string; width: number }
  events: StudyEvent[]
}

/* ── aggregates (written only by the backend) ────────────── */

export interface TopicStatsDoc {
  key: string
  title: string
  subject: string
  /** all-time totals */
  views: number
  seconds: number
  completes: number
  /** 'YYYY-MM-DD' → { views, seconds, users } for the last 30 days */
  daily: Record<string, { views: number; seconds: number; users: number }>
  updatedAt: number
}

export interface TrendingDoc {
  /** most studied topics of the last 7 days */
  topics: { key: string; title: string; subject: string; score: number }[]
  updatedAt: number
}
