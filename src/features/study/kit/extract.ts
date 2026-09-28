/* ============================================================
   STUDY KIT EXTRACTION — builds revision aids from a topic's
   normalized HTML (see scripts/content/sanitize.mjs), instantly
   and offline:

     outline   side headings (each `section.block > h3`)
     notes     quick notes: the key sentence(s) of every section
     terms     key terms (bold phrases, most frequent first)
     remember  definitions, notes and warnings from callouts

   Section ids (`sec-N`) match the ids Prose gives the headings
   (both use sectionHeadings).
   ============================================================ */

import { cleanText } from '@/features/voice/speech'

export interface KitSection {
  id: string
  title: string
  points: string[]
}

export interface KitCallout {
  kind: 'def' | 'note' | 'warn' | 'good' | 'bad' | 'example'
  label: string
  text: string
}

export interface StudyKit {
  lead: string
  sections: KitSection[]
  terms: string[]
  remember: KitCallout[]
  words: number
}

/**
 * Section anchors: each `section.block > h3`; otherwise top-level h2/h3;
 * otherwise the panels of a tabbed topic (titled by their tab label).
 */
export function sectionHeadings(root: ParentNode): HTMLElement[] {
  const blocks = [...root.querySelectorAll<HTMLElement>('section.block > h3')]
  if (blocks.length) return blocks
  const plain = [...root.querySelectorAll<HTMLElement>('h2, h3')].filter((h) => !h.closest('.card, .callout, figure, .tab-panel, details'))
  if (plain.length) return plain
  return [...root.querySelectorAll<HTMLElement>('.tab-panel')]
}

const headingTitle = (h: Element) => h.getAttribute('data-label') || text(h)

/** The content belonging to a heading: its block, or the siblings up to the next heading. */
function sectionBody(h: Element, all: Element[]): Element {
  if (h.matches('.tab-panel')) return h
  if (h.parentElement?.matches('section.block')) return h.parentElement
  const box = h.ownerDocument.createElement('div')
  for (let n = h.nextElementSibling; n && !all.includes(n); n = n.nextElementSibling) box.appendChild(n.cloneNode(true))
  return box
}

const text = (el: Element | null | undefined) => cleanText(el?.textContent ?? '')

function firstSentence(s: string, max = 200) {
  const m = s.match(/^(.+?[.!?])(\s|$)/)
  const out = (m ? m[1] : s).trim()
  return out.length > max ? `${out.slice(0, max - 1).trimEnd()}…` : out
}

const inCode = (el: Element) => Boolean(el.closest('figure.code, pre'))

export function buildStudyKit(html: string): StudyKit {
  const doc = new DOMParser().parseFromString(`<!doctype html><html><body>${html}</body></html>`, 'text/html')
  const body = doc.body

  const lead = firstSentence(text(body.querySelector('.lead')), 260)

  const headings = sectionHeadings(body)
  const sections: KitSection[] = headings.map((h, i) => {
    const block = sectionBody(h, headings)
    const points: string[] = []
    const add = (s: string, prefix = '') => {
      const sentence = firstSentence(s)
      if (sentence.length <= 12 || (sentence.endsWith('?') && sentence.length < 60)) return
      if (prefix.endsWith('?') || prefix.length > 40) prefix = ''
      const p = prefix && !sentence.toLowerCase().startsWith(prefix.toLowerCase()) ? `${prefix}: ${sentence}` : sentence
      // Skip repeats (a card often restates the paragraph above it).
      const low = sentence.toLowerCase()
      if (points.some((q) => q.toLowerCase().includes(low) || low.includes(q.toLowerCase().replace(/^[^:]+: /, '')))) return
      points.push(p)
    }
    // Definitions first, then the opening paragraph, then cards / list items / table rows.
    block.querySelectorAll('.callout--def').forEach((c) => add(text(c.querySelector('p') ?? c)))
    const para = [...block.querySelectorAll('p')].find((p) => !inCode(p) && !p.closest('.callout, .card') && text(p).length > 30)
    if (para) add(text(para))
    for (const el of [...block.querySelectorAll('.card, li, .step-desc, tbody tr')].filter((e) => !inCode(e)).slice(0, 8)) {
      if (points.length >= 4) break
      if (el.classList.contains('card')) {
        const head = text(el.querySelector('h3, h4, strong, .callout-label')).replace(/[:.]$/, '')
        add(text(el.querySelector('p') ?? el), head)
      } else if (el.tagName === 'TR') {
        const cells = [...el.children].map((c) => text(c))
        if (cells.length >= 2) add(cells.slice(1).join(' — '), cells[0])
      } else if (!el.closest('.card')) add(text(el))
    }
    return { id: `sec-${i}`, title: headingTitle(h).replace(/\.$/, ''), points: points.slice(0, 4) }
  })

  // Key terms: bold phrases, ranked by how often they appear.
  const counts = new Map<string, { term: string; n: number; first: number }>()
  ;[...body.querySelectorAll('strong, b')].forEach((el, i) => {
    if (inCode(el)) return
    const term = text(el).replace(/[:.,;]+$/, '')
    if (term.length < 2 || term.length > 48 || /^\d+$/.test(term)) return
    const k = term.toLowerCase()
    const e = counts.get(k)
    counts.set(k, e ? { ...e, n: e.n + 1 } : { term, n: 1, first: i })
  })
  const terms = [...counts.values()].sort((a, b) => b.n - a.n || a.first - b.first).slice(0, 18).map((t) => t.term)

  const remember: KitCallout[] = []
  body.querySelectorAll('.callout').forEach((c) => {
    if (remember.length >= 10) return
    const kind = (['def', 'note', 'warn', 'good', 'bad', 'example'] as const).find((k) => c.classList.contains(`callout--${k}`))
    if (!kind || kind === 'example') return
    const label = text(c.querySelector('.callout-label')).replace(/[:.]$/, '')
    const clone = c.cloneNode(true) as Element
    clone.querySelector('.callout-label')?.remove()
    const t = firstSentence(text(clone), 240)
    if (t.length > 30) remember.push({ kind, label, text: t })
  })

  return { lead, sections, terms, remember, words: (body.textContent ?? '').trim().split(/\s+/).length }
}

/** Plain-text recap (for read-aloud and "copy notes"). */
export function recapText(title: string, kit: StudyKit) {
  const lines = [`${title} — quick notes`, '']
  if (kit.lead) lines.push(kit.lead, '')
  for (const s of kit.sections) {
    if (!s.points.length) continue
    lines.push(`## ${s.title}`, ...s.points.map((p) => `- ${p}`), '')
  }
  if (kit.terms.length) lines.push(`Key terms: ${kit.terms.join(', ')}`)
  return lines.join('\n')
}
