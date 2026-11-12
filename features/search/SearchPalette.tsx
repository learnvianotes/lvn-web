'use client'

import { BookBookmark, CornerDownLeft, FileText, GraduationCap, Library, Search, Sparkles, UserRound, Users } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/cn'
import { Snippet } from './Snippet'
import { useSearch } from './useSearch'

export const OPEN_SEARCH_EVENT = 'lvn:open-search'

/**
 * Ctrl/⌘+K (§12.2): search from anywhere in the app — notes, people, groups, classes and topics (lvn-backend ADR-0056).
 * Enter opens what is chosen; a topic lists its notes on /search. The header's search button opens it too
 * (OPEN_SEARCH_EVENT); "All results" goes to /search, and "Ask AI" takes the words to Ask AI as a question.
 */
export function SearchPalette() {
  const t = useTranslations('search')
  const router = useRouter()
  const ref = useRef<HTMLDialogElement>(null)
  const input = useRef<HTMLInputElement>(null)
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const [active, setActive] = useState(0)
  const { notes, people, topics, groups, classrooms, resources, searched, settled } = useSearch(open ? query : '', 8)
  const items = [
    ...notes.map((n) => ({ kind: 'note' as const, id: n.note.id, n })),
    ...people.slice(0, 4).map((person) => ({ kind: 'person' as const, id: person.id, person })),
    ...groups.slice(0, 3).map((group) => ({ kind: 'group' as const, id: group.id, group })),
    ...classrooms.slice(0, 3).map((classroom) => ({ kind: 'classroom' as const, id: classroom.id, classroom })),
    ...resources.slice(0, 3).map((resource) => ({ kind: 'resource' as const, id: resource.id, resource })),
    ...topics.slice(0, 4).map((topic) => ({ kind: 'topic' as const, id: topic.id, topic })),
  ]

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        setOpen((o) => !o)
      }
    }
    const onOpen = (e: Event) => {
      e.preventDefault()
      setOpen(true)
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener(OPEN_SEARCH_EVENT, onOpen)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener(OPEN_SEARCH_EVENT, onOpen)
    }
  }, [])
  useEffect(() => {
    const d = ref.current
    if (!d) return
    if (open && !d.open) {
      d.showModal()
      input.current?.select()
    }
    if (!open && d.open) d.close()
  }, [open])
  const [lastItems, setLastItems] = useState(items.length)
  if (items.length !== lastItems) {
    setLastItems(items.length)
    setActive(0)
  }

  /** Opens what is chosen (a topic: its notes on /search), or — with nothing chosen — all results. */
  const go = (item: (typeof items)[number] | undefined) => {
    if (!item && query.trim().length < 2) return
    setOpen(false)
    const where = !item
      ? `/search?q=${encodeURIComponent(query.trim())}`
      : item.kind === 'person'
        ? `/u/${item.person.handle}`
        : item.kind === 'group'
          ? `/groups/${item.id}`
          : item.kind === 'classroom'
            ? `/classes/${item.id}`
            : item.kind === 'resource'
              ? `/resources/${item.id}`
            : item.kind === 'topic'
              ? `/search?${new URLSearchParams({ topic: item.id, topicTitle: item.topic.title }).toString()}`
              : `/notes/${item.id}`
    router.push(where)
  }

  return (
    <dialog
      ref={ref}
      aria-label={t('label')}
      onClose={() => setOpen(false)}
      onClick={(e) => e.target === ref.current && setOpen(false)}
      className="m-auto mt-[12vh] w-[calc(100%-2rem)] max-w-xl overflow-hidden rounded-2xl border border-border bg-bg p-0 text-fg shadow-2xl backdrop:bg-black/40 backdrop:backdrop-blur-sm"
    >
      {open ? (
        <div className="flex max-h-[70vh] flex-col">
          <label className="flex items-center gap-3 border-b border-border px-4 focus-within:border-accent">
            <Search className="size-5 shrink-0 text-muted" aria-hidden />
            <span className="sr-only">{t('label')}</span>
            <input
              ref={input}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'ArrowDown') setActive((a) => Math.min(a + 1, items.length - 1))
                else if (e.key === 'ArrowUp') setActive((a) => Math.max(a - 1, 0))
                else if (e.key === 'Enter') go(items[active])
                else return
                e.preventDefault()
              }}
              placeholder={t('placeholder')}
              role="combobox"
              aria-expanded={items.length > 0}
              aria-controls="search-results"
              aria-activedescendant={items[active] ? `search-${items[active].id}` : undefined}
              className="h-14 min-w-0 flex-1 border-0 bg-transparent text-base placeholder:text-muted outline-none"
            />
            <kbd className="hidden rounded border border-border px-1.5 py-0.5 text-[10px] text-muted sm:block">Esc</kbd>
          </label>
          <ul id="search-results" role="listbox" aria-label={t('results')} className="min-h-0 flex-1 overflow-y-auto p-2">
            {items.map((item, i) => (
              <li key={`${item.kind}-${item.id}`} id={`search-${item.id}`} role="option" aria-selected={i === active}>
                <button
                  type="button"
                  onMouseEnter={() => setActive(i)}
                  onClick={() => go(item)}
                  className={cn('flex w-full items-start gap-3 rounded-xl px-3 py-2.5 text-left', i === active ? 'bg-accent-soft' : 'hover:bg-surface-2')}
                >
                  {item.kind === 'note' ? (
                    <>
                      <FileText className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                      <span className="flex min-w-0 flex-1 flex-col">
                        <span className="truncate font-medium">{item.n.note.title || t('untitled')}</span>
                        <Snippet text={item.n.snippet} className="line-clamp-2 text-xs leading-5 text-muted" />
                        <span className="text-[11px] text-muted">{t('by', { name: item.n.note.owner.displayName })}</span>
                      </span>
                    </>
                  ) : item.kind === 'person' ? (
                    <>
                      <UserRound className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                      <span className="text-sm">
                        {item.person.displayName} <span className="text-muted">@{item.person.handle}</span>
                      </span>
                    </>
                  ) : item.kind === 'group' ? (
                    <>
                      <Users className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                      <span className="text-sm">
                        {item.group.name} <span className="text-muted">· {t(item.group.type === 'PROJECT' ? 'workspace' : item.group.privacy === 'PRIVATE' ? 'privateGroup' : 'group')}</span>
                      </span>
                    </>
                  ) : item.kind === 'classroom' ? (
                    <>
                      <GraduationCap className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                      <span className="text-sm">
                        {item.classroom.name} <span className="text-muted">· {t('classroom')}</span>
                      </span>
                    </>
                  ) : item.kind === 'resource' ? (
                    <>
                      <Library className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                      <span className="text-sm">
                        {item.resource.title} <span className="text-muted">· {item.resource.host}</span>
                      </span>
                    </>
                  ) : (
                    <>
                      <BookBookmark className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />
                      <span className="text-sm">
                        {item.topic.title} <span className="text-muted">· {item.topic.subject.title}</span>
                      </span>
                    </>
                  )}
                  {i === active ? <CornerDownLeft className="ml-auto mt-0.5 size-3.5 shrink-0 text-muted" aria-hidden /> : null}
                </button>
              </li>
            ))}
          </ul>
          {searched && !items.length ? <p className="px-5 pb-5 text-sm text-muted">{t('nothing', { query: settled })}</p> : null}
          {!query.trim() ? <p className="px-5 pb-5 text-sm text-muted">{t('hint')}</p> : null}
          {query.trim().length >= 2 ? (
            <button type="button" onClick={() => go(undefined)} className="border-t border-border px-5 py-3 text-left text-sm font-medium text-accent hover:bg-surface-2">
              {t('all', { query: query.trim() })}
            </button>
          ) : null}
          {query.trim().length >= 3 ? (
            <button
              type="button"
              onClick={() => {
                setOpen(false)
                router.push(`/ask?q=${encodeURIComponent(query.trim())}`)
              }}
              className="flex items-center gap-2 border-t border-border px-5 py-3 text-left text-sm font-medium text-accent hover:bg-surface-2"
            >
              <Sparkles className="size-4 shrink-0" aria-hidden />
              {t('askAi', { query: query.trim() })}
            </button>
          ) : null}
        </div>
      ) : null}
    </dialog>
  )
}
