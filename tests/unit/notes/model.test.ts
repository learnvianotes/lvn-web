import { describe, expect, it } from 'vitest'
import { positionsBetween } from '@/lib/contracts/validation'
import { cardsToDoc, cardToNode, contentKey, docToCards, newCardId, nodeToCard, type StoredCard } from '@/features/notes/model/doc'
import { assignPositions } from '@/features/notes/model/positions'
import { afterSave, planSave, savedStateOf } from '@/features/notes/model/save'
import { acceptFor, cardTypeFor, mimeOf, srcSetOf } from '@/features/notes/media'

const p = (text: string) => ({ type: 'paragraph', content: [{ type: 'text', text }] })
const doc = (...blocks: object[]) => ({ type: 'doc', content: blocks })
const inline = (text: string) => [{ type: 'text', text }]
const id = (n: number) => `01920000-0000-7000-8000-${String(n).padStart(12, '0')}`

/** One stored card per type the editor edits, plus a media card it only carries. */
const keys = positionsBetween(null, null, 13)
const CARDS: StoredCard[] = [
  { id: id(1), type: 'heading', content: { level: 2, content: inline('Graphs') } },
  { id: id(2), type: 'text', content: { doc: doc(p('BFS visits'), { type: 'bulletList', content: [{ type: 'listItem', content: [p('level by level')] }] }) } },
  { id: id(3), type: 'quote', content: { doc: doc(p('Simple is good')), attribution: 'Dijkstra' } },
  { id: id(4), type: 'callout', content: { variant: 'tip', title: 'Remember', doc: doc(p('Use a queue')) } },
  { id: id(5), type: 'checklist', content: { items: [{ id: 'a', checked: true, content: inline('Read') }, { id: 'b', checked: false, content: [] }] } },
  { id: id(6), type: 'code', content: { language: 'python', code: 'from collections import deque' } },
  { id: id(7), type: 'markdown', content: { source: '**bold**' } },
  { id: id(8), type: 'diagram', content: { syntax: 'mermaid', source: 'graph TD; A-->B' } },
  { id: id(9), type: 'table', content: { hasHeaderRow: true, rows: [[inline('n'), inline('ops')], [inline('8'), inline('3')]] } },
  { id: id(10), type: 'question', content: { prompt: doc(p('Why a queue?')), answer: doc(p('FIFO order')) } },
  { id: id(11), type: 'quiz', content: { question: doc(p('BFS uses')), choices: [{ id: 'a', content: inline('a stack') }, { id: 'b', content: inline('a queue') }], correct: ['b'], multiple: false } },
  { id: id(12), type: 'flashcard', content: { front: doc(p('BFS')), back: doc(p('Breadth-first search')) } },
  { id: id(13), type: 'image', content: { fileId: id(99), alt: 'tree', caption: inline('A tree') } },
].map((c, i) => ({ ...c, position: keys[i]!, revision: 1 }) as StoredCard)

describe('the editor document and cards', () => {
  it('turns every card type into an editor node and back without losing anything', () => {
    for (const card of CARDS) {
      const back = nodeToCard(cardToNode(card))
      expect(back).toEqual({ id: card.id, type: card.type, content: card.content })
    }
    expect(docToCards(cardsToDoc(CARDS)).map((c) => c.id)).toEqual(CARDS.map((c) => c.id))
  })

  it('gives an empty note one empty text card to type into', () => {
    const d = cardsToDoc([])
    expect(d.content).toHaveLength(1)
    expect(d.content![0]).toMatchObject({ type: 'textCard', content: [{ type: 'paragraph' }] })
  })

  it('makes UUIDv7 card ids that sort by time, without crypto.randomUUID (plain-HTTP origins)', () => {
    const a = newCardId(Date.UTC(2026, 9, 9))
    const b = newCardId(Date.UTC(2026, 9, 9) + 1)
    expect(a).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/)
    expect(a < b).toBe(true)
    expect(a.slice(0, 13)).toBe('01a11df5-a400') // 2026-10-09T00:00:00Z in the first 48 bits
  })

  it('compares contents whatever the key order', () => {
    expect(contentKey({ b: 1, a: { d: 2, c: [3, { f: 4, e: 5 }] } })).toBe(contentKey({ a: { c: [3, { e: 5, f: 4 }], d: 2 }, b: 1 }))
  })
})

