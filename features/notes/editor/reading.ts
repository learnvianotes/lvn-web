import { Extension, type Editor } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

const key = new PluginKey<string | null>('readingCard')

/** Highlights the card being read aloud (a decoration: the document is not changed). */
export const ReadingHighlight = Extension.create({
  name: 'readingHighlight',
  addProseMirrorPlugins() {
    return [
      new Plugin<string | null>({
        key,
        state: {
          init: () => null,
          apply: (tr, value) => {
            const meta = tr.getMeta(key) as string | null | undefined
            return meta === undefined ? value : meta
          },
        },
        props: {
          decorations(state) {
            const id = key.getState(state)
            if (!id) return null
            let found: DecorationSet | null = null
            state.doc.forEach((node, offset) => {
              if (node.attrs.id === id) found = DecorationSet.create(state.doc, [Decoration.node(offset, offset + node.nodeSize, { class: 'lvn-reading' })])
            })
            return found
          },
        },
      }),
    ]
  },
})

export function setReadingCard(editor: Editor, id: string | null): void {
  editor.view.dispatch(editor.state.tr.setMeta(key, id))
  if (!id) return
  editor.state.doc.forEach((node, offset) => {
    if (node.attrs.id === id) (editor.view.nodeDOM(offset) as HTMLElement | null)?.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  })
}
