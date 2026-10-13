'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { cn } from '@/lib/cn'

/**
 * Board A's card rail (lvn-backend ADR-0076): the note's sections, from its headings, as a row to jump between, with
 * Previous and Next. It is the note's outline on wide screens (phones open Contents instead). Only shown when the note
 * has a heading; the pager only with two sections or more.
 */
export function CardRail({ sections, onGo }: { sections: { key: string | number; text: string }[]; onGo: (index: number) => void }) {
  const t = useTranslations('notes')
  const [current, setCurrent] = useState(0)
  if (!sections.length) return null
  const at = Math.min(current, sections.length - 1)
  const go = (i: number) => {
    setCurrent(i)
    onGo(i)
  }
  return (
    <nav aria-label={t('editor.outline')} className="hidden items-center gap-2 lg:flex">
      {sections.length > 1 ? (
        <button type="button" aria-label={t('view.pager.previous')} disabled={at === 0} onClick={() => go(at - 1)} className="grid size-8 shrink-0 place-items-center rounded-full border border-border text-muted hover:border-accent hover:text-accent disabled:opacity-40">
          <ChevronLeft className="size-4" aria-hidden />
        </button>
      ) : null}
      <ol className="flex min-w-0 flex-1 gap-1.5 overflow-x-auto py-0.5 [scrollbar-width:thin]">
        {sections.map((s, i) => (
          <li key={s.key} className="shrink-0">
            <button
              type="button"
              aria-current={i === at ? 'step' : undefined}
              onClick={() => go(i)}
              className={cn('flex max-w-56 items-center gap-1.5 rounded-xl border px-3 py-1.5 text-left text-sm transition', i === at ? 'border-accent bg-accent-soft text-accent' : 'border-border bg-surface text-muted hover:border-accent hover:text-fg')}
            >
              <span aria-hidden className="text-xs font-bold tabular-nums">
                {i + 1}
              </span>
              <span className="truncate">{s.text || t('editor.untitledHeading')}</span>
            </button>
          </li>
        ))}
      </ol>
      {sections.length > 1 ? (
        <>
          <span aria-live="polite" className="shrink-0 text-xs tabular-nums text-muted">
            {t('view.pager.position', { n: at + 1, total: sections.length })}
          </span>
          <button type="button" aria-label={t('view.pager.next')} disabled={at === sections.length - 1} onClick={() => go(at + 1)} className="grid size-8 shrink-0 place-items-center rounded-full border border-border text-muted hover:border-accent hover:text-accent disabled:opacity-40">
            <ChevronRight className="size-4" aria-hidden />
          </button>
        </>
      ) : null}
    </nav>
  )
}
