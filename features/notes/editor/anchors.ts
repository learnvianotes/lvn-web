import { Extension } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'
import type { CardAnchor } from '@/lib/contracts/validation'

export interface AnchorChipsOptions {
  /** Opens the PDF where the card came from; no chips without it */
  onOpen: ((anchor: CardAnchor, cardId: string) => void) | null
  label: (page: number) => string
}

/**
 * A chip under every card made from a PDF (lvn-backend ADR-0040) — "p. 12" — that opens the PDF at the passage. A
 * widget between cards, so it is never part of what is written or saved.
 */
export const AnchorChips = Extension.create<AnchorChipsOptions>({
  name: 'anchorChips',
  addOptions: () => ({ onOpen: null, label: (page) => `p. ${page}` }),
  addProseMirrorPlugins() {
    const { onOpen, label } = this.options
    if (!onOpen) return []
    return [
      new Plugin({
        key: new PluginKey('anchorChips'),
        props: {
          decorations: (state) => {
            const chips: Decoration[] = []
            state.doc.forEach((node, offset) => {
              const anchor = node.attrs.anchor as CardAnchor | null
              const id = node.attrs.id as string | null
              if (!anchor || !id) return
              chips.push(Decoration.widget(offset + node.nodeSize, () => chip(anchor, id, onOpen, label), { side: -1, key: `${id}:${anchor.fileId}:${anchor.page}`, ignoreSelection: true }))
            })
            return DecorationSet.create(state.doc, chips)
          },
        },
      }),
    ]
  },
})

function chip(anchor: CardAnchor, id: string, onOpen: (anchor: CardAnchor, cardId: string) => void, label: (page: number) => string): HTMLElement {
  const button = document.createElement('button')
  button.type = 'button'
  button.className = 'lvn-anchor-chip'
  button.contentEditable = 'false'
  button.dataset.anchorFor = id
  button.textContent = `↗ ${label(anchor.page)}`
  button.title = anchor.quote ? `“${anchor.quote.slice(0, 120)}${anchor.quote.length > 120 ? '…' : ''}”` : label(anchor.page)
  // Keep the editor's selection where it is.
  button.addEventListener('mousedown', (e) => e.preventDefault())
  button.addEventListener('click', (e) => {
    e.preventDefault()
    onOpen(anchor, id)
  })
  return button
}
