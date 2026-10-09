// Copied from lvn-backend contracts/src/validation/cards.ts by scripts/contracts-sync.mjs — do not edit here.
import { z } from 'zod'
import { CardType } from '../domain/enums'
import { docSchema, docText, inlineSchema, inlineText } from './rich-text'

/**
 * The content of each card type (§4.1): one schema per type, used by the API before it stores a card and by the web
 * and mobile editors before they send one. Rich text is Tiptap JSON (`./rich-text`); media cards point at a file by
 * id — never a URL or storage key (§8.2) — and the API resolves read URLs after its own permission check.
 */

export const CARD_LIMITS = {
  /** Serialised JSON of one card's content */
  contentBytes: 200_000,
  sourceChars: 100_000,
  codeLanguage: 32,
  caption: 1_000,
  alt: 500,
  checklistItems: 200,
  tableRows: 200,
  tableColumns: 20,
  quizChoices: 8,
  /** Anchors (ADR-0040): rectangles of one passage, its words, and the last page a PDF may have */
  anchorRects: 100,
  anchorQuote: 5_000,
  anchorPage: 100_000,
} as const

const uuid = z.string().uuid()
const shortId = z.string().min(1).max(36)

const fraction = z.number().min(0).max(1)

/** One rectangle on a PDF page, `[x0, y0, x1, y1]` as fractions of the page's width and height from its top left. */
export const pageRectSchema = z
  .tuple([fraction, fraction, fraction, fraction])
  .refine(([x0, y0, x1, y1]) => x1 >= x0 && y1 >= y0, 'A rectangle runs from its top left to its bottom right')

/**
 * Where a card came from (ADR-0040): a page of a PDF attached to the note and, for a passage or an area, its
 * rectangles and words. Cards made in the reader and cards the PDF engine makes (ADR-0028) carry the same anchor.
 */
export const cardAnchorSchema = z.object({
  fileId: uuid,
  page: z.number().int().min(1).max(CARD_LIMITS.anchorPage),
  rects: z.array(pageRectSchema).max(CARD_LIMITS.anchorRects).optional(),
  quote: z.string().max(CARD_LIMITS.anchorQuote).optional(),
})
export type CardAnchor = z.infer<typeof cardAnchorSchema>

/** Highlights in the PDF reader (ADR-0040): per note, and the comment on one. */
export const HIGHLIGHT_LIMITS = { perNote: 5_000, comment: 2_000 } as const

/** Every card type may carry an anchor. */
const anchored = { anchor: cardAnchorSchema.optional() }

const media = {
  fileId: uuid,
  caption: inlineSchema.optional(),
  ...anchored,
}

