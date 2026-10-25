'use client'

import { ChevronDown, ChevronUp, Copy, MessageSquareText, NotebookPen, Search, Trash, X, type LucideIcon } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import type { HighlightColor, HighlightFieldsFragment } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import type { OutlineItem } from './PdfViewer'

/** The pieces of the PDF reader (./ReaderPage): actions on a selection, a highlight's card, the side lists. */

export const COLORS: HighlightColor[] = ['YELLOW', 'GREEN', 'BLUE', 'PINK', 'PURPLE']
/** The API's PURPLE keeps its name, so stored highlights stay as they are; it is drawn and named orange (ADR-0094). */
export const SWATCH: Record<HighlightColor, string> = {
  YELLOW: 'bg-yellow-300',
  GREEN: 'bg-green-400',
  BLUE: 'bg-blue-400',
  PINK: 'bg-pink-400',
  PURPLE: 'bg-orange-400',
}

export function ToolButton({ icon: Icon, label, onClick, pressed, disabled, className, showLabel }: { icon: LucideIcon; label: string; onClick: () => void; pressed?: boolean; disabled?: boolean; className?: string; showLabel?: boolean }) {
  return (
    <button
      type="button"
      aria-label={showLabel ? undefined : label}
      title={label}
      aria-pressed={pressed}
      disabled={disabled}
      onClick={onClick}
      className={cn(
        'inline-flex h-9 shrink-0 items-center justify-center gap-1.5 rounded-xl text-sm text-fg transition hover:bg-surface-2 active:scale-95 disabled:opacity-40 aria-pressed:bg-accent-soft aria-pressed:text-accent',
        showLabel ? 'px-2.5' : 'w-9',
        className,
      )}
    >
      <Icon className="size-[18px]" aria-hidden />
      {showLabel ? <span>{label}</span> : null}
    </button>
  )
}

/** A small panel floating at a point of the window, kept inside it. */
export function Floating({ at, children, label, onClose }: { at: { x: number; y: number }; children: React.ReactNode; label: string; onClose?: () => void }) {
  const box = useRef<HTMLDivElement>(null)
  const [pos, setPos] = useState({ left: at.x, top: at.y + 10 })
  useLayoutEffect(() => {
    const el = box.current
    if (!el) return
    const { width, height } = el.getBoundingClientRect()
    const left = Math.min(Math.max(8, at.x - width / 2), window.innerWidth - width - 8)
    const below = at.y + 10
    const top = below + height > window.innerHeight - 8 ? Math.max(8, at.y - height - 40) : below
    setPos({ left, top })
  }, [at.x, at.y])
  useEffect(() => {
    if (!onClose) return
    const close = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', close)
    return () => window.removeEventListener('keydown', close)
  }, [onClose])
  return (
    <div ref={box} role="dialog" aria-label={label} className="fixed z-[60] flex animate-rise flex-col gap-2 rounded-2xl border border-border bg-surface p-2 shadow-2xl shadow-black/20" style={pos} onMouseDown={(e) => e.preventDefault()}>
      {children}
    </div>
  )
}

export function Swatches({ onPick, current, label }: { onPick: (color: HighlightColor) => void; current?: HighlightColor; label: (color: HighlightColor) => string }) {
  return (
    <div className="flex items-center gap-1.5 px-1">
      {COLORS.map((color) => (
        <button
          key={color}
          type="button"
          aria-label={label(color)}
          title={label(color)}
          aria-pressed={current === color}
          className={cn('size-7 rounded-full ring-offset-2 ring-offset-surface transition hover:scale-110 aria-pressed:ring-2 aria-pressed:ring-fg', SWATCH[color])}
          onClick={() => onPick(color)}
        />
      ))}
    </div>
  )
}

