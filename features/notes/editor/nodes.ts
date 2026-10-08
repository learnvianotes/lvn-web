import { Extension, Node, mergeAttributes, type Editor, type JSONContent } from '@tiptap/core'
import { Plugin, PluginKey, TextSelection, type EditorState, type Transaction } from '@tiptap/pm/state'
import type { Node as PMNode } from '@tiptap/pm/model'
import { ReactNodeViewRenderer } from '@tiptap/react'
import { cardToNode, newCardId, type CardType } from '../model/doc'
import { CalloutView, CheckItemView, CodeLikeView, FlashcardView, HeadingView, OpaqueView, QuestionView, QuizView, QuoteView, TableView } from './views'

/**
 * The note editor's schema (lvn-backend §4.1, §12.2): the document is a list of cards, one node type per card type.
 * Rich-text cards hold paragraphs and lists; code-like cards hold plain text; structured cards (table, question, quiz,
 * flashcard) are atoms edited through forms. Every card node carries `id`, `position` and `revision` (../model/doc).
 */

const hidden = (fallback: unknown = null) => ({ default: fallback, rendered: false, keepOnSplit: false })
const cardAttributes = () => ({ id: hidden(), position: hidden(), revision: hidden() })

export const NoteDocument = Node.create({ name: 'doc', topNode: true, content: 'card+' })

export const TextCard = Node.create({
  name: 'textCard',
  group: 'card',
  content: 'block+',
  defining: true,
  addAttributes: cardAttributes,
  parseHTML: () => [{ tag: 'div[data-card="text"]' }],
  renderHTML: () => ['div', { 'data-card': 'text', class: 'lvn-card lvn-card-text' }, 0],
})

export const HeadingCard = Node.create({
  name: 'headingCard',
  group: 'card',
  content: 'inline*',
  defining: true,
  addAttributes: () => ({ ...cardAttributes(), level: { default: 1, rendered: false } }),
  parseHTML: () => [1, 2, 3].map((level) => ({ tag: `h${level}`, attrs: { level } })),
  renderHTML: ({ node }) => [`h${node.attrs.level as number}`, { 'data-card': 'heading', class: 'lvn-card lvn-card-heading' }, 0],
  addNodeView: () => ReactNodeViewRenderer(HeadingView),
  addKeyboardShortcuts() {
    // Enter at the end of a heading starts a text card below it, as in any document.
    return { Enter: ({ editor }) => (inCard(editor, 'headingCard') ? insertCardAfter(editor, 'text') : false) }
  },
})

export const QuoteCard = Node.create({
  name: 'quoteCard',
  group: 'card',
  content: 'block+',
  defining: true,
  addAttributes: () => ({ ...cardAttributes(), attribution: { default: '', rendered: false } }),
  renderHTML: () => ['blockquote', { 'data-card': 'quote', class: 'lvn-card lvn-card-quote' }, 0],
  addNodeView: () => ReactNodeViewRenderer(QuoteView),
})

export const CalloutCard = Node.create({
  name: 'calloutCard',
  group: 'card',
  content: 'block+',
  defining: true,
  addAttributes: () => ({ ...cardAttributes(), variant: { default: 'note', rendered: false }, title: { default: '', rendered: false } }),
  renderHTML: () => ['aside', { 'data-card': 'callout', class: 'lvn-card lvn-card-callout' }, 0],
  addNodeView: () => ReactNodeViewRenderer(CalloutView),
})

export const ChecklistCard = Node.create({
  name: 'checklistCard',
  group: 'card',
  content: 'checkItem+',
  defining: true,
  addAttributes: cardAttributes,
  renderHTML: () => ['ul', { 'data-card': 'checklist', class: 'lvn-card lvn-card-checklist' }, 0],
})

