import { describe, expect, it } from 'vitest'
import {
  addStroke,
  blankPage,
  commit,
  cropRgba,
  enhanceRgba,
  eraseAt,
  historyOf,
  insertImage,
  pagesFromUnknown,
  pressureOf,
  redo,
  removeImage,
  scalePercent,
  straighten,
  strokePath,
  undo,
  updateImage,
  type Stroke,
} from '@/features/notes/pages/model'

const stroke = (points: Stroke['points'], extra: Partial<Stroke> = {}): Stroke => ({
  id: 's1',
  tool: 'pen',
  color: '#1d4ed8',
  width: 0.7,
  points,
  ...extra,
})

describe('note pages', () => {
  it('treats a mouse (pressure 0) as a medium stroke and keeps a stylus pressure', () => {
    expect(pressureOf(0)).toBe(0.5)
    expect(pressureOf(0.2)).toBe(0.2)
    expect(pressureOf(Number.NaN)).toBe(0.5)
  })

  it('undoes and redoes, and forgets the future after a new stroke', () => {
    const page = blankPage()
    let history = historyOf([page])
    const drawn = addStroke(page, stroke([{ x: 0.1, y: 0.1, p: 0.5 }, { x: 0.4, y: 0.2, p: 0.8 }]))
    history = commit(history, [{ ...page, strokes: drawn.strokes }])
    expect(history.present[0]?.strokes).toHaveLength(1)
    history = undo(history)
    expect(history.present[0]?.strokes).toHaveLength(0)
    history = redo(history)
    expect(history.present[0]?.strokes).toHaveLength(1)
    history = undo(history)
    history = commit(history, [insertImage(history.present[0]!, { id: 'img', name: 'a.png', href: 'data:image/png;base64,aa', x: 0.1, y: 0.1, w: 0.3, h: 0.2, rotation: 0 })])
    expect(history.future).toHaveLength(0)
    expect(history.present[0]?.images).toHaveLength(1)
  })

  it('straightens a ruler stroke and reports its length as a percent of the page', () => {
    const ruled = straighten(stroke([{ x: 0, y: 0, p: 0.5 }, { x: 0.2, y: 0.2, p: 0.5 }, { x: 0.3, y: 0.4, p: 0.5 }]))
    expect(ruled.straight).toBe(true)
    expect(ruled.points).toHaveLength(2)
    expect(scalePercent(ruled)).toBe(50)
    expect(strokePath(ruled)).toBe('M 0.00 0.00 L 30.00 40.00')
  })

  it('erases a stroke whose ink is near the pointer', () => {
    const page = addStroke(blankPage(), stroke([{ x: 0.5, y: 0.5, p: 0.5 }, { x: 0.55, y: 0.5, p: 0.5 }]))
    expect(eraseAt(page, { x: 0.52, y: 0.51, p: 0.5 }).strokes).toHaveLength(0)
    expect(eraseAt(page, { x: 0.9, y: 0.9, p: 0.5 }).strokes).toHaveLength(1)
  })

  it('moves, resizes, rotates and removes a picture inside the page', () => {
    const image = { id: 'img', name: 'a.png', href: 'data:image/png;base64,aa', x: 0.2, y: 0.2, w: 0.3, h: 0.3, rotation: 350 }
    let page = insertImage(blankPage(), image)
    page = updateImage(page, 'img', { x: 2, w: 0.01, rotation: image.rotation + 15 })
    expect(page.images[0]).toMatchObject({ x: 1, w: 0.08, rotation: 5 })
    page = removeImage(page, 'img')
    expect(page.images).toHaveLength(0)
  })

  it('crops a rectangle and lifts contrast without touching alpha', () => {
    const width = 4
    const height = 2
    const data = new Uint8ClampedArray(width * height * 4)
    data.set([10, 20, 30, 255, 40, 50, 60, 128], 0)
    const cropped = cropRgba(data, width, height, { x: 0, y: 0, w: 2, h: 1 })
    expect(cropped.width).toBe(2)
    expect(cropped.height).toBe(1)
    expect(Array.from(cropped.data.slice(0, 8))).toEqual([10, 20, 30, 255, 40, 50, 60, 128])
    const enhanced = enhanceRgba(cropped.data)
    expect(enhanced[3]).toBe(255)
    expect(enhanced[7]).toBe(128)
    expect(enhanced[0]).not.toBe(10)
  })

  it('rejects a page payload that is not ink and pictures', () => {
    const page = blankPage()
    expect(pagesFromUnknown([page])).toEqual([page])
    expect(pagesFromUnknown([{ id: 'x' }])).toBeNull()
    expect(pagesFromUnknown('nope')).toBeNull()
  })

  it('keeps at most 40 undo steps', () => {
    let history = historyOf([blankPage()])
    for (let i = 0; i < 45; i++) history = commit(history, [{ ...history.present[0]!, strokes: [stroke([{ x: i / 100, y: 0.1, p: 0.5 }])] }])
    expect(history.past.length).toBe(40)
  })
})
