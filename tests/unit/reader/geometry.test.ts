import { describe, expect, it } from 'vitest'
import { areaRect, hits, quoteOf, selectionRects, toPageRect } from '@/features/reader/geometry'
import { cardToNode, nodeToCard } from '@/features/notes/model/doc'

/** lvn-backend ADR-0040: places on a page are fractions of it, the same at every zoom. */
const page = { left: 100, top: 50, width: 600, height: 800 }
const r = (left: number, top: number, right: number, bottom: number) => ({ left, top, right, bottom })

describe('page rectangles', () => {
  it('turns screen rectangles into fractions of the page, clipped to it', () => {
    expect(toPageRect(r(160, 130, 400, 146), page)).toEqual([0.1, 0.1, 0.5, 0.12])
    expect(toPageRect(r(50, 30, 160, 60), page)).toEqual([0, 0, 0.1, 0.0125])
    expect(toPageRect(r(800, 100, 900, 120), page)).toBeNull()
    expect(toPageRect(r(200, 100, 200.5, 120), page)).toBeNull()
  })

  it('makes one rectangle per line from the spans of a selection, top to bottom', () => {
    const spans = [
      r(400, 170, 650, 186), // line 2
      r(160, 130, 300, 146), // line 1, first span
      r(298, 131, 640, 145), // line 1, second span
      r(160, 170, 402, 186), // line 2, first span
      r(100, 50, 700, 850), // the text layer's end-of-content box
    ]
    expect(selectionRects(spans, page)).toEqual([
      [0.1, 0.1, 0.9, 0.12],
      [0.1, 0.15, 0.91667, 0.17],
    ])
  })

  it('snips an area dragged in any direction, inside the page', () => {
    expect(areaRect({ x: 0.8, y: 0.6 }, { x: 0.2, y: 1.3 })).toEqual([0.2, 0.6, 0.8, 1])
  })

  it('finds what was clicked, with a little slack', () => {
    expect(hits([[0.1, 0.1, 0.5, 0.12]], 0.3, 0.11)).toBe(true)
    expect(hits([[0.1, 0.1, 0.5, 0.12]], 0.3, 0.122)).toBe(true)
    expect(hits([[0.1, 0.1, 0.5, 0.12]], 0.3, 0.2)).toBe(false)
  })

  it('quotes a selection as one line, mending words split at line ends', () => {
    expect(quoteOf('  Photo-\nsynthesis needs\n\nlight and   water ')).toBe('Photosynthesis needs light and water')
    expect(quoteOf('x'.repeat(6000))).toHaveLength(5000)
  })
})

describe('anchors in the editor', () => {
  const anchor = { fileId: '01920000-0000-7000-8000-0000000000aa', page: 3, rects: [[0.1, 0.1, 0.5, 0.12]], quote: 'Cells' }
  const quote = { doc: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Cells' }] }] } }

  it('keeps a card’s anchor through the editor and back, for rich text and for media cards', () => {
    const node = cardToNode({ id: 'q', type: 'quote', content: { ...quote, anchor } })
    expect(node.attrs).toMatchObject({ anchor })
    expect(nodeToCard(node)).toEqual({ id: 'q', type: 'quote', content: { ...quote, anchor } })
    const image = cardToNode({ id: 'i', type: 'image', content: { fileId: '01920000-0000-7000-8000-0000000000bb', alt: '', anchor } })
    expect(nodeToCard(image)).toEqual({ id: 'i', type: 'image', content: { fileId: '01920000-0000-7000-8000-0000000000bb', alt: '', anchor } })
    expect(nodeToCard(cardToNode({ id: 't', type: 'text', content: quote }))!.content).toEqual(quote)
  })
})
