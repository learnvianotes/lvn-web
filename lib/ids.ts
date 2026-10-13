/**
 * A UUIDv7 (lvn-backend §4.6), made in the browser for things that must keep their id offline: cards, learning events.
 * Built on crypto.getRandomValues, which — unlike crypto.randomUUID — also works on plain-HTTP origins (the dev
 * machine's address, the local environment).
 */
export function newId(now: number = Date.now()): string {
  const b = new Uint8Array(16)
  crypto.getRandomValues(b)
  let ms = now
  for (let i = 5; i >= 0; i--) {
    b[i] = ms % 256
    ms = Math.floor(ms / 256)
  }
  b[6] = 0x70 | (b[6]! & 0x0f)
  b[8] = 0x80 | (b[8]! & 0x3f)
  const h = Array.from(b, (x) => x.toString(16).padStart(2, '0')).join('')
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`
}
