// Copied from lvn-backend contracts/src/validation/notes.ts by scripts/contracts-sync.mjs — do not edit here.
import { z } from 'zod'

/** Limits on notes and how they are organised (Phase 2). Changing one is a contracts change, so all apps agree. */
export const NOTE_LIMITS = {
  title: 200,
  cardsPerNote: 1_000,
  /** Card operations in one save (`updateNoteDraft`) */
  opsPerSave: 200,
  tagsPerNote: 20,
  topicsPerNote: 10,
  tagName: 40,
  folderName: 80,
  folderDepth: 5,
  topicTitle: 120,
  /** Versions kept per non-public note; public notes keep every version (§4.3) */
  versionsKept: 50,
  trashDays: 30,
} as const

const collapse = (s: string) => s.replace(/\s+/g, ' ').trim()
const noControl = (s: string) => [...s].every((c) => c.charCodeAt(0) >= 0x20 && c.charCodeAt(0) !== 0x7f)

/** A note's title; empty is allowed and shown as "Untitled". */
export const noteTitleSchema = z.string().transform(collapse).pipe(z.string().max(NOTE_LIMITS.title).refine(noControl, 'Remove control characters'))

export const folderNameSchema = z
  .string()
  .transform(collapse)
  .pipe(z.string().min(1, 'Give the folder a name').max(NOTE_LIMITS.folderName).refine(noControl, 'Remove control characters'))

/** Tags are one or more words; `#` is dropped, case is kept but two tags differing only in case are the same tag. */
export const tagNameSchema = z
  .string()
  .transform((s) => collapse(s).replace(/^#+/, ''))
  .pipe(z.string().min(1, 'Give the tag a name').max(NOTE_LIMITS.tagName).refine(noControl, 'Remove control characters'))

export const topicTitleSchema = z
  .string()
  .transform(collapse)
  .pipe(z.string().min(2, 'Give the topic a name').max(NOTE_LIMITS.topicTitle).refine(noControl, 'Remove control characters'))

/** URL part of a title: lower-case ASCII words joined by hyphens, at most 60 characters; "note" when nothing is left. */
export function slugify(title: string): string {
  const slug = title
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60)
    .replace(/-+$/g, '')
  return slug || 'note'
}
