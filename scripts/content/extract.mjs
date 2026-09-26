/* ============================================================
   CONTENT PIPELINE — extract
   Reads the legacy HTML in content-src/legacy-html and writes
   structured JSON to public/content:

     catalog.json                         all subjects + outlines (search, sidebars, progress totals)
     topics/<subjectId>/<topicId>.json    one theory topic { html }
     problems/<categoryId>.json           all Sheet 150 problems of one category

   The same JSON is what `seed-firestore.mjs` uploads, so the
   static and Firestore content sources always match.

   Usage: node scripts/content/extract.mjs
   ============================================================ */

import fs from 'node:fs'
import path from 'node:path'
import { parseHTML } from 'linkedom'
import { SUBJECTS, SHEET_150_CATEGORIES, SHEET_150_FILES, LEGACY_DIR, OUT_DIR } from './config.mjs'
import { normalizeFragment, normalizeLang, codeText, cleanText, sectionize } from './sanitize.mjs'
import { cppCompiles, javaParses, saveCache, cppErrors, javaErrors, jsErrors } from './validate-code.mjs'

const report = { warnings: [], droppedCode: [] }
/** problem id → dropped snippets; reset when a later file overrides the problem */
const droppedByProblem = new Map()
const warn = (msg) => report.warnings.push(msg)

function load(rel) {
  return parseHTML(fs.readFileSync(path.join(LEGACY_DIR, rel), 'utf8')).document
}

// Build into a sibling directory and swap it in at the end, so the running
// site never sees a half-written content folder.
const BUILD_DIR = `${OUT_DIR}.next`

function writeJson(rel, data) {
  const file = path.join(BUILD_DIR, rel)
  fs.mkdirSync(path.dirname(file), { recursive: true })
  fs.writeFileSync(file, JSON.stringify(data))
  return fs.statSync(file).size
}

const slug = (s) => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')

/* ── Theory subjects ─────────────────────────────────────── */

function extractNotes(subject) {
  const doc = load(subject.source)
  const findPage = (id) => doc.getElementById(`p-${id}`) ?? doc.getElementById(`topic-${id}`)

  // Walk the sidebar in document order, tracking the current group heading.
  const topics = []
  const seen = new Set()
  let group = ''
  for (const el of doc.querySelectorAll('.nav-section, [id^="sn-"], [id^="nav-"]')) {
    if (el.classList.contains('nav-section')) { group = cleanText(el.textContent); continue }
    const id = el.id.replace(/^(sn|nav)-/, '')
    if (seen.has(id) || !findPage(id)) continue
    seen.add(id)
    const label = el.cloneNode(true)
    for (const b of label.querySelectorAll('.badge, [class*="badge"], .count')) b.remove()
    topics.push({ id, title: cleanText(label.textContent).replace(/^\d+[.)]\s*/, ''), group })
  }
  // Pages that exist but were never linked from the sidebar.
  for (const page of doc.querySelectorAll('[id^="p-"], [id^="topic-"]')) {
    const id = page.id.replace(/^(p|topic)-/, '')
    if (seen.has(id) || page.id.startsWith('topic-nav')) continue
    const title = cleanText(page.querySelector('.page-title, .pagetitle, .ptitle, h2')?.textContent ?? id)
    warn(`${subject.id}: page "${id}" is not in the sidebar — added under "More"`)
    seen.add(id)
    topics.push({ id, title, group: 'More' })
  }

  // DSA files use a single "Topics Checklist" group; use each page's eyebrow instead.
  const groups = new Set(topics.map((t) => t.group))
  if (groups.size <= 1) {
    for (const t of topics) t.group = cleanText(findPage(t.id).querySelector('.eyebrow')?.textContent ?? '')
  }

  const outline = []
  for (const [i, t] of topics.entries()) {
    const page = findPage(t.id)
    const html = sectionize(normalizeFragment(page, doc), parseHTML)
    if (html.length < 200) warn(`${subject.id}/${t.id}: very little content (${html.length} chars)`)
    const frag = parseHTML(`<div>${html}</div>`).document
    const headings = [...frag.querySelectorAll('h3')].map((h) => cleanText(h.textContent)).filter(Boolean).slice(0, 60)
    // Key terms for search: sub-headings and bold phrases (full text would bloat the catalog).
    const keywords = [...new Set([...frag.querySelectorAll('h4, strong, .step-title, .callout-label')]
      .map((el) => cleanText(el.textContent).replace(/[:.]$/, ''))
      .filter((k) => k.length > 2 && k.length <= 40))].slice(0, 80).join(' · ')
    const size = writeJson(`topics/${subject.id}/${t.id}.json`, {
      subjectId: subject.id, id: t.id, title: t.title, group: t.group, order: i + 1, html,
    })
    if (size > 900_000) warn(`${subject.id}/${t.id}: ${size} bytes — close to Firestore's 1 MiB document limit`)
    outline.push({ id: t.id, title: t.title, group: t.group, headings, keywords })
  }
  return outline
}