export const CheckItem = Node.create({
  name: 'checkItem',
  content: 'inline*',
  defining: true,
  addAttributes: () => ({ id: hidden(), checked: { default: false, rendered: false, keepOnSplit: false } }),
  renderHTML: ({ HTMLAttributes }) => ['li', mergeAttributes(HTMLAttributes, { class: 'lvn-check-item' }), 0],
  addNodeView: () => ReactNodeViewRenderer(CheckItemView),
})

const codeLike = (name: string, card: string, extra: Record<string, ReturnType<typeof hidden>> = {}) =>
  Node.create({
    name,
    group: 'card',
    content: 'text*',
    marks: '',
    code: true,
    defining: true,
    addAttributes: () => ({ ...cardAttributes(), ...extra }),
    renderHTML: () => ['pre', { 'data-card': card, class: `lvn-card lvn-card-${card}` }, ['code', 0]],
    addNodeView: () => ReactNodeViewRenderer(CodeLikeView),
    addKeyboardShortcuts() {
      return {
        // Code keeps its indentation; Mod-Enter leaves the card.
        Tab: ({ editor }) => (inCard(editor, name) ? editor.commands.insertContent('  ') : false),
        'Mod-Enter': ({ editor }) => (inCard(editor, name) ? insertCardAfter(editor, 'text') : false),
      }
    },
  })

export const CodeCard = codeLike('codeCard', 'code', { language: { default: '', rendered: false, keepOnSplit: false }, filename: { default: '', rendered: false, keepOnSplit: false } })
export const MarkdownCard = codeLike('markdownCard', 'markdown')
export const DiagramCard = codeLike('diagramCard', 'diagram', { caption: hidden() })

const atom = (name: string, card: string, view: typeof TableView) =>
  Node.create({
    name,
    group: 'card',
    atom: true,
    selectable: true,
    draggable: false,
    addAttributes: () => ({ ...cardAttributes(), data: { default: null, rendered: false }, cardType: { default: card, rendered: false } }),
    renderHTML: () => ['div', { 'data-card': card, class: `lvn-card lvn-card-${card}` }],
    addNodeView: () => ReactNodeViewRenderer(view),
  })

export const TableCard = atom('tableCard', 'table', TableView)
export const QuestionCard = atom('questionCard', 'question', QuestionView)
export const QuizCard = atom('quizCard', 'quiz', QuizView)
export const FlashcardCard = atom('flashcardCard', 'flashcard', FlashcardView)
/** A card type this editor does not edit (media until uploads reach notes, or a type from a newer app): kept as it is. */
export const OpaqueCard = atom('opaqueCard', 'opaque', OpaqueView)

// ── Card ids ─────────────────────────────────────────────────────────────────────────────────────────────────

/**
 * Every card and checklist item needs its own id. New nodes get one; a copy (paste, split, duplicate) gets a fresh one
 * and forgets the stored position and revision, so it saves as a new card.
 */
export const CardIds = Extension.create({
  name: 'cardIds',
  addProseMirrorPlugins() {
    return [
      new Plugin({
        key: new PluginKey('cardIds'),
        appendTransaction: (transactions, _old, state) => (transactions.some((t) => t.docChanged) ? fixIds(state) : null),
      }),
    ]
  },
})

function fixIds(state: EditorState): Transaction | null {
  const seen = new Set<string>()
  let tr: Transaction | null = null
  const fix = (node: PMNode, pos: number, card: boolean) => {
    const id = node.attrs.id as string | null
    if (id && !seen.has(id)) return seen.add(id)
    const fresh = newCardId()
    seen.add(fresh)
    tr ??= state.tr
    tr.setNodeMarkup(pos, undefined, card ? { ...node.attrs, id: fresh, position: null, revision: null } : { ...node.attrs, id: fresh })
  }
  state.doc.forEach((card, offset) => {
    fix(card, offset, true)
    if (card.type.name === 'checklistCard') card.forEach((item, itemOffset) => fix(item, offset + 1 + itemOffset, false))
  })
  return tr
}

// ── Commands ─────────────────────────────────────────────────────────────────────────────────────────────────

