/* ============================================================
   CONTENT SCHEMA — study content as structured blocks.

   Every topic (and every rich field of a problem) is a tree of
   typed nodes: sections, headings, paragraphs, lists, code blocks,
   callouts, tables, cards, … down to inline text marks. The web
   app renders each type with one reusable component
   (src/features/content/); a native app can do the same.

   In Firestore a tree is stored FLAT — an ordered array of nodes,
   each pointing to its parent by index — because Firestore limits
   nesting to 20 levels and content nests deeper than that as a
   tree. `flatten()` / `unflatten()` convert between the two.

   Firestore layout (content is public, read-only; see firestore.rules):
     meta/content                          ContentMeta  (version — drives client caching)
     catalog/current                       Catalog      (subjects + topic outlines, for navigation/search)
     subjects/{subjectId}                  SubjectDoc
     subjects/{subjectId}/topics/{topicId} TopicDocFlat
     subjects/{subjectId}/problems/{id}    ProblemDocFlat (problem sheets)
   ============================================================ */

export const CONTENT_SCHEMA = 1

/* ── Node types ──────────────────────────────────────────── */

/** Inline nodes: live inside paragraphs, headings, list items, cells… */
export type InlineType =
  | 'text' | 'strong' | 'em' | 'i' | 'u' | 'code' | 'sup' | 'sub' | 'small' | 'span'
  | 'link' | 'br' | 'icon'

/** Block nodes. */
export type BlockType =
  | 'section'                               // a titled section (first child is its heading)
  | 'heading'                               // level 3 | 4 | 5
  | 'paragraph'                             // variant: lead | muted | mono
  | 'group'                                 // a plain container; variant: muted | mono
  | 'list' | 'listItem'                     // ordered?
  | 'codeBlock'                             // lang, caption, code
  | 'callout' | 'calloutLabel'              // variant: def | example | note | warn | good | bad | plain
  | 'grid' | 'card'                         // cols: 2 | 3
  | 'table' | 'tableHead' | 'tableBody' | 'tableRow' | 'tableCell'
  | 'flow' | 'flowNode' | 'flowArrow'       // box-and-arrow diagrams
  | 'step' | 'stepNum' | 'stepBody' | 'stepTitle' | 'stepDesc'
  | 'chips' | 'chip'
  | 'kv' | 'kvKey' | 'kvValue'              // key → value rows
  | 'formula'
  | 'bits' | 'bit'                          // bit diagrams
  | 'gantt' | 'ganttBlock' | 'ganttScale'   // scheduling charts
  | 'tabs' | 'tabPanel'                     // label
  | 'qa' | 'qaQuestion'                     // question / answer disclosure
  | 'svg'                                   // a vector diagram (markup)
  | 'footer'

export type NodeType = InlineType | BlockType

export interface ContentNode {
  type: NodeType
  children?: ContentNode[]
  /** text: the characters · codeBlock: the source code · svg: the inner markup */
  value?: string
  /** heading level (3–5) */
  level?: number
  /** paragraph / group / callout variant */
  variant?: string
  /** list: ordered? */
  ordered?: boolean
  /** codeBlock language: py | cpp | java | js | sql | bash | json | … */
  lang?: string
  /** codeBlock caption, tabPanel label */
  label?: string
  /** link target */
  href?: string
  /** icon name (Tabler icons, e.g. "ti-bolt") */
  icon?: string
  /** grid columns */
  cols?: number
  /** table cell */
  header?: boolean
  colspan?: number
  rowspan?: number
  /** layout-only inline style kept from the source (flex/grid sizing) */
  style?: string
  /** inline variant of a normally block-level node (e.g. a chip inside a sentence) */
  inline?: boolean
  /** svg: attributes of the <svg> element (viewBox, width, height) */
  attrs?: Record<string, string>
}

/** A rich-text value: the top-level nodes of a fragment. */
export type Content = ContentNode[]

/* ── Flat encoding for Firestore ─────────────────────────── */

/** A node without children plus the index of its parent (−1 = top level), in document order. */
export type FlatNode = Omit<ContentNode, 'children'> & { parent: number }
export type FlatContent = FlatNode[]

export function flatten(content: Content): FlatContent {
  const out: FlatContent = []
  const walk = (nodes: ContentNode[], parent: number) => {
    for (const { children, ...rest } of nodes) {
      const index = out.push({ ...rest, parent }) - 1
      if (children?.length) walk(children, index)
    }
  }
  walk(content, -1)
  return out
}

export function unflatten(flat: FlatContent): Content {
  const nodes: ContentNode[] = flat.map((f) => {
    const node: ContentNode & { parent?: number } = { ...f }
    delete node.parent
    return node
  })
  const roots: ContentNode[] = []
  flat.forEach((f, i) => {
    if (f.parent < 0) roots.push(nodes[i])
    else (nodes[f.parent].children ??= []).push(nodes[i])
  })
  return roots
}

/* ── Documents ───────────────────────────────────────────── */

export interface ContentMeta {
  /** changes whenever any content changes — clients drop their cache when it does */
  version: string
  schema: number
  generatedAt: string
  subjects: number
  topics: number
  problems: number
}

export interface SubjectDoc {
  id: string
  title: string
  description: string
  icon: string
  category?: string
  kind: 'notes' | 'problems'
  order: number
  itemCount: number
  topicCount: number
}

export interface TopicDocFlat {
  subjectId: string
  id: string
  title: string
  group: string
  order: number
  content: FlatContent
  schema: number
}

export interface SolutionFlat {
  title: string
  content: FlatContent
  code: Partial<Record<'py' | 'cpp' | 'java' | 'js', string>>
  complexity?: string[]
}

/** Rich problem fields stored as flat content. */
export const PROBLEM_RICH_FIELDS = [
  'statement', 'io', 'constraints', 'understanding', 'intuition', 'approach', 'variants', 'takeaway',
] as const
export type ProblemRichField = (typeof PROBLEM_RICH_FIELDS)[number]