/* ── Sheet 150 ───────────────────────────────────────────── */

/**
 * C++/Java in several legacy modules was machine-translated from Python and
 * does not compile. C++ is compiled; Java (same translator) is kept only if it
 * parses *and* its sibling C++ compiled.
 */
function readCode(sec, problemId) {
  const code = {}
  for (const box of sec.querySelectorAll('.code-content')) {
    const lang = normalizeLang(box.getAttribute('data-lang') ?? '')
    const pre = box.querySelector('pre')
    if (lang && pre) code[lang] = codeText(pre)
  }
  const cppOk = code.cpp ? cppCompiles(code.cpp) : true
  const javaOk = code.java ? javaParses(code.java) && cppOk : true
  for (const [lang, ok] of [['cpp', cppOk], ['java', javaOk]]) {
    if (code[lang] && !ok) { delete code[lang]; droppedByProblem.get(problemId).push(lang) }
  }
  return code
}

/**
 * Hand-written solutions in content-src/code/<problemId>/<naive|optimal>.<cpp|java|js|py>
 * fill in (or replace) languages from the legacy HTML. They must compile/parse.
 */
const CODE_DIR = 'content-src/code'
const EXT = { py: 'py', cpp: 'cpp', java: 'java', js: 'js' }
const CHECK = { cpp: cppErrors, java: javaErrors, js: jsErrors, py: () => '' }

function applyCodeOverrides(p) {
  const dir = path.join(CODE_DIR, p.id)
  if (!fs.existsSync(dir)) return
  for (const kind of ['naive', 'optimal']) {
    for (const [lang, ext] of Object.entries(EXT)) {
      const file = path.join(dir, `${kind}.${ext}`)
      if (!fs.existsSync(file)) continue
      if (!p[kind]) { warn(`${p.id}: ${kind}.${ext} has no matching section`); continue }
      const code = fs.readFileSync(file, 'utf8').replace(/\s+$/, '')
      const err = CHECK[lang](code)
      if (err) { warn(`${file} rejected: ${err.split('\n')[0]}`); continue }
      p[kind].code = { ...p[kind].code, [lang]: code }
    }
  }
}

function sectionHtml(sec, doc) {
  const clone = sec.cloneNode(true)
  for (const el of clone.querySelectorAll('.sec-title, .code-container, .complexity-row, details')) el.remove()
  return normalizeFragment(clone, doc)
}

function classify(title) {
  const t = title.toLowerCase()
  if (t.includes('problem statement')) return 'statement'
  if (t.includes('input') && t.includes('output')) return 'io'
  if (t.includes('constraint')) return 'constraints'
  if (t.includes('similar')) return 'similar'
  if (t.includes('complexity')) return /naive/.test(t) ? 'naiveComplexity' : 'optimalComplexity'
  if (t.includes('naive')) return 'naive'
  if (t.includes('understanding')) return 'understanding'
  if (t.includes('intuition')) return 'intuition'
  if (t.includes('approach') || t.includes('algorithm')) return 'approach'
  if (t.includes('optimized code') || t.includes('code (optimized)') || t.includes('standard solution')) return 'optimal'
  if (t.includes('variant') || t.includes('methods')) return 'variants'
  if (t.includes('takeaway') || t.includes('pattern')) return 'takeaway'
  return 'extra'
}

function extractProblem(card, doc, category) {
  const id = card.id
  const title = cleanText(card.querySelector('.problem-header h2')?.textContent)
  const lcLink = card.querySelector('.problem-meta a[href*="leetcode.com"]')
  const p = {
    id,
    lc: Number(id.replace('lc-', '')),
    slug: lcLink?.getAttribute('href').match(/problems\/([^/]+)/)?.[1] ?? slug(title),
    title,
    difficulty: cleanText(card.querySelector('.problem-meta .diff-badge')?.textContent) || 'Medium',
    category,
    leetcodeUrl: lcLink?.getAttribute('href') ?? '',
    youtubeUrl: '',
  }
  const extra = []
  for (const sec of [...card.children].filter((c) => c.classList.contains('sec-block'))) {
    const secTitle = cleanText(sec.querySelector('.sec-title')?.textContent).replace(/^\d+\.\s*/, '')
    const kind = classify(secTitle)
    const chips = [...sec.querySelectorAll('.c-badge')].map((b) => cleanText(b.textContent))
    switch (kind) {
      case 'naive':
      case 'optimal':
        p[kind] = { ...(p[kind] ?? {}), title: secTitle, html: sectionHtml(sec, doc), code: readCode(sec, id) }
        break
      case 'naiveComplexity':
        p.naive = { ...(p.naive ?? { title: 'Naive Solution', html: '', code: {} }), complexity: chips }
        break
      case 'optimalComplexity':
        p.optimal = { ...(p.optimal ?? { title: 'Optimized Code', html: '', code: {} }), complexity: chips }
        break
      case 'similar':
        p.similar = [...sec.querySelectorAll('.s150-similar-link')].map((a) => ({
          title: cleanText(a.querySelector('.sim-name')?.textContent),
          difficulty: cleanText(a.querySelector('.sim-diff')?.textContent),
          lc: Number(a.querySelector('.sim-lc')?.textContent.replace(/\D/g, '')) || null,
          url: a.getAttribute('href') ?? '',
        }))
        break
      case 'extra':
        extra.push({ title: secTitle, html: sectionHtml(sec, doc) })
        break
      default:
        p[kind] = sectionHtml(sec, doc)
    }
  }
  if (extra.length) p.extra = extra
  if (!p.statement) warn(`sheet-150/${id}: missing problem statement`)
  if (!p.optimal || !Object.keys(p.optimal.code ?? {}).length) warn(`sheet-150/${id}: missing optimized code`)
  return p
}