/** The top-level card the selection is in: its node and position. */
export function currentCard(editor: Editor): { node: PMNode; pos: number; index: number } | null {
  const { $from } = editor.state.selection
  if ($from.depth === 0) {
    const node = editor.state.doc.nodeAt($from.pos)
    return node ? { node, pos: $from.pos, index: $from.index(0) } : null
  }
  return { node: $from.node(1), pos: $from.before(1), index: $from.index(0) }
}

function inCard(editor: Editor, name: string): boolean {
  const card = currentCard(editor)
  return card?.node.type.name === name && editor.state.selection.empty && editor.state.selection.$from.parentOffset === editor.state.selection.$from.parent.content.size
}

/** A new, empty card of a type, as editor JSON. */
export function emptyCard(type: CardType): JSONContent {
  const empty: Record<CardType, unknown> = {
    text: { doc: { type: 'doc', content: [] } },
    heading: { level: 2, content: [] },
    quote: { doc: { type: 'doc', content: [] } },
    callout: { variant: 'note', doc: { type: 'doc', content: [] } },
    checklist: { items: [] },
    code: { language: '', code: '' },
    markdown: { source: '' },
    diagram: { syntax: 'mermaid', source: 'graph TD\n  A --> B' },
    table: { hasHeaderRow: true, rows: [[[], []], [[], []]] },
    question: { prompt: { type: 'doc', content: [] }, answer: { type: 'doc', content: [] } },
    quiz: { question: { type: 'doc', content: [] }, choices: [{ id: 'a', content: [] }, { id: 'b', content: [] }], correct: ['a'], multiple: false },
    flashcard: { front: { type: 'doc', content: [] }, back: { type: 'doc', content: [] } },
    image: null,
    video: null,
    audio: null,
    file: null,
  }
  return cardToNode({ id: newCardId(), type, content: empty[type] })
}

/** Inserts an empty card after the current one and puts the cursor in it. */
export function insertCardAfter(editor: Editor, type: CardType): boolean {
  const card = currentCard(editor)
  const at = card ? card.pos + card.node.nodeSize : editor.state.doc.content.size
  return editor.chain().insertContentAt(at, emptyCard(type)).focus().setTextSelection(at + 1).run()
}

/** Replaces the current card — an empty text card the slash menu was typed in — with an empty card of a type. */
export function replaceCurrentCard(editor: Editor, type: CardType): boolean {
  const card = currentCard(editor)
  if (!card) return false
  const empty = card.node.type.name === 'textCard' && card.node.textContent.trim() === ''
  if (!empty) return insertCardAfter(editor, type)
  return editor
    .chain()
    .command(({ tr }) => {
      tr.replaceWith(card.pos, card.pos + card.node.nodeSize, editor.schema.nodeFromJSON(emptyCard(type)))
      tr.setSelection(TextSelection.near(tr.doc.resolve(card.pos + 1)))
      return true
    })
    .focus()
    .run()
}

/** Moves the current card up or down one place. */
export function moveCard(editor: Editor, direction: -1 | 1): boolean {
  const card = currentCard(editor)
  if (!card) return false
  const { doc } = editor.state
  const target = card.index + direction
  if (target < 0 || target >= doc.childCount) return false
  const other = doc.child(target)
  return editor
    .chain()
    .command(({ tr }) => {
      const offsetInCard = editor.state.selection.from - card.pos
      if (direction === -1) {
        const otherPos = card.pos - other.nodeSize
        tr.delete(card.pos, card.pos + card.node.nodeSize).insert(otherPos, card.node)
        tr.setSelection(TextSelection.near(tr.doc.resolve(Math.min(otherPos + offsetInCard, tr.doc.content.size))))
      } else {
        const after = card.pos + card.node.nodeSize + other.nodeSize
        tr.insert(after, card.node).delete(card.pos, card.pos + card.node.nodeSize)
        const newPos = after - card.node.nodeSize
        tr.setSelection(TextSelection.near(tr.doc.resolve(Math.min(newPos + offsetInCard, tr.doc.content.size))))
      }
      return true
    })
    .scrollIntoView()
    .run()
}

