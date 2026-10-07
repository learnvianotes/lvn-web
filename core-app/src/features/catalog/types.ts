/* ============================================================
   CONTENT TYPES
   The app-side shape of study content, as read from Firestore
   (flat content is rebuilt into trees — see schema/content.ts).
   ============================================================ */

import type { Content } from '@core-schema/content'

export type SubjectKind = 'notes' | 'problems'
export type Difficulty = 'Easy' | 'Medium' | 'Hard'
export type CodeLang = 'py' | 'cpp' | 'java' | 'js'

export interface ProblemSummary {
  id: string
  lc: number
  title: string
  difficulty: Difficulty
}

/** A sidebar entry: a notes topic, or a Sheet 150 category (with problems). */
export interface TopicOutline {
  id: string
  title: string
  group: string
  /** h3 headings inside the topic — used by search */
  headings?: string[]
  /** key terms (bold phrases, sub-headings) — used by search */
  keywords?: string
  /** only for `problems` subjects */
  problems?: ProblemSummary[]
}

export interface Subject {
  id: string
  title: string
  description: string
  icon: string
  /** landing-page filter group (Catalog.categories) */
  category?: string
  kind: SubjectKind
  order: number
  /** topics for notes; problems for problem sheets */
  itemCount: number
  topics: TopicOutline[]
}

export interface SubjectCategory {
  id: string
  title: string
}

export interface Catalog {
  version: number
  generatedAt: string
  categories?: SubjectCategory[]
  subjects: Subject[]
}

export interface TopicDoc {
  subjectId: string
  id: string
  title: string
  group: string
  order: number
  content: Content
}

export interface Solution {
  title: string
  content: Content
  code: Partial<Record<CodeLang, string>>
  complexity?: string[]
}

export interface SimilarProblem {
  title: string
  difficulty: string
  lc: number | null
  url: string
}

export interface Problem extends ProblemSummary {
  slug: string
  category: string
  order: number
  leetcodeUrl: string
  youtubeUrl: string
  statement?: Content
  io?: Content
  constraints?: Content
  understanding?: Content
  naive?: Solution
  intuition?: Content
  approach?: Content
  optimal?: Solution
  variants?: Content
  takeaway?: Content
  similar?: SimilarProblem[]
  extra?: { title: string; content: Content }[]
}