function extractSheet150() {
  const byId = new Map()
  for (const file of SHEET_150_FILES) {
    const doc = load(`sheet_150/${file}`)
    // Sidebar: section title → problem ids
    const sectionOf = new Map()
    let section = ''
    for (const el of doc.querySelectorAll('.nav-section-title, a.nav-item')) {
      if (el.classList.contains('nav-section-title')) { section = cleanText(el.textContent); continue }
      const href = el.getAttribute('href') ?? ''
      if (href.startsWith('#lc-')) sectionOf.set(href.slice(1), section)
    }
    for (const card of doc.querySelectorAll('.problem-card')) {
      const sec = sectionOf.get(card.id) ?? ''
      const cat = SHEET_150_CATEGORIES.find((c) => /advanced graphs/i.test(sec) ? c.id === 'advanced-graphs' : c.match.test(sec))
      const category = cat?.id ?? byId.get(card.id)?.category
      if (!category) { warn(`sheet-150/${card.id}: no category for section "${sec}" in ${file}`); continue }
      droppedByProblem.set(card.id, [])
      byId.set(card.id, extractProblem(card, doc, category))
    }
  }

  const outline = []
  for (const cat of SHEET_150_CATEGORIES) {
    // Keep the legacy sidebar order within a category.
    const problems = [...byId.values()].filter((p) => p.category === cat.id)
    problems.forEach((p, i) => { p.order = i + 1; applyCodeOverrides(p) })
    const size = writeJson(`problems/${cat.id}.json`, { categoryId: cat.id, title: cat.title, problems })
    if (size > 900_000) warn(`sheet-150/${cat.id}: ${size} bytes — split before seeding`)
    outline.push({
      id: cat.id,
      title: cat.title,
      group: '',
      problems: problems.map(({ id, lc, title, difficulty }) => ({ id, lc, title, difficulty })),
    })
  }
  return outline
}

/* ── Main ────────────────────────────────────────────────── */

fs.rmSync(BUILD_DIR, { recursive: true, force: true })

const catalog = {
  version: 1,
  generatedAt: new Date().toISOString(),
  subjects: SUBJECTS.map(({ source, ...meta }) => {
    const topics = meta.kind === 'problems' ? extractSheet150() : extractNotes({ ...meta, source })
    const itemCount = meta.kind === 'problems'
      ? topics.reduce((n, t) => n + t.problems.length, 0)
      : topics.length
    return { ...meta, itemCount, topics }
  }),
}
const catalogSize = writeJson('catalog.json', catalog)
for (const [id, langs] of droppedByProblem) if (langs.length) report.droppedCode.push(`${id}: ${langs.join(', ')}`)
const droppedCount = [...droppedByProblem.values()].reduce((n, l) => n + l.length, 0)

for (const s of catalog.subjects) {
  console.log(`${s.id.padEnd(20)} ${String(s.topics.length).padStart(3)} topics  ${String(s.itemCount).padStart(4)} items`)
}
console.log(`catalog.json ${(catalogSize / 1024).toFixed(0)} KB`)
console.log(`\nDropped ${droppedCount} C++/Java snippets that fail to compile/parse (see content-src/extract-report.json).`)
if (report.warnings.length) console.log(`\n${report.warnings.length} warnings:\n  ` + report.warnings.join('\n  '))
fs.writeFileSync('content-src/extract-report.json', JSON.stringify(report, null, 2))
const OLD_DIR = `${OUT_DIR}.old`
fs.rmSync(OLD_DIR, { recursive: true, force: true })
if (fs.existsSync(OUT_DIR)) fs.renameSync(OUT_DIR, OLD_DIR)
fs.renameSync(BUILD_DIR, OUT_DIR)
fs.rmSync(OLD_DIR, { recursive: true, force: true })
saveCache()
