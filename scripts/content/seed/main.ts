/* ============================================================
   SEED — puts every subject into Firestore as structured content,
   and proves it arrived intact.

     npm run content:seed          local emulator (127.0.0.1:8080)
     npm run content:seed:live     the live project (asks to confirm)

   Steps
     1. Read the scanned content (content-build/, from extract.mjs).
     2. Convert every HTML fragment to structured content.
     3. Verify: render each with the app's components and compare
        with the source HTML. Any difference → stop, nothing written.
     4. Write meta, catalog, subjects, topics and problems; delete
        documents that no longer exist in the source.
     5. Read everything back from Firestore and verify again.
   ============================================================ */

import fs from 'node:fs'
import path from 'node:path'
import readline from 'node:readline/promises'
import crypto from 'node:crypto'
import { initializeApp, applicationDefault } from 'firebase-admin/app'
import { getFirestore, type Firestore, type DocumentReference } from 'firebase-admin/firestore'
import {
  CONTENT_SCHEMA, PROBLEM_RICH_FIELDS, flatten, unflatten,
  type Content, type ContentMeta, type FlatContent, type SubjectDoc, type TopicDocFlat,
} from '../../../schema/content'
import { htmlToContent, ConvertError } from './fromHtml'
import { compareContent } from './verify'

const ROOT = path.resolve(import.meta.dirname ?? '.', '../../..')
const SRC = path.join(ROOT, 'content-build')
const MAX_DOC_BYTES = 1_000_000

/* ── args ────────────────────────────────────────────────── */

const args = new Set(process.argv.slice(2))
const live = args.has('--live')
const dryRun = args.has('--dry-run')
// SEED_PROJECT=test (an alias in .firebaserc, or a project id) seeds another project; default: the default project.
const firebaserc = JSON.parse(fs.readFileSync(path.join(ROOT, '.firebaserc'), 'utf8')) as { projects: Record<string, string> }
const projectId = (process.env.SEED_PROJECT && (firebaserc.projects[process.env.SEED_PROJECT] ?? process.env.SEED_PROJECT)) || firebaserc.projects.default

const log = (...a: unknown[]) => console.log(...a)
const read = <T>(rel: string): T => JSON.parse(fs.readFileSync(path.join(SRC, rel), 'utf8')) as T

/* ── source (content-build) ──────────────────────────────── */

interface SourceTopic { subjectId: string; id: string; title: string; group: string; order: number; html: string }
interface SourceSolution { title: string; html: string; code: Record<string, string>; complexity?: string[] }
type SourceProblem = Record<string, unknown> & {
  id: string
  category: string
  naive?: SourceSolution
  optimal?: SourceSolution
  extra?: { title: string; html: string }[]
}
interface Catalog { version: number; generatedAt: string; subjects: (SubjectDoc & { topics: { id: string }[] })[] }

const catalog = read<Catalog>('catalog.json')

/** Every fragment we convert, with where it came from — used for both verification passes. */
interface Fragment { where: string; html: string; content: Content }
const fragments: Fragment[] = []
const problems: SourceProblem[] = []
const failures: string[] = []

function convert(where: string, html: string): Content | null {
  try {
    const content = htmlToContent(html, where)
    fragments.push({ where, html, content })
    return content
  } catch (e) {
    failures.push(e instanceof ConvertError ? e.message : `${where}: ${(e as Error).message}`)
    return null
  }
}

/* ── 1–2. read + convert ─────────────────────────────────── */

type TopicWrite = { ref: string; data: TopicDocFlat }
type ProblemWrite = { ref: string; data: Record<string, unknown> }
const topicWrites: TopicWrite[] = []
const problemWrites: ProblemWrite[] = []

