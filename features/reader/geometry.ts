import { CARD_LIMITS } from '@/lib/contracts/validation'

/**
 * Places on a PDF page (lvn-backend ADR-0040): rectangles as fractions of the page's width and height from its top
 * left, `[x0, y0, x1, y1]` — the same at every zoom, on every screen, and what the API stores for anchors and
 * highlights.
 */
export type PageRect = [number, number, number, number]

export interface Box {
  left: number
  top: number
  width: number
  height: number
}

const round = (n: number) => Math.round(n * 100_000) / 100_000
const clamp = (n: number) => Math.min(1, Math.max(0, n))

/** One screen rectangle as a page rectangle, or null when it misses the page or is too small to mean anything. */
export function toPageRect(r: { left: number; top: number; right: number; bottom: number }, page: Box): PageRect | null {
  if (r.right - r.left < 1 || r.bottom - r.top < 1) return null
  const x0 = clamp((r.left - page.left) / page.width)
  const y0 = clamp((r.top - page.top) / page.height)
  const x1 = clamp((r.right - page.left) / page.width)
  const y1 = clamp((r.bottom - page.top) / page.height)
  if (x1 - x0 <= 0 || y1 - y0 <= 0) return null
  return [round(x0), round(y0), round(x1), round(y1)]
}

/**
 * The rectangles of a text selection on one page, one per line: the browser gives a rectangle per text span, often
 * overlapping, plus odd tall ones for line ends; spans on the same line become one rectangle.
 */
export function selectionRects(clientRects: Iterable<{ left: number; top: number; right: number; bottom: number }>, page: Box): PageRect[] {
  const rects = [...clientRects]
    .map((r) => toPageRect(r, page))
    .filter((r): r is PageRect => r !== null && r[3] - r[1] < 0.15)
    .sort((a, b) => a[1] + a[3] - (b[1] + b[3]) || a[0] - b[0])
  const lines: PageRect[] = []
  for (const r of rects) {
    const line = lines.find((l) => {
      const overlap = Math.min(l[3], r[3]) - Math.max(l[1], r[1])
      return overlap > 0.5 * Math.min(l[3] - l[1], r[3] - r[1])
    })
    if (line) {
      line[0] = Math.min(line[0], r[0])
      line[1] = Math.min(line[1], r[1])
      line[2] = Math.max(line[2], r[2])
      line[3] = Math.max(line[3], r[3])
    } else lines.push([...r])
  }
  return lines.sort((a, b) => a[1] - b[1]).slice(0, CARD_LIMITS.anchorRects)
}

/** The area between two points on a page (a snip), inside the page. */
export function areaRect(a: { x: number; y: number }, b: { x: number; y: number }): PageRect {
  return [round(clamp(Math.min(a.x, b.x))), round(clamp(Math.min(a.y, b.y))), round(clamp(Math.max(a.x, b.x))), round(clamp(Math.max(a.y, b.y)))]
}

/** Whether a point of the page falls in one of the rectangles (with a little slack for thin lines). */
export function hits(rects: PageRect[], x: number, y: number, slack = 0.003): boolean {
  return rects.some(([x0, y0, x1, y1]) => x >= x0 - slack && x <= x1 + slack && y >= y0 - slack && y <= y1 + slack)
}

/** The words of a selection as a quote: lines joined, words split at a line end mended, at most the anchor limit. */
export function quoteOf(text: string): string {
  return text
    .replace(/(\p{Ll})-\s*\n\s*(\p{Ll})/gu, '$1$2')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, CARD_LIMITS.anchorQuote)
}