/** What can be done with selected words. */
export function SelectionActions({ at, editable, onHighlight, onAdd, onCopy, onStudy, onClose }: { at: { x: number; y: number }; editable: boolean; onHighlight: (c: HighlightColor) => void; onAdd: () => void; onCopy: () => void; onStudy?: () => void; onClose: () => void }) {
  const t = useTranslations('reader')
  return (
    <Floating at={at} label={t('selectionActions')} onClose={onClose}>
      {editable ? <Swatches label={(c) => t('highlightIn', { color: t(`colors.${c}`) })} onPick={onHighlight} /> : null}
      <div className="flex items-center gap-1">
        {editable ? <ToolButton icon={NotebookPen} label={t('addToNotes')} onClick={onAdd} showLabel className="bg-accent text-accent-fg hover:bg-accent/90" /> : null}
        <ToolButton icon={Copy} label={t('copy')} onClick={onCopy} showLabel />
        {!editable && onStudy ? <ToolButton icon={NotebookPen} label={t('study')} onClick={onStudy} showLabel /> : null}
      </div>
    </Floating>
  )
}

/** What can be done with a snipped area. */
export function AreaActions({ at, busy, onHighlight, onAdd, onCancel }: { at: { x: number; y: number }; busy: boolean; onHighlight: (c: HighlightColor) => void; onAdd: () => void; onCancel: () => void }) {
  const t = useTranslations('reader')
  return (
    <Floating at={at} label={t('areaActions')} onClose={onCancel}>
      <Swatches label={(c) => t('highlightIn', { color: t(`colors.${c}`) })} onPick={onHighlight} />
      <div className="flex items-center gap-1">
        <ToolButton icon={NotebookPen} label={busy ? t('adding') : t('addToNotes')} onClick={onAdd} disabled={busy} showLabel className="bg-accent text-accent-fg hover:bg-accent/90" />
        <ToolButton icon={X} label={t('cancel')} onClick={onCancel} showLabel />
      </div>
    </Floating>
  )
}

/** A highlight: its colour, a comment, add it to the notes, remove it. */
export function HighlightCard({ highlight, at, onColor, onComment, onAdd, onRemove, onClose }: { highlight: HighlightFieldsFragment; at: { x: number; y: number }; onColor: (c: HighlightColor) => void; onComment: (text: string) => void; onAdd: () => void; onRemove: () => void; onClose: () => void }) {
  const t = useTranslations('reader')
  const [comment, setComment] = useState(highlight.comment ?? '')
  const changed = comment.trim() !== (highlight.comment ?? '')
  return (
    <Floating at={at} label={t('highlightCard')} onClose={onClose}>
      <div className="flex items-center justify-between gap-2">
        <Swatches current={highlight.color} label={(c) => t('highlightIn', { color: t(`colors.${c}`) })} onPick={onColor} />
        <ToolButton icon={X} label={t('close')} onClick={onClose} />
      </div>
      {highlight.quote ? <p className="line-clamp-3 max-w-72 px-1 text-sm text-muted">“{highlight.quote}”</p> : null}
      <label className="flex flex-col gap-1 px-1">
        <span className="sr-only">{t('comment')}</span>
        <textarea
          rows={2}
          maxLength={2000}
          value={comment}
          placeholder={t('commentPlaceholder')}
          onChange={(e) => setComment(e.target.value)}
          onMouseDown={(e) => e.stopPropagation()}
          className="w-72 max-w-full resize-y rounded-lg border border-border bg-bg px-2.5 py-1.5 text-sm focus-visible:border-accent focus-visible:outline-none"
        />
      </label>
      <div className="flex flex-wrap items-center gap-1">
        {changed ? <ToolButton icon={MessageSquareText} label={t('saveComment')} onClick={() => onComment(comment)} showLabel className="bg-accent text-accent-fg hover:bg-accent/90" /> : null}
        <ToolButton icon={NotebookPen} label={highlight.cardId ? t('addAgain') : t('addToNotes')} onClick={onAdd} showLabel />
        <ToolButton icon={Trash} label={t('remove')} onClick={onRemove} className="ml-auto text-red-600 dark:text-red-400" />
      </div>
    </Floating>
  )
}

