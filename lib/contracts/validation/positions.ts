// Copied from lvn-backend contracts/src/validation/positions.ts by scripts/contracts-sync.mjs — do not edit here.
/**
 * Card order as fractional indexes (§13.2): every card's `position` is a string key, and a card goes between two others
 * by taking a key between theirs — no renumbering, so devices that insert while offline never rewrite each other's
 * order, and a move is one write. Keys compare as plain strings (JavaScript `<`, Postgres `COLLATE "C"`); equal keys
 * from two devices are ordered by card id.
 *
 * The algorithm is David Greenspan's "Implementing Fractional Indexing", as in rocicorp/fractional-indexing (CC0):
 * an integer part whose first character encodes its length, then a fraction that never ends in the zero digit.
 */

const DIGITS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
const ZERO = DIGITS[0]!
const SMALLEST_INTEGER = `A${ZERO.repeat(26)}`

/** Longest key the API accepts; ordinary editing stays far below it. */
export const MAX_POSITION_LENGTH = 64

function midpoint(a: string, b: string | null): string {
  if (b !== null && a >= b) throw new Error(`${a} >= ${b}`)
  if (a.endsWith(ZERO) || (b !== null && b.endsWith(ZERO))) throw new Error('trailing zero')
  if (b !== null) {
    let n = 0
    while ((a[n] ?? ZERO) === b[n]) n++
    if (n > 0) return b.slice(0, n) + midpoint(a.slice(n), b.slice(n))
  }
  const digitA = a ? DIGITS.indexOf(a[0]!) : 0
  const digitB = b !== null ? DIGITS.indexOf(b[0]!) : DIGITS.length
  if (digitB - digitA > 1) return DIGITS[Math.round(0.5 * (digitA + digitB))]!
  if (b !== null && b.length > 1) return b.slice(0, 1)
  return DIGITS[digitA]! + midpoint(a.slice(1), null)
}

function integerLength(head: string): number {
  if (head >= 'a' && head <= 'z') return head.charCodeAt(0) - 'a'.charCodeAt(0) + 2
  if (head >= 'A' && head <= 'Z') return 'Z'.charCodeAt(0) - head.charCodeAt(0) + 2
  throw new Error(`invalid position head: ${head}`)
}

function integerPart(key: string): string {
  const length = integerLength(key[0] ?? '')
  if (length > key.length) throw new Error(`invalid position: ${key}`)
  return key.slice(0, length)
}

function validate(key: string): void {
  if (key === SMALLEST_INTEGER) throw new Error(`invalid position: ${key}`)
  for (const c of key) if (!DIGITS.includes(c)) throw new Error(`invalid position: ${key}`)
  const int = integerPart(key)
  if (key.slice(int.length).endsWith(ZERO)) throw new Error(`invalid position: ${key}`)
}

function increment(int: string): string | null {
  const [head, ...digits] = int.split('') as [string, ...string[]]
  let carry = true
  for (let i = digits.length - 1; carry && i >= 0; i--) {
    const d = DIGITS.indexOf(digits[i]!) + 1
    if (d === DIGITS.length) digits[i] = ZERO
    else {
      digits[i] = DIGITS[d]!
      carry = false
    }
  }
  if (!carry) return head + digits.join('')
  if (head === 'Z') return `a${ZERO}`
  if (head === 'z') return null
  const next = String.fromCharCode(head.charCodeAt(0) + 1)
  if (next > 'a') digits.push(ZERO)
  else digits.pop()
  return next + digits.join('')
}

function decrement(int: string): string | null {
  const [head, ...digits] = int.split('') as [string, ...string[]]
  let borrow = true
  for (let i = digits.length - 1; borrow && i >= 0; i--) {
    const d = DIGITS.indexOf(digits[i]!) - 1
    if (d === -1) digits[i] = DIGITS.at(-1)!
    else {
      digits[i] = DIGITS[d]!
      borrow = false
    }
  }
  if (!borrow) return head + digits.join('')
  if (head === 'a') return `Z${DIGITS.at(-1)!}`
  if (head === 'A') return null
  const prev = String.fromCharCode(head.charCodeAt(0) - 1)
  if (prev < 'Z') digits.push(DIGITS.at(-1)!)
  else digits.pop()
  return prev + digits.join('')
}

/** A key strictly between `a` and `b`; `null` means "the start" or "the end". */
export function positionBetween(a: string | null, b: string | null): string {
  if (a !== null) validate(a)
  if (b !== null) validate(b)
  if (a !== null && b !== null && a >= b) throw new Error(`${a} >= ${b}`)
  if (a === null) {
    if (b === null) return `a${ZERO}`
    const ib = integerPart(b)
    const fb = b.slice(ib.length)
    if (ib === SMALLEST_INTEGER) return ib + midpoint('', fb)
    if (ib < b) return ib
    const res = decrement(ib)
    if (res === null) throw new Error('cannot go before this position')
    return res
  }
  if (b === null) {
    const ia = integerPart(a)
    const next = increment(ia)
    return next === null ? ia + midpoint(a.slice(ia.length), null) : next
  }
  const ia = integerPart(a)
  const ib = integerPart(b)
  if (ia === ib) return ia + midpoint(a.slice(ia.length), b.slice(ib.length))
  const next = increment(ia)
  if (next === null) throw new Error('cannot go after this position')
  return next < b ? next : ia + midpoint(a.slice(ia.length), null)
}

/** `n` ascending keys between `a` and `b`, spread so later inserts stay short (imports, restores, pasted blocks). */
export function positionsBetween(a: string | null, b: string | null, n: number): string[] {
  if (n <= 0) return []
  if (n === 1) return [positionBetween(a, b)]
  if (b === null) {
    const keys = [positionBetween(a, null)]
    while (keys.length < n) keys.push(positionBetween(keys.at(-1)!, null))
    return keys
  }
  if (a === null) {
    const keys = [positionBetween(null, b)]
    while (keys.length < n) keys.push(positionBetween(null, keys.at(-1)!))
    return keys.reverse()
  }
  const mid = Math.floor(n / 2)
  const c = positionBetween(a, b)
  return [...positionsBetween(a, c, mid), c, ...positionsBetween(c, b, n - mid - 1)]
}

/** True for a key the API accepts. */
export function isValidPosition(key: unknown): key is string {
  if (typeof key !== 'string' || key.length === 0 || key.length > MAX_POSITION_LENGTH) return false
  try {
    validate(key)
    return true
  } catch {
    return false
  }
}
