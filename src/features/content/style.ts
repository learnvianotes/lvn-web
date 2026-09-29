/* "display: flex; gap: 8px" → { display: 'flex', gap: '8px' } for React. */

import type { CSSProperties } from 'react'

const cache = new Map<string, CSSProperties>()

export function parseStyle(style: string): CSSProperties {
  let out = cache.get(style)
  if (out) return out
  const obj: Record<string, string> = {}
  for (const decl of style.split(';')) {
    const i = decl.indexOf(':')
    if (i < 0) continue
    const prop = decl.slice(0, i).trim()
    const value = decl.slice(i + 1).trim()
    if (!prop || !value) continue
    obj[prop.startsWith('--') ? prop : prop.replace(/-([a-z])/g, (_, c: string) => c.toUpperCase())] = value
  }
  out = obj as CSSProperties
  cache.set(style, out)
  return out
}