/** Deletes the current card; a note always keeps at least one card. */
export function deleteCard(editor: Editor): boolean {
  const card = currentCard(editor)
  if (!card) return false
  return editor
    .chain()
    .command(({ tr, state }) => {
      tr.delete(card.pos, card.pos + card.node.nodeSize)
      if (tr.doc.childCount === 0) tr.insert(0, state.schema.nodeFromJSON(emptyCard('text')))
      tr.setSelection(TextSelection.near(tr.doc.resolve(Math.min(card.pos, tr.doc.content.size - 1))))
      return true
    })
    .focus()
    .run()
}

/** Puts the selection in the card at `pos` (text cursor at its start, or the whole card for a structured card). */
export function selectCard(editor: Editor, pos: number): void {
  const node = editor.state.doc.nodeAt(pos)
  if (!node) return
  if (node.isAtom) editor.commands.setNodeSelection(pos)
  else editor.commands.setTextSelection(pos + 1)
}

/** Copies the card at the cursor right below it; the copy is a new card with its own id. */
export function duplicateCard(editor: Editor): boolean {
  const card = currentCard(editor)
  if (!card) return false
  return editor.chain().insertContentAt(card.pos + card.node.nodeSize, card.node.toJSON()).focus().run()
}

/** Rich-text card types a text card can turn into, and back. */
export const CONVERTIBLE: CardType[] = ['text', 'heading', 'quote', 'callout']

/** Turns the current rich-text card into another rich-text type, keeping its words, id and history. */
export function convertCard(editor: Editor, to: CardType): boolean {
  const card = currentCard(editor)
  if (!card) return false
  const from = card.node.type.name
  if (!['textCard', 'headingCard', 'quoteCard', 'calloutCard'].includes(from)) return false
  const json = card.node.toJSON() as JSONContent
  const attrs = { id: json.attrs?.id, position: json.attrs?.position, revision: json.attrs?.revision }
  const blocks: JSONContent[] = from === 'headingCard' ? [{ type: 'paragraph', content: json.content ?? [] }] : (json.content ?? [{ type: 'paragraph' }])
  const firstLine = (blocks.find((b) => b.type === 'paragraph')?.content ?? []) as JSONContent[]
  const next: JSONContent =
    to === 'heading'
      ? { type: 'headingCard', attrs: { ...attrs, level: 2 }, content: firstLine }
      : to === 'quote'
        ? { type: 'quoteCard', attrs: { ...attrs, attribution: '' }, content: blocks }
        : to === 'callout'
          ? { type: 'calloutCard', attrs: { ...attrs, variant: 'tip', title: '' }, content: blocks }
          : { type: 'textCard', attrs, content: blocks }
  return editor
    .chain()
    .command(({ tr }) => {
      tr.replaceWith(card.pos, card.pos + card.node.nodeSize, editor.schema.nodeFromJSON(next))
      tr.setSelection(TextSelection.near(tr.doc.resolve(card.pos + 1)))
      return true
    })
    .focus()
    .run()
}

export const CardKeys = Extension.create({
  name: 'cardKeys',
  addKeyboardShortcuts() {
    return {
      'Alt-ArrowUp': ({ editor }) => moveCard(editor, -1),
      'Alt-ArrowDown': ({ editor }) => moveCard(editor, 1),
      'Mod-Shift-Enter': ({ editor }) => insertCardAfter(editor, 'text'),
      'Mod-Shift-d': ({ editor }) => duplicateCard(editor),
    }
  },
})

export const CARD_NODES = [NoteDocument, TextCard, HeadingCard, QuoteCard, CalloutCard, ChecklistCard, CheckItem, CodeCard, MarkdownCard, DiagramCard, TableCard, QuestionCard, QuizCard, FlashcardCard, OpaqueCard, CardIds, CardKeys]
