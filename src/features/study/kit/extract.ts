/* ============================================================
   STUDY KIT EXTRACTION — builds revision aids from a topic's
   structured content (schema/content.ts), instantly and offline:

     outline   side headings (the topic's section anchors)
     notes     quick notes: the key sentence(s) of every section
     terms     key terms (bold phrases, most frequent first)
     remember  definitions, notes and warnings from callouts

   Section ids (`sec-N`) match the ids ContentView gives the
   headings (both use sectionAnchors).
   ============================================================ */

import type { Content, ContentNode } from '@schema/content'
import { cleanText } from '@/features/voice/speech'
import { findAll, first, hasAncestor, isType, sectionAnchors, textOf, type Visit } from '@/features/content/query'

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

const text = (n: ContentNode | Content | undefined) => cleanText(textOf(n))

function firstSentence(s: string, max = 200) {
  const m = s.match(/^(.+?[.!?])(\s|$)/)
  const out = (m ? m[1] : s).trim()
  return out.length > max ? `${out.slice(0, max - 1).trimEnd()}…` : out
}

const inCode = (v: Visit) => v.node.type === 'codeBlock' || hasAncestor(v, ['codeBlock'])
const within = (node: ContentNode) => node.children ?? []

export function buildStudyKit(content: Content): StudyKit {
  const lead = firstSentence(text(first(content, (v) => v.node.type === 'paragraph' && v.node.variant === 'lead')?.node), 260)

  const sections: KitSection[] = sectionAnchors(content).map((a) => {
    const block = [a.body]
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
    for (const c of findAll(block, (v) => v.node.type === 'callout' && v.node.variant === 'def')) {
      add(text(first(within(c.node), isType('paragraph'))?.node ?? c.node))
    }
    const para = findAll(block, isType('paragraph'))
      .find((v) => !inCode(v) && !hasAncestor(v, ['callout', 'card']) && text(v.node).length > 30)
    if (para) add(text(para.node))
    const items = findAll(block, (v) =>
      !inCode(v) && (v.node.type === 'card' || v.node.type === 'listItem' || v.node.type === 'stepDesc' ||
        (v.node.type === 'tableRow' && v.path[v.path.length - 1]?.type === 'tableBody')),
    ).slice(0, 8)
    for (const v of items) {
      if (points.length >= 4) break
      if (v.node.type === 'card') {
        const head = text(first(within(v.node), (x) => (x.node.type === 'heading' && (x.node.level === 3 || x.node.level === 4)) || x.node.type === 'strong' || x.node.type === 'calloutLabel')?.node).replace(/[:.]$/, '')
        add(text(first(within(v.node), isType('paragraph'))?.node ?? v.node), head)
      } else if (v.node.type === 'tableRow') {
        const cells = within(v.node).filter((c) => c.type === 'tableCell').map((c) => text(c))
        if (cells.length >= 2) add(cells.slice(1).join(' — '), cells[0])
      } else if (!hasAncestor(v, ['card'])) add(text(v.node))
    }
    return { id: a.id, title: cleanText(a.title).replace(/\.$/, ''), points: points.slice(0, 4) }
  })

  // Key terms: bold phrases, ranked by how often they appear.
  const counts = new Map<string, { term: string; n: number; first: number }>()
  findAll(content, isType('strong')).forEach((v, i) => {
    if (inCode(v)) return
    const term = text(v.node).replace(/[:.,;]+$/, '')
    if (term.length < 2 || term.length > 48 || /^\d+$/.test(term)) return
    const k = term.toLowerCase()
    const e = counts.get(k)
    counts.set(k, e ? { ...e, n: e.n + 1 } : { term, n: 1, first: i })
  })
  const terms = [...counts.values()].sort((a, b) => b.n - a.n || a.first - b.first).slice(0, 18).map((t) => t.term)

  const remember: KitCallout[] = []
  for (const v of findAll(content, isType('callout'))) {
    if (remember.length >= 10) break
    const kind = (['def', 'note', 'warn', 'good', 'bad', 'example'] as const).find((k) => v.node.variant === k)
    if (!kind || kind === 'example') continue
    const labelNode = first(within(v.node), isType('calloutLabel'))?.node
    const label = text(labelNode).replace(/[:.]$/, '')
    const rest = { ...v.node, children: within(v.node).filter((c) => c !== labelNode) }
    const t = firstSentence(text(rest), 240)
    if (t.length > 30) remember.push({ kind, label, text: t })
  }

  return { lead, sections, terms, remember, words: textOf(content).trim().split(/\s+/).length }
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
