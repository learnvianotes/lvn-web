import { safeLinkHref } from '@/lib/http-url'

/** A page of a note: ink strokes and placed pictures, in page units (0–1). */

export type DrawTool = 'pen' | 'marker' | 'eraser' | 'ruler'

export interface InkPoint {
  /** 0–1 across the page */
  x: number
  /** 0–1 down the page */
  y: number
  /** 0–1. A mouse reports 0; callers should store 0.5 for it. */
  p: number
}

export interface Stroke {
  id: string
  tool: 'pen' | 'marker'
  color: string
  /** Width in viewBox units (the page is 100×100). */
  width: number
  points: InkPoint[]
  straight?: boolean
}

export interface PageImage {
  id: string
  name: string
  href: string
  /** Set after createUploadIntent purpose PAGE_IMAGE accepts the bytes. */
  fileId?: string
  x: number
  y: number
  w: number
  h: number
  /** Degrees clockwise */
  rotation: number
}

export interface NotePage {
  id: string
  strokes: Stroke[]
  images: PageImage[]
  /** Server field returned beside strokes (contracts 0.74.0). Round-tripped on save. */
  drawing?: unknown
}

export interface PageHistory {
  past: NotePage[][]
  present: NotePage[]
  future: NotePage[][]
}

const NEAR = 0.035

export function newPageId(): string {
  return crypto.randomUUID()
}

export function blankPage(): NotePage {
  return { id: newPageId(), strokes: [], images: [] }
}

export function historyOf(pages: NotePage[]): PageHistory {
  return { past: [], present: pages.length ? pages : [blankPage()], future: [] }
}

export function commit(history: PageHistory, present: NotePage[]): PageHistory {
  if (samePages(history.present, present)) return history
  return { past: [...history.past, history.present].slice(-40), present, future: [] }
}

export function undo(history: PageHistory): PageHistory {
  const prev = history.past.at(-1)
  if (!prev) return history
  return { past: history.past.slice(0, -1), present: prev, future: [history.present, ...history.future] }
}

export function redo(history: PageHistory): PageHistory {
  const next = history.future[0]
  if (!next) return history
  return { past: [...history.past, history.present], present: next, future: history.future.slice(1) }
}

export function pressureOf(reported: number): number {
  if (!Number.isFinite(reported) || reported <= 0) return 0.5
  return Math.min(1, reported)
}

export function clamp01(n: number): number {
  if (!Number.isFinite(n)) return 0
  return Math.min(1, Math.max(0, n))
}

export function addStroke(page: NotePage, stroke: Stroke): NotePage {
  return { ...page, strokes: [...page.strokes, stroke] }
}

/** A ruler stroke is the straight segment from the first point to the last. */
export function straighten(stroke: Stroke): Stroke {
  if (stroke.points.length < 2) return { ...stroke, straight: true }
  const a = stroke.points[0]!
  const b = stroke.points[stroke.points.length - 1]!
  return { ...stroke, points: [a, b], straight: true }
}

/** Portion of the page the ruler spans, as a whole percent of the page width. */
export function scalePercent(stroke: Stroke): number | null {
  if (!stroke.straight || stroke.points.length < 2) return null
  const a = stroke.points[0]!
  const b = stroke.points[stroke.points.length - 1]!
  return Math.round(Math.hypot(b.x - a.x, b.y - a.y) * 100)
}

export function eraseAt(page: NotePage, at: InkPoint): NotePage {
  return {
    ...page,
    strokes: page.strokes.filter((stroke) => !stroke.points.some((point) => Math.hypot(point.x - at.x, point.y - at.y) <= NEAR)),
  }
}

export function insertImage(page: NotePage, image: PageImage): NotePage {
  return { ...page, images: [...page.images, image] }
}

export function updateImage(page: NotePage, id: string, patch: Partial<Pick<PageImage, 'x' | 'y' | 'w' | 'h' | 'rotation' | 'fileId' | 'href'>>): NotePage {
  return {
    ...page,
    images: page.images.map((image) => {
      if (image.id !== id) return image
      const next = { ...image, ...patch }
      next.w = Math.min(1, Math.max(0.08, next.w))
      next.h = Math.min(1, Math.max(0.08, next.h))
      next.x = clamp01(next.x)
      next.y = clamp01(next.y)
      next.rotation = ((next.rotation % 360) + 360) % 360
      return next
    }),
  }
}

