import type { JSONContent } from '@tiptap/core'
import { CardType } from '@/lib/contracts/domain/enums'
import { parseCardContent, type CardAnchor } from '@/lib/contracts/validation'

/**
 * The editor holds a whole note as one Tiptap document whose top-level nodes are cards (lvn-backend spec §4.1: "one
 * extension per card type"); the API stores cards. These functions convert between the two. Every card node carries
 * the card's id, its last saved position and revision, so a save can tell what changed (./save.ts).
 */

export interface DraftCard {
  id: string
  type: CardType
  content: unknown
}

export interface StoredCard extends DraftCard {
  position: string
  revision: number
}

/**
 * Card node names in the editor, by card type. Media cards (image, video, audio, file) share `mediaCard`, which keeps
 * the type in an attribute; types without an editor node of their own are kept as `opaqueCard`.
 */
export const NODE_OF: Partial<Record<CardType, string>> = {
  text: 'textCard',
  heading: 'headingCard',
  quote: 'quoteCard',
  callout: 'calloutCard',
  checklist: 'checklistCard',
  code: 'codeCard',
  markdown: 'markdownCard',
  diagram: 'diagramCard',
  table: 'tableCard',
  question: 'questionCard',
  quiz: 'quizCard',
  flashcard: 'flashcardCard',
}

const TYPE_OF: Record<string, CardType> = Object.fromEntries(Object.entries(NODE_OF).map(([type, node]) => [node, type as CardType]))

const EMPTY_PARAGRAPH: JSONContent = { type: 'paragraph' }
const blocks = (doc: { content?: JSONContent[] } | undefined): JSONContent[] => (doc?.content?.length ? doc.content : [EMPTY_PARAGRAPH])
const textOf = (node: JSONContent): string => (node.content ?? []).map((n) => n.text ?? '').join('')
const plain = (s: string): JSONContent[] => (s ? [{ type: 'text', text: s }] : [])

/**
 * Attributes every card node has; `position` and `revision` are what the server last stored, `anchor` where the card
 * came from in a PDF of the note (lvn-backend ADR-0040) — kept through every edit of the card.
 */
export const cardAttrs = (card: { id: string; position?: string | null; revision?: number | null; content?: unknown }) => ({
  id: card.id,
  position: card.position ?? null,
  revision: card.revision ?? null,
  anchor: ((card.content as { anchor?: CardAnchor } | null)?.anchor ?? null) as CardAnchor | null,
})

export function cardToNode(card: StoredCard | (DraftCard & { position?: string | null; revision?: number | null })): JSONContent {
  const attrs = cardAttrs(card)
  const c = (card.content ?? {}) as Record<string, unknown>
  switch (card.type) {
    case 'text':
      return { type: 'textCard', attrs, content: blocks(c.doc as never) }
    case 'heading':
      return { type: 'headingCard', attrs: { ...attrs, level: c.level ?? 1 }, content: (c.content as JSONContent[]) ?? [] }
    case 'quote':
      return { type: 'quoteCard', attrs: { ...attrs, attribution: c.attribution ?? '' }, content: blocks(c.doc as never) }
    case 'callout':
      return { type: 'calloutCard', attrs: { ...attrs, variant: c.variant ?? 'note', title: c.title ?? '' }, content: blocks(c.doc as never) }
    case 'checklist': {
      const items = (c.items as { id: string; checked: boolean; content: JSONContent[] }[] | undefined) ?? []
      const nodes = items.length ? items : [{ id: newCardId(), checked: false, content: [] }]
      return { type: 'checklistCard', attrs, content: nodes.map((i) => ({ type: 'checkItem', attrs: { id: i.id, checked: i.checked }, content: i.content ?? [] })) }
    }
    case 'code':
      return { type: 'codeCard', attrs: { ...attrs, language: c.language ?? '', filename: c.filename ?? '' }, content: plain(String(c.code ?? '')) }
    case 'markdown':
      return { type: 'markdownCard', attrs, content: plain(String(c.source ?? '')) }
    case 'diagram':
      return { type: 'diagramCard', attrs: { ...attrs, caption: c.caption ?? null }, content: plain(String(c.source ?? '')) }
    case 'table':
    case 'question':
    case 'quiz':
    case 'flashcard':
      return { type: NODE_OF[card.type]!, attrs: { ...attrs, data: card.content } }
    case 'image':
    case 'video':
    case 'audio':
    case 'file':
      return { type: 'mediaCard', attrs: { ...attrs, cardType: card.type, data: card.content ?? null } }
    default:
      return { type: 'opaqueCard', attrs: { ...attrs, cardType: card.type, data: card.content } }
  }
}

