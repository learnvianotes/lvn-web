/* ============================================================
   C-NOTE DOMAIN TYPES
   Core domain model. Designed for extensibility.
   Content is data-driven — components do not hardcode content.
   ============================================================ */

import type { Slug, ISODateString } from './common'

/* ── Difficulty ───────────────────────────────────────────── */
export type Difficulty = 'easy' | 'medium' | 'hard'

/* ── Subject category ─────────────────────────────────────── */
export type SubjectCategory = 'core-cs' | 'dsa' | 'ai-ml' | 'tools'

/* ── Progress ─────────────────────────────────────────────── */
export type ProgressStatus = 'unsolved' | 'solved' | 'revisit'

/* ── Subject ──────────────────────────────────────────────── */
/**
 * A top-level learning domain in C-NOTE.
 * e.g. "Computer Networks", "Operating Systems", "DSA — Basics"
 */
export interface Subject {
  id: Slug
  title: string
  shortTitle?: string
  description: string
  category: SubjectCategory
  /** Lucide icon name to use for this subject */
  lucideIcon: string
  /** Ordered list of topic IDs belonging to this subject */
  topicIds: Slug[]
  /** Short tags shown on the subject card (max 3) */
  displayTags?: string[]
  /** Search keywords and topic terms for quick filtering */
  keywords?: string
  /** Approximate total question/item count */
  itemCount?: number
  /** Whether this subject is actively being worked on */
  isActive?: boolean
  createdAt?: ISODateString
  updatedAt?: ISODateString
}

/* ── Topic ────────────────────────────────────────────────── */
/**
 * A chapter or section within a Subject.
 * e.g. "Arrays", "TCP/IP", "Process Scheduling"
 */
export interface Topic {
  id: Slug
  subjectId: Slug
  title: string
  description?: string
  /** Ordered list of question IDs in this topic */
  questionIds: Slug[]
  order: number
  createdAt?: ISODateString
  updatedAt?: ISODateString
}

/* ── Question ─────────────────────────────────────────────── */
/**
 * A single learning item / interview question.
 * The actual content lives in src/content/ as separate files.
 * This type defines the metadata only.
 */
export interface Question {
  id: Slug
  topicId: Slug
  subjectId: Slug
  title: string
  difficulty: Difficulty
  /** Short conceptual tags — e.g. ["sliding-window", "hash-map"] */
  tags: string[]
  /** Optional external reference (e.g. LeetCode problem number) */
  externalRef?: string
  order: number
  createdAt?: ISODateString
  updatedAt?: ISODateString
}

/* ── User progress (future-ready) ────────────────────────── */
/**
 * Tracks a user's status on a single question.
 * Stored locally via storage abstraction. Firebase-ready later.
 */
export interface QuestionProgress {
  questionId: Slug
  status: ProgressStatus
  /** Last time this status was updated */
  updatedAt: ISODateString
  /** Optional personal notes */
  notes?: string
}

/* ── Registry ─────────────────────────────────────────────── */
/**
 * Top-level data structure that the app consumes.
 * Populated from src/data/ at build time.
 */
export interface ContentRegistry {
  subjects: Subject[]
  topics: Topic[]
  questions: Question[]
}
