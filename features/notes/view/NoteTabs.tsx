'use client'

import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useRef, useState, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

export type NoteTab = 'content' | 'summary' | 'flashcards' | 'quiz' | 'discussions'
export const NOTE_TABS: NoteTab[] = ['content', 'summary', 'flashcards', 'quiz', 'discussions']

/**
 * The note's tab (lvn-backend ADR-0076), kept in `?tab=`: it survives the reload after AI cards are added to the note,
 * and a link can open one (a comment opens Discussions). A tab not offered falls back to the content.
 */
export function useNoteTab(offered: readonly NoteTab[]) {
  const asked = useSearchParams().get('tab') as NoteTab | null
  const [tab, setTab] = useState<NoteTab>(asked && NOTE_TABS.includes(asked) ? asked : 'content')
  const current = offered.includes(tab) ? tab : 'content'
  const choose = (next: NoteTab) => {
    setTab(next)
    const url = new URL(window.location.href)
    if (next === 'content') url.searchParams.delete('tab')
    else url.searchParams.set('tab', next)
    window.history.replaceState(window.history.state, '', url)
  }
  return [current, choose] as const
}

/** The tab strip: Content · AI Summary · Flashcards · Quiz · Discussions, those offered; arrow keys move along it. */
export function NoteTabs({ tabs, current, onChange, idBase }: { tabs: readonly NoteTab[]; current: NoteTab; onChange: (tab: NoteTab) => void; idBase: string }) {
  const t = useTranslations('notes.view.tabs')
  const buttons = useRef<(HTMLButtonElement | null)[]>([])
  const move = (to: number) => {
    const i = (to + tabs.length) % tabs.length
    onChange(tabs[i]!)
    buttons.current[i]?.focus()
  }
  return (
    <div role="tablist" aria-label={t('label')} className="-mx-1 flex gap-1 overflow-x-auto border-b border-border px-1 [scrollbar-width:none]">
      {tabs.map((tab, i) => {
        const selected = tab === current
        return (
          <button
            key={tab}
            ref={(el) => {
              buttons.current[i] = el
            }}
            type="button"
            role="tab"
            id={`${idBase}-tab-${tab}`}
            aria-selected={selected}
            aria-controls={`${idBase}-panel-${tab}`}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(tab)}
            onKeyDown={(e) => {
              const to = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : e.key === 'Home' ? 0 : e.key === 'End' ? tabs.length - 1 : null
              if (to === null) return
              e.preventDefault()
              move(to)
            }}
            className={cn('-mb-px shrink-0 border-b-2 px-3 py-2.5 text-sm font-semibold transition', selected ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg')}
          >
            {t(tab)}
          </button>
        )
      })}
    </div>
  )
}

/** One tab's panel; the content's stays mounted while another is open (the editor keeps its state and autosave). */
export function NoteTabPanel({ idBase, tab, current, keepMounted, children }: { idBase: string; tab: NoteTab; current: NoteTab; keepMounted?: boolean; children: ReactNode }) {
  if (tab !== current && !keepMounted) return null
  return (
    <div role="tabpanel" id={`${idBase}-panel-${tab}`} aria-labelledby={`${idBase}-tab-${tab}`} hidden={tab !== current} className={tab === current ? 'flex flex-col gap-4' : 'hidden'}>
      {children}
    </div>
  )
}