for (const s of catalog.subjects) {
  if (s.kind === 'notes') {
    for (const t of s.topics) {
      const src = read<SourceTopic>(`topics/${s.id}/${t.id}.json`)
      const content = convert(`${s.id}/${t.id}`, src.html)
      if (!content) continue
      topicWrites.push({
        ref: `subjects/${s.id}/topics/${t.id}`,
        data: { subjectId: s.id, id: src.id, title: src.title, group: src.group, order: src.order, content: flatten(content), schema: CONTENT_SCHEMA },
      })
    }
  } else {
    for (const t of s.topics) {
      for (const p of read<{ problems: SourceProblem[] }>(`problems/${t.id}.json`).problems) {
        problems.push(p)
        const doc: Record<string, unknown> = { ...p }
        for (const f of PROBLEM_RICH_FIELDS) {
          delete doc[f]
          const html = p[f] as string | undefined
          if (html) {
            const c = convert(`${s.id}/${p.id}.${f}`, html)
            if (c) doc[f] = flatten(c)
          }
        }
        for (const k of ['naive', 'optimal'] as const) {
          const sol = p[k]
          if (!sol) continue
          const c = sol.html ? convert(`${s.id}/${p.id}.${k}`, sol.html) : []
          const { html: _html, ...rest } = sol
          void _html
          doc[k] = { ...rest, content: flatten(c ?? []) }
        }
        if (p.extra) {
          doc.extra = p.extra.map((x, i) => ({ title: x.title, content: flatten(convert(`${s.id}/${p.id}.extra[${i}]`, x.html) ?? []) }))
        }
        doc.schema = CONTENT_SCHEMA
        problemWrites.push({ ref: `subjects/${s.id}/problems/${p.id}`, data: doc })
      }
    }
  }
}

if (failures.length) {
  console.error(`\n✗ ${failures.length} fragment(s) could not be converted:\n\n${failures.slice(0, 20).join('\n\n')}`)
  process.exit(1)
}
log(`Converted ${fragments.length} fragments (${topicWrites.length} topics, ${problemWrites.length} problems).`)

/* ── 3. verify before writing ────────────────────────────── */

function verifyAll(label: string, get: (f: Fragment) => Content) {
  const bad: string[] = []
  for (const f of fragments) {
    const diff = compareContent(f.html, get(f))
    if (diff) bad.push(`${f.where}: ${diff}`)
  }
  if (bad.length) {
    console.error(`\n✗ ${label}: ${bad.length} of ${fragments.length} fragments differ from the source:\n\n${bad.slice(0, 10).join('\n\n')}`)
    process.exit(1)
  }
  log(`✓ ${label}: all ${fragments.length} fragments render exactly like the source.`)
}

verifyAll('Round-trip (source → structured → rendered)', (f) => f.content)
verifyAll('Flat encoding (flatten → unflatten)', (f) => unflatten(flatten(f.content)))

/* ── version + documents ─────────────────────────────────── */

const subjects: SubjectDoc[] = catalog.subjects.map(({ topics, ...s }) => ({ ...s, topicCount: topics.length }))
const hash = crypto.createHash('sha256')
hash.update(JSON.stringify(catalog.subjects))
for (const w of [...topicWrites, ...problemWrites]) hash.update(w.ref).update(JSON.stringify(w.data))
const version = hash.digest('hex').slice(0, 16)
const meta: ContentMeta = {
  version, schema: CONTENT_SCHEMA, generatedAt: catalog.generatedAt,
  subjects: subjects.length, topics: topicWrites.length, problems: problemWrites.length,
}

const sizes = [...topicWrites, ...problemWrites].map((w) => ({ ref: w.ref, bytes: Buffer.byteLength(JSON.stringify(w.data)) }))
const largest = sizes.sort((a, b) => b.bytes - a.bytes)[0]
const tooBig = sizes.filter((s) => s.bytes > MAX_DOC_BYTES)
if (tooBig.length) {
  console.error(`✗ Documents over Firestore's 1 MiB limit:\n${tooBig.map((t) => `  ${t.ref} ${t.bytes} B`).join('\n')}`)
  process.exit(1)
}
log(`Content version ${version} · largest document ${largest.ref} (${(largest.bytes / 1024).toFixed(0)} KB) · catalog ${(Buffer.byteLength(JSON.stringify(catalog)) / 1024).toFixed(0)} KB`)

if (dryRun) {
  log('Dry run — nothing written.')
  process.exit(0)
}

/* ── 4. write ────────────────────────────────────────────── */

async function confirmLive() {
  if (args.has('--yes')) return
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout })
  const answer = await rl.question(`\nThis writes ${topicWrites.length + problemWrites.length + subjects.length + 2} documents to the LIVE project "${projectId}". Type the project id to continue: `)
  rl.close()
  if (answer.trim() !== projectId) {
    console.error('Cancelled.')
    process.exit(1)
  }
}

