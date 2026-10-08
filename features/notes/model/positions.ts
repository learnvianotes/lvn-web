import { positionsBetween } from '@/lib/contracts/validation'

/**
 * Positions for the cards in their new order. Cards keep their stored position where they can — the longest run of
 * cards still in ascending order stays put — and only new or moved cards get a new key between their neighbours, so a
 * save sends as few moves as possible.
 */
export function assignPositions(items: { id: string; position: string | null }[]): Map<string, string> {
  const kept = longestAscending(items)
  const result = new Map<string, string>()
  let i = 0
  while (i < items.length) {
    if (kept.has(i)) {
      result.set(items[i]!.id, items[i]!.position!)
      i++
      continue
    }
    const start = i
    while (i < items.length && !kept.has(i)) i++
    const before = start > 0 ? result.get(items[start - 1]!.id)! : null
    const after = i < items.length ? items[i]!.position! : null
    const keys = positionsBetween(before, after, i - start)
    for (let k = start; k < i; k++) result.set(items[k]!.id, keys[k - start]!)
  }
  return result
}

/** Indexes of a longest strictly ascending subsequence of the stored positions (O(n log n)). */
function longestAscending(items: { position: string | null }[]): Set<number> {
  const tails: number[] = []
  const prev = new Array<number>(items.length).fill(-1)
  items.forEach((item, i) => {
    const p = item.position
    if (p === null) return
    let lo = 0
    let hi = tails.length
    while (lo < hi) {
      const mid = (lo + hi) >> 1
      if (items[tails[mid]!]!.position! < p) lo = mid + 1
      else hi = mid
    }
    if (lo > 0) prev[i] = tails[lo - 1]!
    tails[lo] = i
  })
  const keep = new Set<number>()
  for (let at = tails.at(-1) ?? -1; at !== -1; at = prev[at]!) keep.add(at)
  return keep
}
