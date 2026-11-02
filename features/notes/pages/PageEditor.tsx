'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { Camera, Eraser, ImagePlus, Pen, Redo2, Ruler, Trash2, Undo2 } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { uploadPageImage } from '@/features/beta/api'
import { NotePagesDocument, SaveNotePagesDocument } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { PhotoScan } from './PhotoScan'
import {
  addStroke,
  blankPage,
  clamp01,
  commit,
  eraseAt,
  historyOf,
  insertImage,
  pagesFromServer,
  pagesToSave,
  newPageId,
  pressureOf,
  redo,
  removeImage,
  scalePercent,
  straighten,
  strokePath,
  strokeWidth,
  undo,
  updateImage,
  updatePage,
  type DrawTool,
  type InkPoint,
  type NotePage,
  type PageHistory,
  type Stroke,
} from './model'

const PEN = '#1d4ed8'
const MARKER = '#0284c7'

/**
 * Page-based drawing on a note: pen, marker, eraser and a ruler, plus pictures that move, resize and rotate.
 * Pointer events carry pressure (a mouse is treated as 0.5) and work with a finger or a stylus.
 */
export function PageEditor({ noteId }: { noteId: string }) {
  const t = useTranslations('notes.pages')
  const client = useApolloClient()
  const loaded = useQuery(NotePagesDocument, { variables: { noteId }, fetchPolicy: 'network-only' })
  const [savePages] = useMutation(SaveNotePagesDocument)
  const [history, setHistory] = useState<PageHistory>(() => historyOf([blankPage()]))
  const [index, setIndex] = useState(0)
  const [tool, setTool] = useState<DrawTool>('pen')
  const [live, setLive] = useState<Stroke | null>(null)
  const [selected, setSelected] = useState<string | null>(null)
  const [scan, setScan] = useState(false)
  const [status, setStatus] = useState<'loading' | 'saved' | 'saving' | 'error'>('loading')
  const board = useRef<HTMLDivElement>(null)
  const draft = useRef<Stroke | null>(null)
  const erasing = useRef(false)
  const before = useRef<NotePage[] | null>(null)
  const ready = useRef(false)
  const hydrated = useRef<NotePage[] | null>(null)
  const file = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (loaded.loading || hydrated.current) return
    if (loaded.error || !loaded.data) {
      hydrated.current = []
      setStatus('error')
      return
    }
    const pages = pagesFromServer(loaded.data.note?.pages ?? [])
    const next = pages.length ? pages : [blankPage()]
    hydrated.current = next
    setHistory(historyOf(next))
    setStatus('saved')
  }, [loaded.data, loaded.error, loaded.loading])

  useEffect(() => {
    if (!hydrated.current) return
    // The load effect sets history for the next render. Do not write the previous pages first.
    if (!ready.current) {
      if (hydrated.current === history.present) ready.current = true
      return
    }
    setStatus('saving')
    const timer = setTimeout(() => {
      void savePages({ variables: { input: pagesToSave(noteId, history.present) } })
        .then((res) => setStatus(res.data?.saveNotePages.userErrors.length ? 'error' : 'saved'))
        .catch(() => setStatus('error'))
    }, 400)
    return () => clearTimeout(timer)
  }, [history.present, noteId, savePages])

  const page = history.present[Math.min(index, history.present.length - 1)] ?? history.present[0]!
  const pageIndex = history.present.indexOf(page)

  const at = (event: React.PointerEvent): InkPoint => {
    const box = board.current?.getBoundingClientRect()
    if (!box) return { x: 0, y: 0, p: 0.5 }
    return { x: clamp01((event.clientX - box.left) / box.width), y: clamp01((event.clientY - box.top) / box.height), p: pressureOf(event.pressure) }
  }
  const down = (event: React.PointerEvent) => {
    if (event.button !== 0) return
    const target = event.target as HTMLElement
    if (target.closest('[data-image]')) return
    event.currentTarget.setPointerCapture(event.pointerId)
    setSelected(null)
    const point = at(event)
    before.current = history.present
    if (tool === 'eraser') {
      erasing.current = true
      setHistory((h) => ({ ...h, present: updatePage(h.present, pageIndex, (p) => eraseAt(p, point)) }))
      return
    }
    const stroke: Stroke = {
      id: newPageId(),
      tool: tool === 'marker' ? 'marker' : 'pen',
      color: tool === 'marker' ? MARKER : PEN,
      width: tool === 'marker' ? 2.4 : 0.7,
      points: [point],
    }
    draft.current = stroke
    setLive(stroke)
  }
  const move = (event: React.PointerEvent) => {
    const point = at(event)
    if (erasing.current) {
      setHistory((h) => ({ ...h, present: updatePage(h.present, pageIndex, (p) => eraseAt(p, point)) }))
      return
    }
    if (!draft.current) return
    draft.current = { ...draft.current, points: [...draft.current.points, point] }
    setLive(draft.current)
  }
  const up = () => {
    if (erasing.current) {
      erasing.current = false
      const snapshot = before.current
      before.current = null
      if (snapshot) setHistory((h) => ({ past: [...h.past, snapshot].slice(-40), present: h.present, future: [] }))
      return
    }
    const stroke = draft.current
    draft.current = null
    setLive(null)
    if (!stroke || stroke.points.length < 2) return
    const finished = tool === 'ruler' ? straighten(stroke) : stroke
    setHistory((h) => commit(h, updatePage(h.present, pageIndex, (p) => addStroke(p, finished))))
  }
  const place = (href: string, name: string, file?: File) => {
    const image = { id: newPageId(), name, href, x: 0.18, y: 0.18, w: 0.42, h: 0.32, rotation: 0 }
    setHistory((h) => commit(h, updatePage(h.present, pageIndex, (p) => insertImage(p, image))))
    setSelected(image.id)
    if (!file) return
    void uploadPageImage(client, noteId, file)
      .then((fileId) => {
        setHistory((h) => ({
          ...h,
          present: h.present.map((item) => (item.images.some((placed) => placed.id === image.id) ? updateImage(item, image.id, { fileId }) : item)),
        }))
      })
      .catch(() => undefined)
  }
  const shown = live && tool === 'ruler' ? straighten(live) : live
  const lastRuled = [...page.strokes].reverse().find((item) => item.straight)
  const scale = (shown ? scalePercent(shown) : null) ?? (lastRuled ? scalePercent(lastRuled) : null)

  return (
    <div className="flex flex-col gap-3" data-testid="page-editor">
      <div className="flex flex-wrap items-center gap-2">
        <div role="toolbar" aria-label={t('tools')} className="flex flex-wrap gap-1">
          <ToolButton icon={Pen} label={t('pen')} pressed={tool === 'pen'} onClick={() => setTool('pen')} />
          <ToolButton icon={Pen} label={t('marker')} pressed={tool === 'marker'} onClick={() => setTool('marker')} marker />
          <ToolButton icon={Eraser} label={t('eraser')} pressed={tool === 'eraser'} onClick={() => setTool('eraser')} />
          <ToolButton icon={Ruler} label={t('ruler')} pressed={tool === 'ruler'} onClick={() => setTool('ruler')} />
        </div>
        <span className="mx-1 hidden h-6 w-px bg-border sm:block" aria-hidden />
        <button type="button" className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3 py-2 text-sm" onClick={() => file.current?.click()}>
          <ImagePlus className="size-4" aria-hidden />
          {t('insertPng')}
        </button>
        <input
          ref={file}
          type="file"
          accept="image/png,image/jpeg,image/webp"
          className="sr-only"
          aria-label={t('insertPng')}
          onChange={(event) => {
            const picked = event.target.files?.[0]
            event.target.value = ''
            if (!picked) return
            const reader = new FileReader()
            reader.onload = () => typeof reader.result === 'string' && place(reader.result, picked.name || 'image.png', picked)
            reader.readAsDataURL(picked)
          }}
        />
        <button type="button" className="inline-flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3 py-2 text-sm" onClick={() => setScan(true)}>
          <Camera className="size-4" aria-hidden />
          {t('scan')}
        </button>
        <span className="ml-auto flex gap-1">
          <ToolButton icon={Undo2} label={t('undo')} pressed={false} disabled={!history.past.length} onClick={() => setHistory(undo)} />
          <ToolButton icon={Redo2} label={t('redo')} pressed={false} disabled={!history.future.length} onClick={() => setHistory(redo)} />
        </span>
      </div>
      <p className="text-xs text-muted" role="status">
        {t(status)}
        {scale != null ? ` · ${t('scale', { n: scale })}` : ''}
      </p>
      <div className="flex flex-col gap-3 lg:flex-row">
        <div className="flex gap-2 overflow-x-auto lg:w-24 lg:flex-col lg:overflow-visible">
          {history.present.map((item, i) => (
            <button key={item.id} type="button" aria-current={i === pageIndex ? 'page' : undefined} className={cn('h-16 w-12 shrink-0 rounded-lg border bg-white text-xs text-slate-600', i === pageIndex ? 'border-sky-600 ring-2 ring-sky-600/40' : 'border-border')} onClick={() => setIndex(i)}>
              {t('pageN', { n: i + 1 })}
            </button>
          ))}
          <button
            type="button"
            className="h-16 w-12 shrink-0 rounded-lg border border-dashed border-border text-xs text-muted"
            onClick={() => {
              const next = [...history.present, blankPage()]
              setHistory((h) => commit(h, next))
              setIndex(next.length - 1)
            }}
          >
            {t('addPage')}
          </button>
        </div>
        <div
          ref={board}
          tabIndex={0}
          role="application"
          aria-label={t('board')}
          data-strokes={page.strokes.length}
          className="relative aspect-[3/4] w-full max-w-3xl touch-none overflow-hidden rounded-2xl border border-border bg-white shadow-sm outline-none focus-visible:ring-2 focus-visible:ring-sky-600"
          onPointerDown={down}
          onPointerMove={move}
          onPointerUp={up}
          onPointerCancel={up}
          onKeyDown={(event) => {
            if (!(event.metaKey || event.ctrlKey) || event.key.toLowerCase() !== 'z') return
            event.preventDefault()
            setHistory(event.shiftKey ? redo : undo)
          }}
        >
          <svg viewBox="0 0 100 100" className="absolute inset-0 h-full w-full" aria-hidden>
            {[...page.strokes, ...(shown ? [shown] : [])].map((stroke) => (
              <path
                key={stroke.id}
                d={strokePath(stroke)}
                fill="none"
                stroke={stroke.color}
                strokeWidth={strokeWidth(stroke)}
                strokeLinecap="round"
                strokeLinejoin="round"
                opacity={stroke.tool === 'marker' ? 0.45 : 1}
              />
            ))}
          </svg>
          {page.images.map((image) => (
            <div
              key={image.id}
              data-image
              className={cn('absolute touch-none', selected === image.id && 'ring-2 ring-sky-600')}
              style={{ left: `${image.x * 100}%`, top: `${image.y * 100}%`, width: `${image.w * 100}%`, height: `${image.h * 100}%`, transform: `rotate(${image.rotation}deg)` }}
              onPointerDown={(event) => {
                event.stopPropagation()
                const handle = (event.target as HTMLElement).dataset.handle
                const start = { x: event.clientX, y: event.clientY, image: { ...image } }
                setSelected(image.id)
                const box = board.current?.getBoundingClientRect()
                const drag = (moveEvent: PointerEvent) => {
                  if (!box) return
                  const dx = (moveEvent.clientX - start.x) / box.width
                  const dy = (moveEvent.clientY - start.y) / box.height
                  const patch = handle === 'resize' ? { w: start.image.w + dx, h: start.image.h + dy } : { x: start.image.x + dx, y: start.image.y + dy }
                  setHistory((h) => ({ ...h, present: updatePage(h.present, pageIndex, (p) => updateImage(p, image.id, patch)) }))
                }
                const end = () => {
                  window.removeEventListener('pointermove', drag)
                  window.removeEventListener('pointerup', end)
                  setHistory((h) => commit({ ...h, present: beforePages(h.present, history.present) }, h.present))
                }
                // Snapshot the pages from before this drag by committing against the current history on release.
                before.current = history.present
                window.addEventListener('pointermove', drag)
                window.addEventListener('pointerup', end)
              }}
            >
              {/* Placed by the author on this page; the href is their upload or scan. */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={image.href} alt={image.name} draggable={false} className="h-full w-full select-none object-contain" />
              {selected === image.id ? (
                <>
                  <button type="button" data-handle="resize" aria-label={t('resize')} className="absolute -bottom-2 -right-2 size-4 rounded-full border border-sky-700 bg-white" />
                  <button
                    type="button"
                    aria-label={t('rotate')}
                    className="absolute -top-7 left-0 rounded-md bg-sky-700 px-1.5 py-0.5 text-[10px] font-semibold text-white"
                    onPointerDown={(event) => event.stopPropagation()}
                    onClick={(event) => {
                      event.stopPropagation()
                      setHistory((h) => commit(h, updatePage(h.present, pageIndex, (p) => updateImage(p, image.id, { rotation: image.rotation + 15 }))))
                    }}
                  >
                    {t('rotate')}
                  </button>
                  <button
                    type="button"
                    aria-label={t('removeImage')}
                    className="absolute -right-2 -top-2 grid size-5 place-items-center rounded-full bg-slate-900 text-white"
                    onPointerDown={(event) => event.stopPropagation()}
                    onClick={(event) => {
                      event.stopPropagation()
                      setHistory((h) => commit(h, updatePage(h.present, pageIndex, (p) => removeImage(p, image.id))))
                      setSelected(null)
                    }}
                  >
                    <Trash2 className="size-3" aria-hidden />
                  </button>
                </>
              ) : null}
            </div>
          ))}
        </div>
      </div>
      <PhotoScan open={scan} onClose={() => setScan(false)} onImage={place} />
    </div>
  )
}

function beforePages(current: NotePage[], previous: NotePage[]): NotePage[] {
  return previous.length ? previous : current
}

function ToolButton({ icon: Icon, label, pressed, disabled, onClick, marker }: { icon: typeof Pen; label: string; pressed: boolean; disabled?: boolean; onClick: () => void; marker?: boolean }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-pressed={pressed}
      disabled={disabled}
      onClick={onClick}
      className={cn('inline-flex size-10 items-center justify-center rounded-xl border border-border bg-surface text-fg disabled:opacity-40 aria-pressed:border-sky-600 aria-pressed:bg-sky-50 aria-pressed:text-sky-800', marker && 'text-sky-600')}
    >
      <Icon className="size-[18px]" aria-hidden />
    </button>
  )
}
