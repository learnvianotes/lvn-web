import type { CardType } from '@/lib/contracts/domain/enums'
import { cardToNode, contentKey, nodeToCard, normalise, type DraftCard } from './doc'
import { assignPositions } from './positions'

const MEDIA = new Set<CardType>(['image', 'video', 'audio', 'file'])

/** What the server last stored, as far as this editor knows. */
export interface SavedState {
  title: string
  cards: Map<string, { type: CardType; key: string; position: string; revision: number }>
}

export interface CardOp {
  kind: 'UPSERT' | 'MOVE' | 'DELETE'
  id: string
  type?: CardType
  position?: string
  content?: unknown
  baseRevision?: number
}

export interface SavePlan {
  title?: string
  ops: CardOp[]
  /** The state to keep if every op is applied */
  next: SavedState
  /** Cards that cannot be saved as they are, with the reason */
  invalid: { id: string; message: string }[]
}

/**
 * One autosave (lvn-backend §13.2): the title if it changed, and per card an UPSERT (new or changed, with the revision
 * the editor last saw), a MOVE (only the position changed) or a DELETE. Empty when nothing changed.
 */
export function planSave(saved: SavedState, title: string, cards: DraftCard[]): SavePlan {
  const positions = assignPositions(cards.map((c) => ({ id: c.id, position: saved.cards.get(c.id)?.position ?? null })))
  const ops: CardOp[] = []
  const invalid: SavePlan['invalid'] = []
  const next: SavedState = { title, cards: new Map() }
  for (const card of cards) {
    // A media card waiting for its file is not a card yet: it is saved once the upload is done.
    if (MEDIA.has(card.type) && !(card.content as { fileId?: string } | null)?.fileId) {
      const old = saved.cards.get(card.id)
      if (old) next.cards.set(card.id, old)
      continue
    }
    const normal = normalise(card)
    if (!normal.ok) {
      invalid.push({ id: card.id, message: normal.message })
      const old = saved.cards.get(card.id)
      if (old) next.cards.set(card.id, old)
      continue
    }
    const key = contentKey(normal.content)
    const position = positions.get(card.id)!
    const old = saved.cards.get(card.id)
    if (!old) ops.push({ kind: 'UPSERT', id: card.id, type: card.type, position, content: normal.content })
    else if (old.type !== card.type || old.key !== key) ops.push({ kind: 'UPSERT', id: card.id, type: card.type, position, content: normal.content, baseRevision: old.revision })
    else if (old.position !== position) ops.push({ kind: 'MOVE', id: card.id, position })
    next.cards.set(card.id, { type: card.type, key, position, revision: old?.revision ?? 0 })
  }
  const present = new Set(cards.map((c) => c.id))
  for (const [id, old] of saved.cards) if (!present.has(id)) ops.push({ kind: 'DELETE', id, baseRevision: old.revision })
  return { ...(title !== saved.title ? { title } : {}), ops, next, invalid }
}

export interface OpResult {
  id: string
  status: 'APPLIED' | 'APPLIED_WITH_CONFLICT' | 'REJECTED'
  revision: number | null
}

/** The saved state after the server answered a plan: applied cards take their new revision; rejected ones are dropped. */
export function afterSave(plan: SavePlan, results: OpResult[]): SavedState {
  const next: SavedState = { title: plan.next.title, cards: new Map(plan.next.cards) }
  const byId = new Map(results.map((r) => [r.id, r]))
  for (const op of plan.ops) {
    const r = byId.get(op.id)
    if (!r) continue
    if (r.status === 'REJECTED') {
      // A move of a card deleted elsewhere: forget it, so the next save recreates it. A refused delete: the card is
      // still on the server; forgetting it here stops the editor retrying, and a reload shows it again.
      next.cards.delete(op.id)
    } else if (op.kind !== 'DELETE' && r.revision !== null) {
      const card = next.cards.get(op.id)
      if (card) next.cards.set(op.id, { ...card, revision: r.revision })
    }
  }
  return next
}

/** The saved state of cards as they came from the server. */
export function savedStateOf(title: string, cards: { id: string; type: CardType; position: string; revision: number; content: unknown }[]): SavedState {
  return {
    title,
    cards: new Map(
      cards.map((c) => {
        // Through the editor and back, as local edits will be: an empty card the editor fills with an empty paragraph
        // must not look changed.
        const asEdited = nodeToCard(cardToNode(c)) ?? c
        const normal = normalise(asEdited)
        return [c.id, { type: c.type, key: contentKey(normal.ok ? normal.content : c.content), position: c.position, revision: c.revision }]
      }),
    ),
  }
}