describe('positions after editing', () => {
  it('keeps every position when nothing moved, and only renumbers moved or new cards', () => {
    const items = CARDS.slice(0, 5).map((c) => ({ id: c.id, position: c.position }))
    expect([...assignPositions(items).values()]).toEqual(items.map((i) => i.position))

    const moved = [items[0]!, items[3]!, items[1]!, items[2]!, { id: 'new', position: null }, items[4]!]
    const result = assignPositions(moved)
    const order = moved.map((m) => result.get(m.id)!)
    expect([...order].sort()).toEqual(order)
    const changed = moved.filter((m) => m.position !== null && result.get(m.id) !== m.position)
    expect(changed).toHaveLength(1)
  })
})

describe('planning a save (§13.2)', () => {
  const stored = CARDS.slice(0, 4)
  const asDraft = (cards: StoredCard[]) => cards.map((c) => nodeToCard(cardToNode(c))!)

  it('sends nothing when nothing changed', () => {
    const plan = planSave(savedStateOf('T', stored), 'T', asDraft(stored))
    expect(plan).toMatchObject({ ops: [], invalid: [] })
    expect(plan.title).toBeUndefined()
  })

  it('does not count an empty card the editor filled with an empty paragraph as a change', () => {
    const empty: StoredCard = { id: id(50), type: 'text', position: 'a0', revision: 1, content: { doc: doc() } }
    expect(planSave(savedStateOf('', [empty]), '', asDraft([empty])).ops).toEqual([])
  })

  it('sends changes with the revision the editor saw, moves, new cards and deletes', () => {
    const saved = savedStateOf('T', stored)
    const draft = asDraft(stored)
    draft[1] = { ...draft[1]!, content: { doc: doc(p('BFS visits, edited')) } }
    const fresh = { id: id(60), type: 'text' as const, content: { doc: doc(p('new')) } }
    const next = [draft[1]!, draft[0]!, fresh, draft[3]!] // card 3 deleted, card 2 moved first
    const plan = planSave(saved, 'T2', next)
    expect(plan.title).toBe('T2')
    expect(plan.ops.map((o) => [o.kind, o.id, o.baseRevision])).toEqual([
      ['UPSERT', id(2), 1],
      ['UPSERT', id(60), undefined],
      ['DELETE', id(3), 1],
    ])
    // Card 1 kept its position; card 2's new position comes before it, so no separate MOVE is needed for card 1.
    const positions = next.map((c) => plan.next.cards.get(c.id)!.position)
    expect([...positions].sort()).toEqual(positions)

    const after = afterSave(plan, [
      { id: id(2), status: 'APPLIED', revision: 2 },
      { id: id(60), status: 'APPLIED', revision: 1 },
      { id: id(3), status: 'APPLIED', revision: 1 },
    ])
    expect(after.cards.get(id(2))!.revision).toBe(2)
    expect(after.cards.has(id(3))).toBe(false)
    expect(planSave(after, 'T2', next).ops).toEqual([])
  })

  it('holds back an invalid card and says why, saving the rest', () => {
    const saved = savedStateOf('T', stored)
    const draft = asDraft(stored)
    draft[0] = { ...draft[0]!, content: { level: 2, content: [{ type: 'text', text: 'x', marks: [{ type: 'link', attrs: { href: 'javascript:alert(1)' } }] }] } }
    draft[1] = { ...draft[1]!, content: { doc: doc(p('fine')) } }
    const plan = planSave(saved, 'T', draft)
    expect(plan.invalid.map((i) => i.id)).toEqual([id(1)])
    expect(plan.ops.map((o) => o.id)).toEqual([id(2)])
  })

  it('forgets cards the server refused, so the editor never loops', () => {
    const saved = savedStateOf('T', stored)
    const plan = planSave(saved, 'T', asDraft(stored).slice(1))
    const after = afterSave(plan, [{ id: id(1), status: 'REJECTED', revision: 3 }])
    expect(after.cards.has(id(1))).toBe(false)
    expect(planSave(after, 'T', asDraft(stored).slice(1)).ops).toEqual([])
  })
})

