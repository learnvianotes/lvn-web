'use client'

import 'pdfjs-dist/web/pdf_viewer.css'
import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react'
import { cn } from '@/lib/cn'
import { areaRect, hits, quoteOf, selectionRects, type PageRect } from './geometry'
import { pdfSource } from './ranges'

/**
 * A PDF on the page (lvn-backend ADR-0040): pdf.js's own viewer — pages rendered as you scroll, a text layer to
 * select and find words, links, zoom and pinch — with our marks drawn over each page: highlights, the passages cards
 * were made from, and the area being snipped. It reports what the reader selects or snips; the page decides what to
 * do with it.
 */

type PdfJs = typeof import('pdfjs-dist')
type ViewerModule = typeof import('pdfjs-dist/web/pdf_viewer.mjs')
type Viewer = InstanceType<ViewerModule['PDFViewer']>
type Bus = InstanceType<ViewerModule['EventBus']>
type Doc = Awaited<ReturnType<PdfJs['getDocument']>['promise']>
type PageView = { div: HTMLDivElement; viewport: { width: number; height: number; convertToPdfPoint: (x: number, y: number) => number[] } }

export interface Mark {
  id: string
  page: number
  rects: PageRect[]
  /** highlight: a coloured passage or area; anchor: where a card came from; pending: the snip waiting for a choice */
  kind: 'highlight' | 'anchor' | 'pending'
  color?: string
}

export interface OutlineItem {
  title: string
  dest: unknown
  items: OutlineItem[]
}

export interface TextSelection {
  page: number
  rects: PageRect[]
  quote: string
  /** Where to show actions, in the window */
  at: { x: number; y: number }
}

export interface AreaSelection {
  page: number
  rect: PageRect
  at: { x: number; y: number }
}

export interface PdfViewerHandle {
  /** Scrolls to a page, to a passage on it when given, and makes the passage flash */
  goTo(page: number, rects?: PageRect[]): void
  zoom(to: 'in' | 'out' | 'width' | 'page'): void
  find(query: string, direction?: 'next' | 'previous'): void
  goToDest(dest: unknown): void
  /** A picture of an area of a page, sharp enough for a note */
  crop(page: number, rect: PageRect): Promise<Blob>
  clearSelection(): void
}

export interface PdfViewerProps {
  url: string
  /** A new URL for the same file when the old one has expired (lvn-backend ADR-0090) */
  refreshUrl: () => Promise<string | null>
  marks: Mark[]
  initialPage?: number
  snipping: boolean
  className?: string
  onLoaded: (info: { pages: number; outline: OutlineItem[] }) => void
  onPage: (page: number) => void
  onScale: (percent: number) => void
  onSelection: (selection: TextSelection | null) => void
  onArea: (area: AreaSelection) => void
  onMark: (id: string, at: { x: number; y: number }) => void
  onFind: (result: { current: number; total: number } | null) => void
  onError: (kind: 'load' | 'password') => void
}

const FLASH_MS = 1800