export function removeImage(page: NotePage, id: string): NotePage {
  return { ...page, images: page.images.filter((image) => image.id !== id) }
}

export function updatePage(pages: NotePage[], index: number, edit: (page: NotePage) => NotePage): NotePage[] {
  return pages.map((page, i) => (i === index ? edit(page) : page))
}

const INK = /^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$/
const DATA_IMAGE = /^data:image\/(?:png|jpeg|webp|gif);base64,[a-z0-9+/]+=*$/i

/** A colour safe to put on an SVG stroke. Anything else (a url(), a script) is the pen default. */
export function inkColor(color: string, fallback = '#1d4ed8'): string {
  return INK.test(color) ? color : fallback
}

/**
 * A page picture safe to use as an img src: a data URL this editor made, a blob preview, or an http(s) read URL.
 */
export function pageImageSrc(href: string): string | null {
  if (DATA_IMAGE.test(href)) return href
  if (href.startsWith('blob:') && !/[\s<>"']/.test(href)) return href
  return safeLinkHref(href)
}

/** SVG path in a 100×100 viewBox. Ruler strokes ignore the in-between points. */
export function strokePath(stroke: Stroke): string {
  const points = stroke.straight && stroke.points.length >= 2 ? [stroke.points[0]!, stroke.points[stroke.points.length - 1]!] : stroke.points
  if (!points.length) return ''
  return points.map((point, i) => `${i === 0 ? 'M' : 'L'} ${(point.x * 100).toFixed(2)} ${(point.y * 100).toFixed(2)}`).join(' ')
}

export function strokeWidth(stroke: Stroke): number {
  const pressure = stroke.points.reduce((sum, point) => sum + pressureOf(point.p), 0) / Math.max(1, stroke.points.length)
  return stroke.width * (0.45 + pressure)
}

export interface RgbaRect {
  x: number
  y: number
  w: number
  h: number
}

/** Contrast and a small brightness lift. Alpha is copied. */
export function enhanceRgba(data: Uint8ClampedArray, contrast = 1.35, brightness = 12): Uint8ClampedArray {
  const out = new Uint8ClampedArray(data.length)
  for (let i = 0; i < data.length; i += 4) {
    for (let channel = 0; channel < 3; channel++) {
      const value = data[i + channel] ?? 0
      out[i + channel] = clampByte((value - 128) * contrast + 128 + brightness)
    }
    out[i + 3] = data[i + 3] ?? 255
  }
  return out
}

export function cropRgba(data: Uint8ClampedArray, width: number, height: number, rect: RgbaRect): { data: Uint8ClampedArray; width: number; height: number } {
  const x = clampInt(rect.x, 0, Math.max(0, width - 1))
  const y = clampInt(rect.y, 0, Math.max(0, height - 1))
  const w = clampInt(rect.w, 1, width - x)
  const h = clampInt(rect.h, 1, height - y)
  const out = new Uint8ClampedArray(w * h * 4)
  for (let row = 0; row < h; row++) {
    const from = ((y + row) * width + x) * 4
    out.set(data.subarray(from, from + w * 4), row * w * 4)
  }
  return { data: out, width: w, height: h }
}

export function pagesFromUnknown(value: unknown): NotePage[] | null {
  if (!Array.isArray(value)) return null
  const pages: NotePage[] = []
  for (const item of value) {
    const page = pageFromUnknown(item)
    if (!page) return null
    pages.push(page)
  }
  return pages
}

function pageFromUnknown(value: unknown): NotePage | null {
  if (!value || typeof value !== 'object') return null
  const page = value as NotePage
  if (typeof page.id !== 'string' || !Array.isArray(page.strokes)) return null
  const strokes = page.strokes.filter(isStroke).map((stroke) => ({
    ...stroke,
    points: stroke.points.map((point) => ({ x: point.x, y: point.y, p: typeof point.p === 'number' ? point.p : 0.5 })),
  }))
  if (strokes.length !== page.strokes.length) return null
  const images = Array.isArray(page.images) ? page.images.filter(isImage) : []
  return { id: page.id, strokes, images, drawing: page.drawing ?? null }
}

function isStroke(value: unknown): value is Stroke {
  if (!value || typeof value !== 'object') return false
  const stroke = value as Stroke
  return (stroke.tool === 'pen' || stroke.tool === 'marker') && typeof stroke.id === 'string' && typeof stroke.color === 'string' && typeof stroke.width === 'number' && Array.isArray(stroke.points) && stroke.points.every(isPoint)
}

function isImage(value: unknown): value is PageImage {
  if (!value || typeof value !== 'object') return false
  const image = value as PageImage
  return typeof image.id === 'string' && typeof image.href === 'string' && [image.x, image.y, image.w, image.h, image.rotation].every((n) => typeof n === 'number')
}

function isPoint(value: unknown): value is InkPoint {
  if (!value || typeof value !== 'object') return false
  const point = value as Partial<InkPoint>
  // StrokePoint on the server is x and y. Pressure stays on the device while drawing.
  return typeof point.x === 'number' && Number.isFinite(point.x) && typeof point.y === 'number' && Number.isFinite(point.y) && (point.p === undefined || (typeof point.p === 'number' && Number.isFinite(point.p)))
}

/** A page as Note.pages returns it. Pressure is not stored, so loaded ink uses a medium stroke. */
export function pagesFromServer(pages: ReadonlyArray<{
  id: string
  strokes: ReadonlyArray<{ id: string; tool: string; color: string | null; width: number; points: ReadonlyArray<{ x: number; y: number }> }>
  images: ReadonlyArray<{ id: string; fileId: string; href: string | null; name: string; x: number; y: number; w: number; h: number; rotation: number }>
}>): NotePage[] {
  return pages.map((page) => ({
    id: page.id,
    strokes: page.strokes.flatMap((stroke) => {
      const tool = stroke.tool === 'MARKER' || stroke.tool === 'marker' ? 'marker' : stroke.tool === 'ERASER' || stroke.tool === 'eraser' ? null : 'pen'
      if (!tool) return []
      return [{
        id: stroke.id,
        tool,
        color: stroke.color ?? (tool === 'marker' ? '#0284c7' : '#1d4ed8'),
        width: stroke.width,
        straight: stroke.tool === 'RULER' || stroke.tool === 'ruler',
        points: stroke.points.map((point) => ({ x: point.x, y: point.y, p: 0.5 })),
      }]
    }),
    images: page.images.map((image) => ({
      id: image.id,
      fileId: image.fileId,
      name: image.name,
      href: image.href ?? '',
      x: image.x,
      y: image.y,
      w: image.w,
      h: image.h,
      rotation: image.rotation,
    })),
  }))
}

/** SaveNotePages input. Points are x and y; a ruler stroke is stored as tool ruler. */
export function pagesToSave(noteId: string, pages: NotePage[]) {
  return {
    noteId,
    pages: pages.map((page, index) => ({
      id: page.id,
      index,
      drawing: {
        strokes: page.strokes.map((stroke) => ({
          id: stroke.id,
          tool: stroke.straight ? 'ruler' : stroke.tool,
          color: stroke.color,
          width: stroke.width,
          points: stroke.points.map(({ x, y }) => ({ x, y })),
        })),
      },
      images: page.images.flatMap((image) => (
        image.fileId
          ? [{ id: image.id, fileId: image.fileId, name: image.name, x: image.x, y: image.y, w: image.w, h: image.h, rotation: image.rotation }]
          : []
      )),
    })),
  }
}

function samePages(a: NotePage[], b: NotePage[]): boolean {
  return JSON.stringify(a) === JSON.stringify(b)
}

function clampByte(n: number): number {
  return Math.min(255, Math.max(0, Math.round(n)))
}

function clampInt(n: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, Math.round(n)))
}
