/* ============================================================
   Content tree helpers — text extraction and lookups over
   structured content, used by the study kit, read-time tracking
   and anchors. No DOM needed (works the same in a native app).
   ============================================================ */

import type { Content, ContentNode, NodeType } from '@schema/content'

/** Concatenated text of a node (like DOM textContent: code included, <br> ignored). */
export function textOf(node: ContentNode | Content | undefined): string {
  if (!node) return ''
  if (Array.isArray(node)) return node.map(textOf).join('')
  if (node.type === 'text' || node.type === 'codeBlock') return node.value ?? ''
  if (node.type === 'qaQuestion' || !node.children) return node.children ? node.children.map(textOf).join('') : ''
  return node.children.map(textOf).join('')
}

/** All readable text of a fragment. */
export const plainText = (content: Content) => textOf(content)

export interface Visit {
  node: ContentNode
  /** ancestors, outermost first */
  path: ContentNode[]
}

/** Every node in document order (pre-order), with its ancestors. */
export function* walk(content: Content, path: ContentNode[] = []): Generator<Visit> {
  for (const node of content) {
    yield { node, path }
    if (node.children) yield* walk(node.children, [...path, node])
  }
}

export function findAll(content: Content, pred: (v: Visit) => boolean): Visit[] {
  const out: Visit[] = []
  for (const v of walk(content)) if (pred(v)) out.push(v)
  return out
}

export function first(content: Content, pred: (v: Visit) => boolean): Visit | undefined {
  for (const v of walk(content)) if (pred(v)) return v
  return undefined
}

export const hasAncestor = (v: Visit, types: NodeType[]) => v.path.some((a) => types.includes(a.type))
export const isType = (...types: NodeType[]) => (v: Visit) => types.includes(v.node.type)

export interface Anchor {
  /** the node that carries the id: a section heading, or a tab panel */
  node: ContentNode
  id: string
  title: string
  /** the content belonging to the anchor */
  body: ContentNode
}

/**
 * Section anchors of a topic (`sec-0`, `sec-1`, …):
 *   1. the h3 heading of every titled section, else
 *   2. top-level h3 headings (outside cards, callouts, tabs, Q&A), else
 *   3. the panels of a tabbed topic.
 */
export function sectionAnchors(content: Content): Anchor[] {
  const make = (items: { node: ContentNode; title: string; body: ContentNode }[]) =>
    items.map((it, i) => ({ ...it, id: `sec-${i}` }))

  const sections = findAll(content, (v) => v.node.type === 'section')
    .map((v) => ({ section: v.node, heading: v.node.children?.find((c) => c.type === 'heading' && c.level === 3) }))
    .filter((s) => s.heading)
  if (sections.length) return make(sections.map((s) => ({ node: s.heading!, title: textOf(s.heading), body: s.section })))

  const plain = findAll(content, (v) => v.node.type === 'heading' && v.node.level === 3 && !hasAncestor(v, ['card', 'callout', 'tabPanel', 'qa']))
  if (plain.length) {
    const heads = new Set(plain.map((v) => v.node))
    // A plain heading's body: its following siblings, up to the next anchored heading.
    return make(plain.map((v) => {
      const siblings = v.path.length ? v.path[v.path.length - 1].children ?? [] : content
      const start = siblings.indexOf(v.node)
      const rest: ContentNode[] = []
      for (let i = start + 1; i < siblings.length && !heads.has(siblings[i]); i++) rest.push(siblings[i])
      return { node: v.node, title: textOf(v.node), body: { type: 'group', children: rest } as ContentNode }
    }))
  }

  const panels = findAll(content, isType('tabPanel'))
  return make(panels.map((v) => ({ node: v.node, title: v.node.label || textOf(v.node).slice(0, 40), body: v.node })))
}
