/* ============================================================
   /core DATA — the documents the old site read from Firestore,
   built from content-build/ at build time and served as static
   JSON by app/(core)/core/data/[...path]/route.ts.

   The shapes and the conversion are the old seeder's
   (scripts/content/seed/main.ts): every HTML fragment becomes
   structured content (htmlToContent), so the app renders it
   with the same components as before. Nothing runs per request.
   ============================================================ */

import 'server-only'
import crypto from 'node:crypto'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { CONTENT_SCHEMA, PROBLEM_RICH_FIELDS, type ContentMeta } from '@core-schema/content'
import type { Catalog, Problem, Solution, TopicDoc } from '@core/features/catalog/types'
import { htmlToContent } from './fromHtml'

const ROOT = path.join(process.cwd(), 'content-build')
const SAFE_ID = /^[a-z0-9][a-z0-9_-]*$/i

const raw = new Map<string, string>()
function readText(rel: string): string {
  let text = raw.get(rel)
  if (text === undefined) {
    text = readFileSync(path.join(ROOT, rel), 'utf8')
    raw.set(rel, text)
  }
  return text
}
const readJson = <T>(rel: string) => JSON.parse(readText(rel)) as T

/* ── source (content-build) ──────────────────────────────── */

interface SourceTopic { subjectId: string; id: string; title: string; group: string; order: number; html: string }
interface SourceSolution { title: string; html: string; code: Solution['code']; complexity?: string[] }
type SourceProblem = Record<string, unknown> & {
  id: string
  order: number
  naive?: SourceSolution
  optimal?: SourceSolution
  extra?: { title: string; html: string }[]
}

let catalogMemo: Catalog | undefined
/** The catalog exactly as the old site stored it (Firestore catalog/current). */
export function legacyCatalog(): Catalog {
  catalogMemo ??= readJson<Catalog>('catalog.json')
  return catalogMemo
}

const subjectOf = (id: string) => legacyCatalog().subjects.find((s) => s.id === id)

/* ── documents ───────────────────────────────────────────── */

export function legacyTopic(subjectId: string, topicId: string): TopicDoc | undefined {
  const subject = subjectOf(subjectId)
  if (subject?.kind !== 'notes' || !SAFE_ID.test(topicId) || !subject.topics.some((t) => t.id === topicId)) return undefined
  const src = readJson<SourceTopic>(`topics/${subjectId}/${topicId}.json`)
  const where = `${subjectId}/${topicId}`
  return { subjectId, id: src.id, title: src.title, group: src.group, order: src.order, content: htmlToContent(src.html, where) }
}

function toProblem(subjectId: string, p: SourceProblem): Problem {
  const doc: Record<string, unknown> = { ...p }
  const at = (field: string) => `${subjectId}/${p.id}.${field}`
  for (const f of PROBLEM_RICH_FIELDS) {
    delete doc[f]
    const html = p[f] as string | undefined
    if (html) doc[f] = htmlToContent(html, at(f))
  }
  for (const k of ['naive', 'optimal'] as const) {
    const sol = p[k]
    if (!sol) continue
    const { html, ...rest } = sol
    doc[k] = { ...rest, content: html ? htmlToContent(html, at(k)) : [] } satisfies Solution
  }
  if (p.extra) doc.extra = p.extra.map((x, i) => ({ title: x.title, content: htmlToContent(x.html, at(`extra[${i}]`)) }))
  return doc as unknown as Problem
}

/** One category of a problem sheet, in sheet order (the old `where('category', '==', id)` query). */
export function legacyProblems(subjectId: string, categoryId: string): Problem[] | undefined {
  const subject = subjectOf(subjectId)
  if (subject?.kind !== 'problems' || !subject.topics.some((t) => t.id === categoryId)) return undefined
  const { problems } = readJson<{ problems: SourceProblem[] }>(`problems/${categoryId}.json`)
  return problems.map((p) => toProblem(subjectId, p)).sort((a, b) => a.order - b.order)
}

/* ── paths ───────────────────────────────────────────────── */

/** Every document's path under /core/data, e.g. `topics/python/variables.json`. */
export function legacyDataPaths(): string[] {
  return [
    'meta.json',
    'catalog.json',
    ...legacyCatalog().subjects.flatMap((s) =>
      s.topics.map((t) => (s.kind === 'notes' ? `topics/${s.id}/${t.id}.json` : `problems/${s.id}/${t.id}.json`)),
    ),
  ]
}

let metaMemo: ContentMeta | undefined
/**
 * The content version: a hash of everything served, so a device's cached copy is replaced
 * exactly when the content changes (source.ts compares it once per session).
 */
export function legacyMeta(): ContentMeta {
  if (metaMemo) return metaMemo
  const catalog = legacyCatalog()
  const hash = crypto.createHash('sha256').update(String(CONTENT_SCHEMA)).update(readText('catalog.json'))
  let topics = 0, problems = 0
  for (const s of catalog.subjects) {
    for (const t of s.topics) {
      if (s.kind === 'notes') {
        hash.update(readText(`topics/${s.id}/${t.id}.json`))
        topics++
      } else {
        const text = readText(`problems/${t.id}.json`)
        hash.update(text)
        problems += (JSON.parse(text) as { problems: unknown[] }).problems.length
      }
    }
  }
  metaMemo = {
    version: hash.digest('hex').slice(0, 16),
    schema: CONTENT_SCHEMA,
    generatedAt: catalog.generatedAt,
    subjects: catalog.subjects.length,
    topics,
    problems,
  }
  return metaMemo
}

/** The document at a /core/data path, or undefined when there is none. */
export function legacyDocument(dataPath: string): ContentMeta | Catalog | TopicDoc | Problem[] | undefined {
  if (dataPath === 'meta.json') return legacyMeta()
  if (dataPath === 'catalog.json') return legacyCatalog()
  const m = /^(topics|problems)\/([^/]+)\/([^/]+)\.json$/.exec(dataPath)
  if (!m) return undefined
  const [, kind, subjectId = '', id = ''] = m
  return kind === 'topics' ? legacyTopic(subjectId, id) : legacyProblems(subjectId, id)
}