export function HighlightsList({ highlights, onOpen }: { highlights: HighlightFieldsFragment[]; onOpen: (h: HighlightFieldsFragment) => void }) {
  const t = useTranslations('reader')
  if (!highlights.length) return <p className="px-2 py-6 text-sm text-muted">{t('highlightsEmpty')}</p>
  const pages = [...new Set(highlights.map((h) => h.page))].sort((a, b) => a - b)
  return (
    <div className="flex flex-col gap-4">
      {pages.map((page) => (
        <section key={page} className="flex flex-col gap-1.5">
          <h3 className="px-2 text-xs font-semibold uppercase tracking-wider text-muted">{t('pageLabel', { page })}</h3>
          {highlights
            .filter((h) => h.page === page)
            .map((h) => (
              <button key={h.id} type="button" onClick={() => onOpen(h)} className="flex gap-2.5 rounded-xl border border-border bg-surface p-2.5 text-left text-sm transition hover:border-accent/50 hover:shadow-sm">
                <span className={cn('mt-1 size-3 shrink-0 rounded-full', SWATCH[h.color])} aria-hidden />
                <span className="flex min-w-0 flex-col gap-1">
                  <span className="line-clamp-3">{h.kind === 'AREA' ? <em className="text-muted">{t('area')}</em> : `“${h.quote ?? ''}”`}</span>
                  {h.comment ? <span className="line-clamp-2 text-xs text-muted">{h.comment}</span> : null}
                  {h.cardId ? <span className="text-xs font-medium text-accent">{t('inNotes')}</span> : null}
                </span>
              </button>
            ))}
        </section>
      ))}
    </div>
  )
}

export function OutlineList({ items, onPick, depth = 0 }: { items: OutlineItem[]; onPick: (dest: unknown) => void; depth?: number }) {
  const t = useTranslations('reader')
  if (!items.length && depth === 0) return <p className="px-2 py-6 text-sm text-muted">{t('contentsEmpty')}</p>
  return (
    <ul className="flex flex-col">
      {items.map((item, i) => (
        <li key={`${depth}-${i}`}>
          <button type="button" className="w-full truncate rounded-lg px-2 py-1.5 text-left text-sm text-muted transition hover:bg-surface-2 hover:text-fg" style={{ paddingLeft: `${0.5 + depth * 0.85}rem` }} onClick={() => onPick(item.dest)}>
            {item.title || t('untitled')}
          </button>
          {item.items.length ? <OutlineList items={item.items} onPick={onPick} depth={depth + 1} /> : null}
        </li>
      ))}
    </ul>
  )
}

export function FindBar({ result, onFind, onClose }: { result: { current: number; total: number } | null; onFind: (query: string, direction?: 'next' | 'previous') => void; onClose: () => void }) {
  const t = useTranslations('reader')
  const [query, setQuery] = useState('')
  const input = useRef<HTMLInputElement>(null)
  useEffect(() => input.current?.focus(), [])
  return (
    <div role="search" className="flex items-center gap-1.5 border-b border-border bg-surface px-3 py-1.5">
      <Search className="size-4 shrink-0 text-muted" aria-hidden />
      <input
        ref={input}
        type="search"
        value={query}
        aria-label={t('find')}
        placeholder={t('findPlaceholder')}
        className="min-w-0 flex-1 bg-transparent py-1 text-sm focus:outline-none"
        onChange={(e) => {
          setQuery(e.target.value)
          onFind(e.target.value)
        }}
        onKeyDown={(e) => {
          if (e.key === 'Enter') onFind(query, e.shiftKey ? 'previous' : 'next')
          if (e.key === 'Escape') onClose()
        }}
      />
      <span role="status" className="shrink-0 text-xs text-muted">
        {query.trim() && result ? (result.total ? t('findCount', { current: result.current, total: result.total }) : t('findNone')) : ''}
      </span>
      <ToolButton icon={ChevronUp} label={t('findPrevious')} onClick={() => onFind(query, 'previous')} disabled={!result?.total} />
      <ToolButton icon={ChevronDown} label={t('findNext')} onClick={() => onFind(query, 'next')} disabled={!result?.total} />
      <ToolButton icon={X} label={t('close')} onClick={onClose} />
    </div>
  )
}