export function cardsToDoc(cards: StoredCard[]): JSONContent {
  return { type: 'doc', content: cards.length ? cards.map(cardToNode) : [cardToNode({ id: newCardId(), type: 'text', content: { doc: { type: 'doc', content: [] } } })] }
}

/** Card content from a card node, in the shape @lvn/contracts validates (not yet normalised). */
export function nodeToCard(node: JSONContent): DraftCard | null {
  const card = nodeContent(node)
  const anchor = node.attrs?.anchor as CardAnchor | null | undefined
  if (!card || !anchor || !card.content || typeof card.content !== 'object') return card
  return { ...card, content: { ...(card.content as object), anchor } }
}

function nodeContent(node: JSONContent): DraftCard | null {
  const a = (node.attrs ?? {}) as Record<string, unknown>
  const id = a.id as string | null
  if (!id) return null
  const doc = { type: 'doc', content: (node.content ?? []).filter((n) => n.type === 'paragraph' || n.type === 'bulletList' || n.type === 'orderedList') }
  switch (node.type) {
    case 'textCard':
      return { id, type: 'text', content: { doc } }
    case 'headingCard':
      return { id, type: 'heading', content: { level: a.level ?? 1, content: node.content ?? [] } }
    case 'quoteCard':
      return { id, type: 'quote', content: { doc, ...(a.attribution ? { attribution: a.attribution } : {}) } }
    case 'calloutCard':
      return { id, type: 'callout', content: { variant: a.variant ?? 'note', ...(a.title ? { title: a.title } : {}), doc } }
    case 'checklistCard':
      return {
        id,
        type: 'checklist',
        content: { items: (node.content ?? []).map((i) => ({ id: String(i.attrs?.id ?? newCardId()), checked: !!i.attrs?.checked, content: i.content ?? [] })) },
      }
    case 'codeCard':
      return { id, type: 'code', content: { language: String(a.language ?? ''), code: textOf(node), ...(a.filename ? { filename: a.filename } : {}) } }
    case 'markdownCard':
      return { id, type: 'markdown', content: { source: textOf(node) } }
    case 'diagramCard':
      return { id, type: 'diagram', content: { syntax: 'mermaid', source: textOf(node), ...(a.caption ? { caption: a.caption } : {}) } }
    case 'opaqueCard':
    case 'mediaCard':
      return { id, type: a.cardType as CardType, content: a.data }
    default: {
      const type = node.type ? TYPE_OF[node.type] : undefined
      return type ? { id, type, content: a.data } : null
    }
  }
}

/** The cards of an editor document, in order. */
export function docToCards(doc: JSONContent): DraftCard[] {
  return (doc.content ?? []).map(nodeToCard).filter((c): c is DraftCard => c !== null)
}

/** Card content as the API will store it (validated, unknown attributes dropped); null with the reason if invalid. */
export function normalise(card: DraftCard): { ok: true; content: unknown } | { ok: false; message: string } {
  return parseCardContent(card.type, card.content)
}

/** A stable text for comparing contents: JSON with sorted keys. */
export function contentKey(content: unknown): string {
  return JSON.stringify(content, (_, v: unknown) => (v && typeof v === 'object' && !Array.isArray(v) ? Object.fromEntries(Object.entries(v).sort(([a], [b]) => (a < b ? -1 : 1))) : v))
}

/**
 * A new card id: a UUIDv7 (lvn-backend §4.6), made here so cards created offline keep their id. Built on
 * crypto.getRandomValues, which — unlike crypto.randomUUID — also works on plain-HTTP origins (the dev machine's
 * address, the local environment).
 */
export function newCardId(now: number = Date.now()): string {
  const b = new Uint8Array(16)
  crypto.getRandomValues(b)
  let ms = now
  for (let i = 5; i >= 0; i--) {
    b[i] = ms % 256
    ms = Math.floor(ms / 256)
  }
  b[6] = 0x70 | (b[6]! & 0x0f)
  b[8] = 0x80 | (b[8]! & 0x3f)
  const h = Array.from(b, (x) => x.toString(16).padStart(2, '0')).join('')
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`
}

export { CardType }
