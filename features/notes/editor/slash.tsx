'use client'

import { computePosition, flip, offset, shift } from '@floating-ui/dom'
import { Extension, type Editor } from '@tiptap/core'
import { ReactRenderer } from '@tiptap/react'
import Suggestion, { type SuggestionProps } from '@tiptap/suggestion'
import { useTranslations } from 'next-intl'
import { forwardRef, useImperativeHandle, useState } from 'react'
import { cn } from '@/lib/cn'
import type { CardType } from '../model/doc'
import { replaceCurrentCard } from './nodes'

/** The cards the slash menu and the Add-card menu offer, with words people search for. Media cards come with uploads. */
export const CARD_MENU: { type: CardType; keywords: string }[] = [
  { type: 'text', keywords: 'paragraph text plain' },
  { type: 'heading', keywords: 'heading title h1 h2 h3 section' },
  { type: 'checklist', keywords: 'checklist todo task list' },
  { type: 'quote', keywords: 'quote citation' },
  { type: 'callout', keywords: 'callout note tip warning info box' },
  { type: 'code', keywords: 'code snippet program' },
  { type: 'table', keywords: 'table grid rows columns' },
  { type: 'question', keywords: 'question practice answer reveal' },
  { type: 'quiz', keywords: 'quiz multiple choice mcq test' },
  { type: 'flashcard', keywords: 'flashcard flash card front back revise' },
  { type: 'markdown', keywords: 'markdown md' },
  { type: 'diagram', keywords: 'diagram mermaid chart flow graph' },
]

export interface SlashListHandle {
  onKeyDown: (event: KeyboardEvent) => boolean
}

type SlashProps = SuggestionProps<(typeof CARD_MENU)[number], { type: CardType }>

const SlashList = forwardRef<SlashListHandle, SlashProps>(function SlashList({ items, command }, ref) {
  const t = useTranslations('notes.editor')
  const [active, setActive] = useState(0)
  const [lastItems, setLastItems] = useState(items)
  // A new search starts at the top of the list (adjusting state during render, without an effect).
  if (items !== lastItems) {
    setLastItems(items)
    setActive(0)
  }
  useImperativeHandle(ref, () => ({
    onKeyDown: (event) => {
      if (!items.length) return false
      if (event.key === 'ArrowDown') setActive((a) => (a + 1) % items.length)
      else if (event.key === 'ArrowUp') setActive((a) => (a - 1 + items.length) % items.length)
      else if (event.key === 'Enter' || event.key === 'Tab') command({ type: items[active]!.type })
      else return false
      return true
    },
  }))
  if (!items.length) return <div className="rounded-xl border border-border bg-surface p-3 text-sm text-muted shadow-lg">{t('noCardType')}</div>
  return (
    <ul role="listbox" aria-label={t('addCard')} className="max-h-72 w-60 overflow-y-auto rounded-xl border border-border bg-surface p-1 shadow-lg">
      {items.map((item, i) => (
        <li key={item.type} role="option" aria-selected={i === active}>
          <button
            type="button"
            className={cn('flex w-full flex-col rounded-lg px-3 py-2 text-left text-sm', i === active ? 'bg-accent-soft text-fg' : 'text-fg hover:bg-surface-2')}
            onMouseEnter={() => setActive(i)}
            onMouseDown={(e) => {
              e.preventDefault()
              command({ type: item.type })
            }}
          >
            <span className="font-medium">{t(`cards.${item.type}`)}</span>
            <span className="text-xs text-muted">{t(`cardHints.${item.type}`)}</span>
          </button>
        </li>
      ))}
    </ul>
  )
})

function place(el: HTMLElement, rect: (() => DOMRect | null) | null | undefined) {
  const box = rect?.()
  if (!box) return
  void computePosition({ getBoundingClientRect: () => box }, el, { placement: 'bottom-start', middleware: [offset(6), flip(), shift({ padding: 8 })] }).then(({ x, y }) => {
    Object.assign(el.style, { left: `${x}px`, top: `${y}px` })
  })
}

/** Type "/" at the start of a line in a text card to turn it into, or add, another card. */
export const SlashMenu = Extension.create({
  name: 'slashMenu',
  addProseMirrorPlugins() {
    return [
      Suggestion<(typeof CARD_MENU)[number], { type: CardType }>({
        editor: this.editor,
        char: '/',
        startOfLine: true,
        allow: ({ state, range }) => {
          const $from = state.doc.resolve(range.from)
          return $from.depth >= 2 && $from.node(1).type.name === 'textCard' && $from.parent.type.name === 'paragraph'
        },
        items: ({ query }) => {
          const q = query.toLowerCase().trim()
          return CARD_MENU.filter((i) => !q || i.type.includes(q) || i.keywords.split(' ').some((k) => k.startsWith(q)))
        },
        command: ({ editor, range, props }) => {
          editor.chain().focus().deleteRange(range).run()
          replaceCurrentCard(editor as Editor, props.type)
        },
        render: () => {
          let component: ReactRenderer<SlashListHandle, SlashProps> | null = null
          let el: HTMLElement | null = null
          return {
            onStart: (props) => {
              component = new ReactRenderer(SlashList, { props, editor: props.editor })
              el = component.element as HTMLElement
              Object.assign(el.style, { position: 'absolute', zIndex: '50' })
              document.body.appendChild(el)
              place(el, props.clientRect)
            },
            onUpdate: (props) => {
              component?.updateProps(props)
              if (el) place(el, props.clientRect)
            },
            onKeyDown: ({ event }) => {
              if (event.key === 'Escape') {
                el?.remove()
                return true
              }
              return component?.ref?.onKeyDown(event) ?? false
            },
            onExit: () => {
              el?.remove()
              component?.destroy()
              component = null
              el = null
            },
          }
        },
      }),
    ]
  },
})
