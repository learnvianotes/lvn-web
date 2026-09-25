/* ============================================================
   SHEET 150 — TYPE MODEL
   Canonical types for Sheet 150 problems and categories.
   These types are consumed by the UI layer and the data-access
   layer (src/lib/sheet150.ts). Problem content lives in
   Firestore at: subjects/sheet-150/questions/{id}
   ============================================================ */

/** Programming languages supported in code solutions */
export type CodeLanguage = 'py' | 'cpp' | 'java' | 'js'

/** Difficulty labels (casing preserved as stored in Firestore) */
export type Sheet150Difficulty = 'Easy' | 'Medium' | 'Hard'

/* ── Code Solution ─────────────────────────────────────────── */

/**
 * One complete solution (brute-force or optimized).
 * All fields optional except complexities; a problem may not
 * have all languages implemented yet.
 */
export interface CodeSolution {
  /** Human-readable title, e.g. "Naive Solution — O(n²) Brute Force" */
  title: string
  /** Short explanation of the approach */
  explanation?: string
  /** Step-by-step walkthrough (each string is one bullet step) */
  approach?: string[]
  /** Big-O time complexity, e.g. "O(n)" */
  complexityTime: string
  /** Big-O space complexity, e.g. "O(n)" */
  complexitySpace: string
  /** Code implementations keyed by language */
  code: Partial<Record<CodeLanguage, string>>
}

/* ── Input / Output ────────────────────────────────────────── */

export interface IOExample {
  in: string
  out: string
  comment?: string
}

export interface InputOutput {
  input?: string
  output?: string
  examples?: IOExample[]
}

/* ── Similar Question Reference ────────────────────────────── */

export interface SimilarQuestion {
  /** URL slug of the linked problem (e.g. "group-anagrams") */
  slug?: string
  title: string
  /** LeetCode problem number */
  lc: number
  difficulty: string
}

/* ── Sheet 150 Problem ─────────────────────────────────────── */

/**
 * A single Sheet 150 problem document as stored in Firestore.
 * Path: subjects/sheet-150/questions/{id}
 */
export interface Sheet150Problem {
  /** Stable document ID, e.g. "lc-1" */
  id: string
  /** URL-safe slug, e.g. "two-sum" — used in /sheet-150/problems/:slug */
  slug: string
  /** LeetCode problem number */
  lcNumber: number
  /** Display title */
  title: string
  difficulty: Sheet150Difficulty
  /** Category slug, e.g. "arrays-hashing" */
  category: string
  /** Sort order within the category */
  order?: number
  /** Short concept tags, e.g. ["array", "hash-map"] */
  tags?: string[]
  /** LeetCode URL */
  leetcodeUrl?: string

  /** Full problem description */
  problemStatement: string
  inputOutput?: InputOutput
  constraints?: string[]

  /** Key insight / understanding block */
  keyInsight?: string

  /** Brute-force / naive solution */
  naiveSolution?: CodeSolution
  /** Optimal solution */
  optimalSolution?: CodeSolution

  /** Related problems */
  similarQuestions?: SimilarQuestion[]

  /** Firestore server timestamp */
  updatedAt?: unknown
}

/* ── Category ──────────────────────────────────────────────── */

/**
 * A category entry stored in the subjects/sheet-150 document
 * under the `categories` array field.
 */
export interface Sheet150Category {
  /** Slug, e.g. "arrays-hashing" */
  id: string
  /** Display label, e.g. "Arrays & Hashing" */
  label: string
  /** Sort position */
  order: number
  /** Total problems in this category */
  problemCount: number
}
