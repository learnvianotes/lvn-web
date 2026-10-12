'use client'

import { BookMarked, FileText, Globe, Lock, Search, Users } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Snippet } from './Snippet'
import { useSearch } from './useSearch'

const VISIBILITY_ICON = { PRIVATE: Lock, SHARED: Users, PUBLIC: Globe } as const

/** /search: everything search finds for a query — notes the viewer may read, with their snippets, and topics. */
export function SearchPage() {
  const t = useTranslations('search')
  const router = useRouter()
  const initial = useSearchParams().get('q') ?? ''
  const [query, setQuery] = useState(initial)
  const { notes, people, topics, loading, searched, settled } = useSearch(query, 20)
  const set = (q: string) => {
    setQuery(q)
    router.replace(q ? `/search?q=${encodeURIComponent(q)}` : '/search', { scroll: false })
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
      <label className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 shadow-sm focus-within:border-accent focus-within:ring-2 focus-within:ring-accent/30">
        <Search className="size-5 text-muted" aria-hidden />
        <span className="sr-only">{t('label')}</span>
        <input autoFocus value={query} onChange={(e) => set(e.target.value)} placeholder={t('placeholder')} className="h-14 flex-1 bg-transparent text-lg placeholder:text-muted focus:outline-none focus-visible:outline-none" />
      </label>
      {people.length ? (
        <section aria-labelledby="people-heading" className="flex flex-col gap-2">
          <h2 id="people-heading" className="text-sm font-semibold text-muted">
            {t('people')}
          </h2>
          <ul className="flex flex-wrap gap-2">
            {people.map((p) => (
              <li key={p.id}>
                <Link href={`/u/${p.handle}`} className="inline-flex items-center gap-2 rounded-full border border-border bg-surface py-1 pl-1 pr-3 text-sm hover:border-accent hover:text-accent">
                  <span aria-hidden className="grid size-7 place-items-center rounded-full bg-accent-soft text-xs font-bold text-accent">
                    {p.displayName.slice(0, 1).toUpperCase()}
                  </span>
                  {p.displayName} <span className="text-muted">@{p.handle}</span>
                  {p.globalRole === 'TEACHER' ? <span className="rounded-full bg-accent-soft px-1.5 text-[10px] font-semibold uppercase text-accent">{t('teacher')}</span> : null}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {topics.length ? (
        <section aria-labelledby="topics-heading" className="flex flex-col gap-2">
          <h2 id="topics-heading" className="text-sm font-semibold text-muted">
            {t('topics')}
          </h2>
          <div className="flex flex-wrap gap-2">
            {topics.map((topic) => (
              <button key={topic.id} type="button" onClick={() => set(topic.title)} className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-3 py-1.5 text-sm hover:border-accent hover:text-accent">
                <BookMarked className="size-3.5" aria-hidden />
                {topic.title} <span className="text-muted">· {topic.subject.title}</span>
              </button>
            ))}
          </div>
        </section>
      ) : null}
      <section aria-labelledby="notes-heading" aria-busy={loading} className="flex flex-col gap-3">
        <h2 id="notes-heading" className="text-sm font-semibold text-muted">
          {t('notes')}
        </h2>
        {searched && !notes.length ? <p className="text-sm text-muted">{t('nothing', { query: settled })}</p> : null}
        {!settled ? <p className="text-sm text-muted">{t('hint')}</p> : null}
        <ul className="flex flex-col gap-3">
          {notes.map(({ note, snippet }) => {
            const Icon = VISIBILITY_ICON[note.visibility]
            return (
              <li key={note.id}>
                <Link href={`/notes/${note.id}`} className="group flex flex-col gap-1.5 rounded-2xl border border-border bg-surface p-4 transition hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-lg hover:shadow-accent/10">
                  <span className="flex items-center gap-2 font-semibold">
                    <FileText className="size-4 text-accent" aria-hidden />
                    {note.title || t('untitled')}
                  </span>
                  <Snippet text={snippet} className="text-sm leading-6 text-muted" />
                  <span className="flex items-center gap-1.5 text-xs text-muted">
                    <Icon className="size-3.5" aria-hidden />
                    {t(`visibility.${note.visibility}`)} · {t('by', { name: note.owner.displayName })}
                  </span>
                </Link>
              </li>
            )
          })}
        </ul>
      </section>
    </div>
  )
}
