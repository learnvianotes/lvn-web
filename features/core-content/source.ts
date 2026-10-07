import 'server-only'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { cache } from 'react'
import { catalog, problemSet, topic, type Catalog, type Subject } from './schema'

/**
 * Reads the existing study content from content-build/ at build time. Every /core page is
 * statically generated, so nothing here runs per request. When the `notes` context owns
 * Subjects and Topics (Phase 2), this module is the one place that switches to GraphQL.
 */

const ROOT = path.join(process.cwd(), 'content-build')
const SAFE_ID = /^[a-z0-9][a-z0-9_-]*$/i

function readJson(...parts: string[]): unknown {
  return JSON.parse(readFileSync(path.join(ROOT, ...parts), 'utf8'))
}

export const getCatalog = cache((): Catalog => {
  const data = catalog.parse(readJson('catalog.json'))
  data.subjects.sort((a, b) => a.order - b.order)
  return data
})

export function getSubject(id: string): Subject | undefined {
  return getCatalog().subjects.find((s) => s.id === id)
}

export const getTopic = cache((subjectId: string, topicId: string) => {
  if (!SAFE_ID.test(subjectId) || !SAFE_ID.test(topicId)) return undefined
  try {
    return topic.parse(readJson('topics', subjectId, `${topicId}.json`))
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') return undefined
    throw err
  }
})

export const getProblemSet = cache((categoryId: string) => {
  if (!SAFE_ID.test(categoryId)) return undefined
  try {
    const set = problemSet.parse(readJson('problems', `${categoryId}.json`))
    set.problems.sort((a, b) => a.order - b.order)
    return set
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code === 'ENOENT') return undefined
    throw err
  }
})

/** Every (subject, item) pair — the static params for /core/[subjectId]/[itemId]. */
export function allItems(): { subjectId: string; itemId: string }[] {
  return getCatalog().subjects.flatMap((s) => s.topics.map((t) => ({ subjectId: s.id, itemId: t.id })))
}

/** Topics in reading order with their group, plus the neighbours of one topic. */
export function neighbours(subject: Subject, itemId: string) {
  const i = subject.topics.findIndex((t) => t.id === itemId)
  return { prev: i > 0 ? subject.topics[i - 1] : undefined, next: subject.topics[i + 1] }
}