describe('media cards (P2c-2)', () => {
  it('are one editor node that keeps the card type', () => {
    expect(cardToNode(CARDS[12]!)).toMatchObject({ type: 'mediaCard', attrs: { cardType: 'image', data: { fileId: id(99) } } })
    expect(cardToNode({ id: id(20), type: 'file', content: null })).toMatchObject({ type: 'mediaCard', attrs: { cardType: 'file', data: null } })
  })

  it('wait for their file before they are saved, then go out as new cards', () => {
    const saved = savedStateOf('T', CARDS.slice(0, 1))
    const waiting = { id: id(21), type: 'video' as const, content: null }
    const plan = planSave(saved, 'T', [nodeToCard(cardToNode(CARDS[0]!))!, waiting])
    expect(plan).toMatchObject({ ops: [], invalid: [] })
    const ready = planSave(saved, 'T', [nodeToCard(cardToNode(CARDS[0]!))!, { ...waiting, content: { fileId: id(98) } }])
    expect(ready.ops).toEqual([expect.objectContaining({ kind: 'UPSERT', id: id(21), type: 'video', content: { fileId: id(98) } })])
  })

  it('know which card a dropped file becomes, and the type the API wants', () => {
    const file = (name: string, type: string) => new File([new Uint8Array(4)], name, { type })
    expect(cardTypeFor(file('a.png', 'image/png'))).toBe('image')
    expect(cardTypeFor(file('clip.mov', ''))).toBe('video')
    expect(mimeOf(file('clip.mov', ''))).toBe('video/quicktime')
    expect(cardTypeFor(file('talk.m4a', 'audio/x-m4a'))).toBe('audio')
    expect(mimeOf(file('talk.m4a', 'audio/x-m4a'))).toBe('audio/mp4')
    expect(cardTypeFor(file('notes.pdf', 'application/pdf'))).toBe('file')
    expect(cardTypeFor(file('run.exe', 'application/x-msdownload'))).toBeNull()
    expect(acceptFor('image')).toBe('image/jpeg,image/png,image/webp,image/gif')
  })

  it('offer the picture sizes the server made, never wider than the original (ADR-0041)', () => {
    const file = { url: 'https://storage.example/o', mimeType: 'image/jpeg', fileName: 'a.jpg', sizeBytes: 1 }
    expect(srcSetOf(file)).toBeUndefined()
    expect(srcSetOf({ ...file, width: 2400, thumbUrl: 'https://storage.example/t', mediumUrl: 'https://storage.example/m', largeUrl: 'https://storage.example/l' })).toBe('https://storage.example/t 320w, https://storage.example/m 960w, https://storage.example/l 1920w')
    expect(srcSetOf({ ...file, width: 500, thumbUrl: 'https://storage.example/t', mediumUrl: 'https://storage.example/m', largeUrl: 'https://storage.example/l' })).toBe('https://storage.example/t 320w, https://storage.example/m 500w, https://storage.example/l 500w')
    expect(srcSetOf({ ...file, width: null, thumbUrl: 'https://storage.example/t', mediumUrl: null, largeUrl: null })).toBe('https://storage.example/t 320w')
    expect(srcSetOf({ ...file, width: 2400, thumbUrl: 'javascript:alert(1)', mediumUrl: 'https://storage.example/m', largeUrl: null })).toBe('https://storage.example/m 960w')
  })
})