export const PdfViewer = forwardRef<PdfViewerHandle, PdfViewerProps>(function PdfViewer(props, ref) {
  const { url, marks, snipping, className } = props
  // The file, not its URL: a fresh URL for the same file (its signature renewed) must not reload the document.
  const fileKey = url.split('?')[0]
  const container = useRef<HTMLDivElement>(null)
  const inner = useRef<HTMLDivElement>(null)
  const state = useRef<{ viewer: Viewer | null; bus: Bus | null; doc: Doc | null; links: InstanceType<ViewerModule['PDFLinkService']> | null }>({ viewer: null, bus: null, doc: null, links: null })
  const latest = useRef(props)
  latest.current = props
  const flash = useRef<{ page: number; rects: PageRect[]; until: number } | null>(null)

  /** Draws the marks of one page into its layer; pdf.js clears the page when it renders it again. */
  const draw = (page: number) => {
    const view = state.current.viewer?.getPageView(page - 1) as PageView | undefined
    if (!view?.div) return
    let layer = view.div.querySelector<HTMLDivElement>(':scope > .lvn-marks')
    if (!layer) {
      layer = document.createElement('div')
      layer.className = 'lvn-marks'
      view.div.append(layer)
    }
    const boxes = latest.current.marks
      .filter((m) => m.page === page)
      .flatMap((m) => m.rects.map((r) => ({ r, className: `lvn-mark lvn-mark-${m.kind}`, color: m.color, id: m.id })))
    const lit = flash.current && flash.current.page === page && flash.current.until > Date.now() ? flash.current.rects.map((r) => ({ r, className: 'lvn-mark lvn-mark-flash', color: undefined, id: '' })) : []
    layer.replaceChildren(
      ...[...boxes, ...lit].map(({ r: [x0, y0, x1, y1], className: name, color, id }) => {
        const box = document.createElement('div')
        box.className = name
        if (color) box.dataset.color = color
        if (id) box.dataset.mark = id
        box.style.cssText = `left:${x0 * 100}%;top:${y0 * 100}%;width:${(x1 - x0) * 100}%;height:${(y1 - y0) * 100}%`
        return box
      }),
    )
  }
  const drawAll = () => {
    const pages = state.current.viewer?.pagesCount ?? 0
    for (let p = 1; p <= pages; p++) draw(p)
  }

  // ── Loading ─────────────────────────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false
    let task: { destroy: () => Promise<void> } | null = null
    const pagesBox = inner.current
    void (async () => {
      const pdfjs: PdfJs = await import('pdfjs-dist')
      // The viewer reads the library from globalThis.pdfjsLib, which importing it sets.
      const ui: ViewerModule = await import('pdfjs-dist/web/pdf_viewer.mjs')
      if (cancelled || !container.current || !inner.current) return
      const assets = `/pdfjs/${pdfjs.version}/`
      pdfjs.GlobalWorkerOptions.workerSrc = `${assets}pdf.worker.min.mjs`
      const bus = new ui.EventBus()
      const links = new ui.PDFLinkService({ eventBus: bus, externalLinkTarget: ui.LinkTarget.BLANK, externalLinkRel: 'noopener noreferrer nofollow' })
      const finder = new ui.PDFFindController({ eventBus: bus, linkService: links })
      const viewer = new ui.PDFViewer({
        container: container.current,
        viewer: inner.current,
        eventBus: bus,
        linkService: links,
        findController: finder,
        textLayerMode: 1,
        annotationMode: pdfjs.AnnotationMode.ENABLE,
        annotationEditorMode: pdfjs.AnnotationEditorType.DISABLE,
      })
      links.setViewer(viewer)
      state.current = { viewer, bus, doc: null, links }

      bus.on('pagesinit', () => {
        viewer.currentScaleValue = window.innerWidth < 640 ? 'page-width' : 'auto'
        const start = latest.current.initialPage
        if (start && start > 1) viewer.currentPageNumber = Math.min(start, viewer.pagesCount)
      })
      bus.on('pagechanging', (e: { pageNumber: number }) => latest.current.onPage(e.pageNumber))
      bus.on('scalechanging', (e: { scale: number }) => latest.current.onScale(Math.round(e.scale * 100)))
      bus.on('pagerendered', (e: { pageNumber: number }) => draw(e.pageNumber))
      bus.on('updatefindmatchescount', (e: { matchesCount: { current: number; total: number } }) => latest.current.onFind(e.matchesCount))
      bus.on('updatefindcontrolstate', (e: { state: number; matchesCount: { current: number; total: number } }) => {
        // FindState.NOT_FOUND
        if (e.state === 1) latest.current.onFind({ current: 0, total: 0 })
        else if (e.matchesCount) latest.current.onFind(e.matchesCount)
      })

      // In ranges, with a fresh URL whenever the 15-minute one expires (ADR-0090).
      const source = await pdfSource(pdfjs, latest.current.url, () => latest.current.refreshUrl())
      if (cancelled) return
      const loading = pdfjs.getDocument({
        ...source,
        cMapUrl: `${assets}cmaps/`,
        cMapPacked: true,
        standardFontDataUrl: `${assets}standard_fonts/`,
        wasmUrl: `${assets}wasm/`,
        iccUrl: `${assets}iccs/`,
        enableXfa: false,
      })
      task = loading
      loading.onPassword = (answer: (password: string) => void, reason: number) => {
        const password = window.prompt(reason === 2 ? 'That password is not right. Password for this PDF:' : 'This PDF needs a password:')
        if (password === null) {
          latest.current.onError('password')
          void loading.destroy()
        } else answer(password)
      }
      try {
        const doc = await loading.promise
        if (cancelled) return
        state.current.doc = doc
        viewer.setDocument(doc)
        links.setDocument(doc)
        const outline = ((await doc.getOutline().catch(() => null)) ?? []) as { title: string; dest: unknown; items: unknown[] }[]
        const shape = (items: { title: string; dest: unknown; items: unknown[] }[], depth: number): OutlineItem[] =>
          items.slice(0, 500).map((i) => ({ title: i.title, dest: i.dest, items: depth < 3 ? shape(i.items as never, depth + 1) : [] }))
        if (!cancelled) latest.current.onLoaded({ pages: doc.numPages, outline: shape(outline, 0) })
      } catch (e) {
        if (!cancelled && (e as { name?: string }).name !== 'PasswordException') latest.current.onError('load')
      }
    })()
    return () => {
      cancelled = true
      void task?.destroy()
      state.current.viewer?.cleanup()
      state.current = { viewer: null, bus: null, doc: null, links: null }
      pagesBox?.replaceChildren()
    }
  }, [fileKey])

  // Marks change as highlights and cards come and go.
  useEffect(drawAll, [marks])

  // ── Selecting text ──────────────────────────────────────────────────────────────────────────────────────────
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined
    const read = () => {
      const sel = document.getSelection()
      const box = container.current
      if (!box || !sel || sel.isCollapsed || !sel.rangeCount) return latest.current.onSelection(null)
      const range = sel.getRangeAt(0)
      if (!box.contains(range.commonAncestorContainer)) return latest.current.onSelection(null)
      const start = range.startContainer.nodeType === Node.ELEMENT_NODE ? (range.startContainer as Element) : range.startContainer.parentElement
      const pageEl = start?.closest<HTMLElement>('.page')
      const surface = pageEl?.querySelector('.textLayer') ?? pageEl?.querySelector('.canvasWrapper')
      if (!pageEl || !surface) return latest.current.onSelection(null)
      const page = surface.getBoundingClientRect()
      const rects = selectionRects(range.getClientRects(), page)
      const quote = quoteOf(sel.toString())
      if (!rects.length || !quote) return latest.current.onSelection(null)
      const last = rects[rects.length - 1]!
      latest.current.onSelection({ page: Number(pageEl.dataset.pageNumber), rects, quote, at: { x: page.left + ((last[0] + last[2]) / 2) * page.width, y: page.top + last[3] * page.height } })
    }
    const soon = () => {
      clearTimeout(timer)
      timer = setTimeout(read, 150)
    }
    document.addEventListener('selectionchange', soon)
    const box = container.current
    box?.addEventListener('scroll', soon, { passive: true })
    return () => {
      clearTimeout(timer)
      document.removeEventListener('selectionchange', soon)
      box?.removeEventListener('scroll', soon)
    }
  }, [])

  // ── Clicking marks, and snipping areas ──────────────────────────────────────────────────────────────────────
  useEffect(() => {
    const box = container.current
    if (!box) return
    const placeOn = (e: PointerEvent | MouseEvent) => {
      const pageEl = (e.target as Element | null)?.closest<HTMLElement>('.page')
      const surface = pageEl?.querySelector('.textLayer') ?? pageEl?.querySelector('.canvasWrapper')
      if (!pageEl || !surface) return null
      const rect = surface.getBoundingClientRect()
      return { pageEl, page: Number(pageEl.dataset.pageNumber), rect, x: (e.clientX - rect.left) / rect.width, y: (e.clientY - rect.top) / rect.height }
    }
    const onClick = (e: MouseEvent) => {
      if (latest.current.snipping) return
      const sel = document.getSelection()
      if (sel && !sel.isCollapsed) return
      const at = placeOn(e)
      if (!at) return
      const hit = latest.current.marks
        .filter((m) => m.page === at.page && m.kind !== 'pending' && hits(m.rects, at.x, at.y))
        // The smallest mark under the pointer; highlights before card anchors.
        .sort((a, b) => (a.kind === b.kind ? area(a.rects) - area(b.rects) : a.kind === 'highlight' ? -1 : 1))[0]
      if (hit) latest.current.onMark(hit.id, { x: e.clientX, y: e.clientY })
    }
    let snip: { page: number; pageEl: HTMLElement; rect: DOMRect; from: { x: number; y: number }; box: HTMLDivElement; pointer: number } | null = null
    const onDown = (e: PointerEvent) => {
      if (!latest.current.snipping || e.button > 0) return
      const at = placeOn(e)
      if (!at) return
      e.preventDefault()
      box.setPointerCapture(e.pointerId)
      const drawn = document.createElement('div')
      drawn.className = 'lvn-snip-box'
      at.pageEl.append(drawn)
      snip = { page: at.page, pageEl: at.pageEl, rect: at.rect, from: { x: at.x, y: at.y }, box: drawn, pointer: e.pointerId }
    }
    const current = (e: PointerEvent) => (snip ? areaRect(snip.from, { x: (e.clientX - snip.rect.left) / snip.rect.width, y: (e.clientY - snip.rect.top) / snip.rect.height }) : null)
    const onMove = (e: PointerEvent) => {
      const r = current(e)
      if (!snip || !r) return
      const surface = snip.pageEl.querySelector<HTMLElement>('.textLayer') ?? snip.pageEl
      // Placed like the marks: against the page surface inside the page's border.
      snip.box.style.cssText = `left:${surface.offsetLeft + r[0] * snip.rect.width}px;top:${surface.offsetTop + r[1] * snip.rect.height}px;width:${(r[2] - r[0]) * snip.rect.width}px;height:${(r[3] - r[1]) * snip.rect.height}px`
    }
    const onUp = (e: PointerEvent) => {
      const r = current(e)
      if (!snip || !r) return
      snip.box.remove()
      box.releasePointerCapture(snip.pointer)
      const done = snip
      snip = null
      if (r[2] - r[0] < 0.02 || r[3] - r[1] < 0.01) return
      latest.current.onArea({ page: done.page, rect: r, at: { x: done.rect.left + r[2] * done.rect.width, y: done.rect.top + r[3] * done.rect.height } })
    }
    box.addEventListener('click', onClick)
    box.addEventListener('pointerdown', onDown)
    box.addEventListener('pointermove', onMove)
    box.addEventListener('pointerup', onUp)
    box.addEventListener('pointercancel', onUp)
    return () => {
      box.removeEventListener('click', onClick)
      box.removeEventListener('pointerdown', onDown)
      box.removeEventListener('pointermove', onMove)
      box.removeEventListener('pointerup', onUp)
      box.removeEventListener('pointercancel', onUp)
    }
  }, [])

  useImperativeHandle(
    ref,
    () => ({
      goTo(page, rects) {
        const viewer = state.current.viewer
        if (!viewer || page < 1 || page > viewer.pagesCount) return
        const view = viewer.getPageView(page - 1) as PageView | undefined
        if (rects?.length && view?.viewport) {
          const top = Math.min(...rects.map((r) => r[1]))
          const left = Math.min(...rects.map((r) => r[0]))
          const [x, y] = view.viewport.convertToPdfPoint(left * view.viewport.width, Math.max(0, top - 0.04) * view.viewport.height)
          viewer.scrollPageIntoView({ pageNumber: page, destArray: [null, { name: 'XYZ' }, x, y, null], allowNegativeOffset: true })
          flash.current = { page, rects, until: Date.now() + FLASH_MS }
          draw(page)
          setTimeout(() => draw(page), FLASH_MS + 50)
        } else viewer.currentPageNumber = page
      },
      zoom(to) {
        const viewer = state.current.viewer
        if (!viewer) return
        if (to === 'in') viewer.increaseScale()
        else if (to === 'out') viewer.decreaseScale()
        else viewer.currentScaleValue = to === 'width' ? 'page-width' : 'page-fit'
      },
      find(query, direction) {
        if (!query.trim()) {
          state.current.bus?.dispatch('findbarclose', { source: null })
          latest.current.onFind(null)
          return
        }
        state.current.bus?.dispatch('find', { source: null, type: direction ? 'again' : '', query, caseSensitive: false, entireWord: false, highlightAll: true, findPrevious: direction === 'previous', matchDiacritics: false })
      },
      goToDest(dest) {
        void state.current.links?.goToDestination(dest as never)
      },
      async crop(page, rect) {
        const doc = state.current.doc
        if (!doc) throw new Error('no document')
        const pdfPage = await doc.getPage(page)
        const base = pdfPage.getViewport({ scale: 1 })
        const width = (rect[2] - rect[0]) * base.width
        const height = (rect[3] - rect[1]) * base.height
        // About 1,400 pixels across, at least 1.5× and at most 4× the page's size.
        const scale = Math.min(4, Math.max(1.5, 1400 / Math.max(width, 1)))
        const viewport = pdfPage.getViewport({ scale })
        const canvas = document.createElement('canvas')
        canvas.width = Math.max(1, Math.round(width * scale))
        canvas.height = Math.max(1, Math.round(height * scale))
        await pdfPage.render({ canvas, viewport, transform: [1, 0, 0, 1, -rect[0] * viewport.width, -rect[1] * viewport.height] }).promise
        return new Promise<Blob>((resolve, reject) => canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('crop failed'))), 'image/png'))
      },
      clearSelection() {
        document.getSelection()?.removeAllRanges()
      },
    }),
    [],
  )

  return (
    <div ref={container} className={cn('lvn-pdf absolute inset-0 overflow-auto', snipping && 'lvn-snipping', className)} data-testid="pdf-viewer">
      <div ref={inner} className="pdfViewer" />
    </div>
  )
})

const area = (rects: PageRect[]) => rects.reduce((n, [x0, y0, x1, y1]) => n + (x1 - x0) * (y1 - y0), 0)