export const CARD_CONTENT = {
  [CardType.TEXT]: z.object({ doc: docSchema, ...anchored }),
  [CardType.HEADING]: z.object({ level: z.union([z.literal(1), z.literal(2), z.literal(3)]), content: inlineSchema, ...anchored }),
  [CardType.MARKDOWN]: z.object({ source: z.string().max(CARD_LIMITS.sourceChars), ...anchored }),
  [CardType.CODE]: z.object({
    language: z.string().regex(/^[a-z0-9+#.-]*$/, 'Use a language name such as python or c++').max(CARD_LIMITS.codeLanguage),
    code: z.string().max(CARD_LIMITS.sourceChars),
    filename: z.string().max(200).optional(),
    ...anchored,
  }),
  [CardType.IMAGE]: z.object({ ...media, alt: z.string().max(CARD_LIMITS.alt).default('') }),
  [CardType.VIDEO]: z.object(media),
  [CardType.AUDIO]: z.object(media),
  [CardType.FILE]: z.object(media),
  [CardType.DIAGRAM]: z.object({ syntax: z.literal('mermaid'), source: z.string().max(20_000), caption: inlineSchema.optional(), ...anchored }),
  [CardType.QUOTE]: z.object({ doc: docSchema, attribution: z.string().max(CARD_LIMITS.caption).optional(), ...anchored }),
  [CardType.CALLOUT]: z.object({
    variant: z.enum(['note', 'info', 'tip', 'warning', 'danger']),
    title: z.string().max(200).optional(),
    doc: docSchema,
    ...anchored,
  }),
  [CardType.CHECKLIST]: z.object({
    items: z.array(z.object({ id: shortId, checked: z.boolean(), content: inlineSchema })).max(CARD_LIMITS.checklistItems),
    ...anchored,
  }),
  [CardType.TABLE]: z
    .object({
      hasHeaderRow: z.boolean(),
      rows: z.array(z.array(inlineSchema).min(1).max(CARD_LIMITS.tableColumns)).min(1).max(CARD_LIMITS.tableRows),
      ...anchored,
    })
    .refine((t) => t.rows.every((r) => r.length === t.rows[0]!.length), 'Every row needs the same number of cells'),
  /** A practice question whose answer the reader reveals. */
  [CardType.QUESTION]: z.object({ prompt: docSchema, answer: docSchema, hint: docSchema.optional(), ...anchored }),
  [CardType.QUIZ]: z
    .object({
      question: docSchema,
      choices: z.array(z.object({ id: shortId, content: inlineSchema })).min(2).max(CARD_LIMITS.quizChoices),
      correct: z.array(shortId).min(1),
      multiple: z.boolean(),
      explanation: docSchema.optional(),
      ...anchored,
    })
    .refine((q) => new Set(q.choices.map((c) => c.id)).size === q.choices.length, 'Choices need different ids')
    .refine((q) => q.correct.every((id) => q.choices.some((c) => c.id === id)), 'A correct answer is not one of the choices')
    .refine((q) => q.multiple || q.correct.length === 1, 'A single-answer question has exactly one correct choice'),
  [CardType.FLASHCARD]: z.object({ front: docSchema, back: docSchema, ...anchored }),
} satisfies Record<CardType, z.ZodType>

export type CardContent<T extends CardType = CardType> = z.infer<(typeof CARD_CONTENT)[T]>

/** Card types whose content points at an uploaded file (§8.1). */
export const MEDIA_CARD_TYPES: ReadonlySet<CardType> = new Set([CardType.IMAGE, CardType.VIDEO, CardType.AUDIO, CardType.FILE])

export type CardParseResult<T extends CardType = CardType> = { ok: true; content: CardContent<T> } | { ok: false; message: string }

/** The anchor a card's content carries (ADR-0040), or null. */
export function cardAnchor(content: unknown): CardAnchor | null {
  const anchor = (content as { anchor?: unknown } | null)?.anchor
  if (anchor === undefined) return null
  const parsed = cardAnchorSchema.safeParse(anchor)
  return parsed.success ? parsed.data : null
}

/** Validates one card's content for its type; unknown attributes are dropped from what is returned. */
export function parseCardContent<T extends CardType>(type: T, content: unknown): CardParseResult<T> {
  const schema = (CARD_CONTENT as Record<string, z.ZodType>)[type] as z.ZodType<CardContent<T>> | undefined
  if (!schema) return { ok: false, message: `Unknown card type ${String(type)}` }
  let size: number
  try {
    size = JSON.stringify(content ?? null).length
  } catch {
    return { ok: false, message: 'The card content is not valid JSON' }
  }
  if (size > CARD_LIMITS.contentBytes) return { ok: false, message: 'This card is too large; split it into several cards' }
  const result = schema.safeParse(content)
  if (result.success) return { ok: true, content: result.data }
  const issue = result.error.issues[0]!
  const where = issue.path.length ? ` (${issue.path.join('.')})` : ''
  return { ok: false, message: `${issue.message}${where}` }
}

/** The words of a card, for search, outlines and read aloud. */
export function cardPlainText(type: CardType, content: unknown): string {
  const parsed = parseCardContent(type, content)
  if (!parsed.ok) return ''
  const c = parsed.content as Record<string, unknown>
  switch (type) {
    case CardType.TEXT:
    case CardType.QUOTE:
      return [docText(c.doc as never), c.attribution].filter(Boolean).join('\n')
    case CardType.CALLOUT:
      return [c.title, docText(c.doc as never)].filter(Boolean).join('\n')
    case CardType.HEADING:
      return inlineText(c.content as never)
    case CardType.MARKDOWN:
    case CardType.DIAGRAM:
      return String(c.source ?? '')
    case CardType.CODE:
      return String(c.code ?? '')
    case CardType.IMAGE:
      return [c.alt, inlineText(c.caption as never)].filter(Boolean).join('\n')
    case CardType.VIDEO:
    case CardType.AUDIO:
    case CardType.FILE:
      return inlineText(c.caption as never)
    case CardType.CHECKLIST:
      return (c.items as { content: never }[]).map((i) => inlineText(i.content)).join('\n')
    case CardType.TABLE:
      return (c.rows as never[][]).map((row) => row.map((cell) => inlineText(cell)).join('\t')).join('\n')
    case CardType.QUESTION:
      return [docText(c.prompt as never), docText(c.answer as never)].join('\n')
    case CardType.QUIZ:
      return [docText(c.question as never), ...(c.choices as { content: never }[]).map((ch) => inlineText(ch.content))].join('\n')
    case CardType.FLASHCARD:
      return [docText(c.front as never), docText(c.back as never)].join('\n')
    default:
      return ''
  }
}