function connect(): Firestore {
  if (live) {
    delete process.env.FIRESTORE_EMULATOR_HOST
    initializeApp({ credential: applicationDefault(), projectId })
  } else {
    process.env.FIRESTORE_EMULATOR_HOST ??= '127.0.0.1:8080'
    initializeApp({ projectId })
  }
  const db = getFirestore()
  db.settings({ ignoreUndefinedProperties: true })
  return db
}

async function write(db: Firestore) {
  const writer = db.bulkWriter()
  writer.onWriteError((err) => err.failedAttempts < 5)
  let count = 0
  const put = (ref: DocumentReference, data: object) => { count++; void writer.set(ref, data) }

  put(db.doc('catalog/current'), catalog)
  for (const s of subjects) put(db.doc(`subjects/${s.id}`), s)
  for (const w of topicWrites) put(db.doc(w.ref), w.data)
  for (const w of problemWrites) put(db.doc(w.ref), w.data)
  await writer.flush()

  // Remove documents that no longer exist in the source.
  const want = new Set([...subjects.map((s) => `subjects/${s.id}`), ...topicWrites.map((w) => w.ref), ...problemWrites.map((w) => w.ref)])
  let removed = 0
  for (const sub of (await db.collection('subjects').listDocuments())) {
    if (!want.has(sub.path)) { await db.recursiveDelete(sub); removed++; continue }
    for (const coll of await sub.listCollections()) {
      for (const d of await coll.listDocuments()) if (!want.has(d.path)) { void writer.delete(d); removed++ }
    }
  }
  // meta last: clients only switch to the new version once everything is in place.
  put(db.doc('meta/content'), meta)
  await writer.close()
  log(`Wrote ${count} documents${removed ? `, removed ${removed} stale` : ''}.`)
}

/* ── 5. read back + verify ───────────────────────────────── */

async function verifyStored(db: Firestore) {
  const byWhere = new Map<string, Content>()
  const topicSnaps = await db.getAll(...topicWrites.map((w) => db.doc(w.ref)))
  for (const snap of topicSnaps) {
    const d = snap.data() as TopicDocFlat | undefined
    if (!d) throw new Error(`missing after write: ${snap.ref.path}`)
    byWhere.set(`${d.subjectId}/${d.id}`, unflatten(d.content))
  }
  const problemSnaps = await db.getAll(...problemWrites.map((w) => db.doc(w.ref)))
  for (const snap of problemSnaps) {
    const d = snap.data() as Record<string, unknown> | undefined
    if (!d) throw new Error(`missing after write: ${snap.ref.path}`)
    const sid = snap.ref.parent.parent!.id
    for (const f of PROBLEM_RICH_FIELDS) if (d[f]) byWhere.set(`${sid}/${d.id}.${f}`, unflatten(d[f] as FlatContent))
    for (const k of ['naive', 'optimal']) {
      const sol = d[k] as { content: FlatContent } | undefined
      if (sol?.content.length) byWhere.set(`${sid}/${d.id}.${k}`, unflatten(sol.content))
    }
    ;(d.extra as { content: FlatContent }[] | undefined)?.forEach((x, i) => byWhere.set(`${sid}/${d.id}.extra[${i}]`, unflatten(x.content)))
  }
  const metaSnap = await db.doc('meta/content').get()
  if ((metaSnap.data() as ContentMeta | undefined)?.version !== version) throw new Error('meta/content was not updated')
  const missing = fragments.filter((f) => !byWhere.has(f.where))
  if (missing.length) throw new Error(`fragments missing in Firestore: ${missing.slice(0, 5).map((m) => m.where).join(', ')}`)
  verifyAll('Stored in Firestore (read back → rendered)', (f) => byWhere.get(f.where)!)
}

if (live) await confirmLive()
const db = connect()
log(`Target: ${live ? `LIVE project ${projectId}` : `emulator ${process.env.FIRESTORE_EMULATOR_HOST} (project ${projectId})`}`)
try {
  await write(db)
  await verifyStored(db)
  log(`\nDone — ${subjects.length} subjects, ${topicWrites.length} topics, ${problemWrites.length} problems. Content version ${version}.`)
} catch (e) {
  const msg = (e as Error).message
  if (/ECONNREFUSED|UNAVAILABLE/.test(msg) && !live) {
    console.error(`\n✗ Can't reach the Firestore emulator at ${process.env.FIRESTORE_EMULATOR_HOST}. Start it first: npm run emulators`)
  } else {
    console.error(`\n✗ ${msg}`)
  }
  process.exit(1)
}
process.exit(0)
