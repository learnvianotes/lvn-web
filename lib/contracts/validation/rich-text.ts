// Copied from lvn-backend contracts/src/validation/rich-text.ts by scripts/contracts-sync.mjs — do not edit here.
import { z } from 'zod'

/**
 * Rich text inside cards: the subset of Tiptap / ProseMirror JSON that web and mobile editors produce and the API
 * stores (§4.1 "the editor persists Tiptap JSON per card"). Anything outside it — unknown nodes or marks, script
 * links, oversized text — fails validation; unknown attributes are dropped.
 */

export const RICH_TEXT_LIMITS = {
  /** Characters in one text node */
  textNode: 10_000,
  /** Nesting of lists inside lists */
  listDepth: 5,
  linkLength: 2_048,
} as const

const SAFE_PROTOCOLS = new Set(['http:', 'https:', 'mailto:'])

/** Only web and mail links: no `javascript:`, `data:` or relative URLs. */
export const safeHref = z
  .string()
  .trim()
  .min(1)
  .max(RICH_TEXT_LIMITS.linkLength)
  .refine((href) => {
    try {
      return SAFE_PROTOCOLS.has(new URL(href).protocol)
    } catch {
      return false
    }
  }, 'Links must start with http://, https:// or mailto:')

const simpleMark = <T extends string>(type: T) => z.object({ type: z.literal(type) })

export const markSchema = z.discriminatedUnion('type', [
  simpleMark('bold'),
  simpleMark('italic'),
  simpleMark('underline'),
  simpleMark('strike'),
  simpleMark('code'),
  simpleMark('highlight'),
  simpleMark('subscript'),
  simpleMark('superscript'),
  z.object({ type: z.literal('link'), attrs: z.object({ href: safeHref }) }),
])
export type Mark = z.infer<typeof markSchema>

export const textNodeSchema = z.object({
  type: z.literal('text'),
  text: z.string().min(1).max(RICH_TEXT_LIMITS.textNode),
  marks: z.array(markSchema).max(9).optional(),
})

export const hardBreakSchema = z.object({ type: z.literal('hardBreak') })

/** Text and line breaks: what a paragraph, heading, table cell or checklist item holds. */
export const inlineSchema = z.array(z.discriminatedUnion('type', [textNodeSchema, hardBreakSchema])).max(2_000)
export type Inline = z.infer<typeof inlineSchema>

export const paragraphSchema = z.object({ type: z.literal('paragraph'), content: inlineSchema.optional() })

export interface ListItemNode {
  type: 'listItem'
  content: BlockNode[]
}
export interface ListNode {
  type: 'bulletList' | 'orderedList'
  attrs?: { start?: number }
  content: ListItemNode[]
}
export type BlockNode = z.infer<typeof paragraphSchema> | ListNode

const listItemSchema: z.ZodType<ListItemNode> = z.object({
  type: z.literal('listItem'),
  get content() {
    return z.array(blockSchema).min(1).max(200)
  },
})

const bulletListSchema: z.ZodType<ListNode> = z.object({
  type: z.literal('bulletList'),
  content: z.array(listItemSchema).min(1).max(500),
})

const orderedListSchema: z.ZodType<ListNode> = z.object({
  type: z.literal('orderedList'),
  attrs: z.object({ start: z.number().int().min(0).max(1_000_000).optional() }).optional(),
  content: z.array(listItemSchema).min(1).max(500),
})

const blockSchema: z.ZodType<BlockNode> = z.union([paragraphSchema, bulletListSchema, orderedListSchema])

/** How deeply lists nest in a document. */
export function listDepth(nodes: readonly BlockNode[]): number {
  let max = 0
  for (const node of nodes) {
    if (node.type === 'paragraph') continue
    for (const item of node.content) max = Math.max(max, 1 + listDepth(item.content))
  }
  return max
}

/** A rich text document: paragraphs and (nested) lists. */
export const docSchema = z
  .object({ type: z.literal('doc'), content: z.array(blockSchema).max(1_000) })
  .refine((doc) => listDepth(doc.content) <= RICH_TEXT_LIMITS.listDepth, `Lists can nest at most ${RICH_TEXT_LIMITS.listDepth} levels deep`)
export type Doc = z.infer<typeof docSchema>

/** Plain text of inline content (search, read aloud, outlines). */
export function inlineText(inline: Inline | undefined): string {
  return (inline ?? []).map((n) => (n.type === 'text' ? n.text : '\n')).join('')
}

/** Plain text of a document, one line per paragraph or list item. */
export function docText(doc: { content: readonly BlockNode[] } | undefined): string {
  const lines: string[] = []
  const walk = (nodes: readonly BlockNode[]) => {
    for (const node of nodes) {
      if (node.type === 'paragraph') lines.push(inlineText(node.content))
      else for (const item of node.content) walk(item.content)
    }
  }
  walk(doc?.content ?? [])
  return lines.join('\n')
}
