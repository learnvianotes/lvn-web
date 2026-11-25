'use client'

import { BookBookmark, FileText, Globe, GraduationCap, Library, Link2, Lock, Search, Users, X } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { LoadFailed } from '@/components/ui/query-state'
import type { NoteKind, NoteSource, SearchScope } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { Snippet } from './Snippet'
import { useSearch } from './useSearch'
import { StudyLoader } from '@/components/ui/study-loader'

const VISIBILITY_ICON = { PRIVATE: Lock, SHARED: Users, UNLISTED: Link2, PUBLIC: Globe } as const
const KINDS: NoteKind[] = ['NOTE', 'BLOG', 'POST', 'PROJECT']
const SOURCES: NoteSource[] = ['MINE', 'SHARED', 'PUBLIC']
type Tab = 'all' | 'notes' | 'topics' | 'groups' | 'users' | 'resources'
const TABS: Tab[] = ['all', 'notes', 'topics', 'groups', 'users', 'resources']
/** What each tab asks for; All asks for everything. Classes are found with groups. */
const SCOPES: Record<Tab, SearchScope[] | undefined> = { all: undefined, notes: ['NOTES'], topics: ['TOPICS'], groups: ['GROUPS', 'CLASSROOMS'], users: ['PEOPLE'], resources: ['RESOURCES'] }

const listParam = <T extends string>(value: string | null, allowed: readonly T[]) => (value ?? '').split(',').filter((v): v is T => (allowed as readonly string[]).includes(v))

/**
 * /search: everything search finds (lvn-backend ADR-0056) — notes the viewer may read with their snippets, page after
 * page; people, groups, classes, resources and topics — in tabs: All, Notes, Topics, Groups, Users and Resources
 * (lvn-backend ADR-0076). Kind and source chips narrow the notes; a topic lists its notes. The URL keeps the query, the
 * tab and the filters.
 */
export function SearchPage() {
  const t = useTranslations('search')
  const router = useRouter()
  const params = useSearchParams()
  const [query, setQuery] = useState(params.get('q') ?? '')
  const [kinds, setKinds] = useState(listParam(params.get('kind'), KINDS))
  const [sources, setSources] = useState(listParam(params.get('from'), SOURCES))
  const [topic, setTopic] = useState(params.get('topic') ? { id: params.get('topic')!, title: params.get('topicTitle') ?? '' } : null)
  const [tab, setTab] = useState<Tab>(TABS.find((x) => x === params.get('tab')) ?? 'all')
  // Kind, source and topic narrow notes, so they apply where notes are listed.
  const narrows = tab === 'all' || tab === 'notes'
  const { notes, people, topics, groups, classrooms, resources, hasMore, more, loadingMore, loading, searched, failed, retry, settled } = useSearch(query, 20, narrows ? { kinds, sources, topicId: topic?.id } : {}, SCOPES[tab])

  const go = (next: { q?: string; tab?: Tab; kinds?: NoteKind[]; sources?: NoteSource[]; topic?: { id: string; title: string } | null }) => {
    const q = next.q ?? query
    const tb = next.tab ?? tab
    const k = next.kinds ?? kinds
    const s = next.sources ?? sources
    const tp = next.topic === undefined ? topic : next.topic
    const search = new URLSearchParams()
    if (q) search.set('q', q)
    if (tb !== 'all') search.set('tab', tb)
    if (k.length) search.set('kind', k.join(','))
    if (s.length) search.set('from', s.join(','))
    if (tp) {
      search.set('topic', tp.id)
      search.set('topicTitle', tp.title)
    }
    router.replace(search.size ? `/search?${search.toString()}` : '/search', { scroll: false })
  }
  const toggle = <T,>(list: T[], value: T) => (list.includes(value) ? list.filter((v) => v !== value) : [...list, value])
  const filtering = narrows && (kinds.length > 0 || sources.length > 0 || !!topic)
  const show = (x: Tab) => tab === 'all' || tab === x
  const open = (x: Tab) => {
    setTab(x)
    go({ tab: x })
  }
  /** On All, a section's heading leads to its tab. */
  const heading = (id: string, label: string, x: Tab) => (
    <div className="flex items-center justify-between gap-2">
      <h2 id={id} className="text-sm font-semibold text-muted">
        {label}
      </h2>
      {tab === 'all' ? (
        <button type="button" onClick={() => open(x)} aria-label={t('seeAllOf', { what: label })} className="text-xs font-semibold text-accent hover:underline">
          {t('seeAll')}
        </button>
      ) : null}
    </div>
  )
  const nothingHere = (n: number) => (searched && settled.length >= 2 && !n ? <p className="text-sm text-muted">{t('nothing', { query: settled })}</p> : null)
  const chip = (pressed: boolean) => cn('rounded-full border px-3 py-1 text-sm transition', pressed ? 'border-accent bg-accent-soft font-medium text-accent' : 'border-border bg-surface hover:border-accent hover:text-accent')

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <h1 className="text-2xl font-semibold">{t('title')}</h1>
      <label className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 shadow-sm focus-within:border-accent">
        <Search className="size-5 text-muted" aria-hidden />
        <span className="sr-only">{t('label')}</span>
        <input
          autoFocus
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            go({ q: e.target.value })
          }}
          placeholder={t('placeholder')}
          className="h-14 min-w-0 flex-1 border-0 bg-transparent text-lg placeholder:text-muted outline-none"
        />
      </label>
      <div role="tablist" aria-label={t('tabs.label')} className="-mx-1 flex gap-1 overflow-x-auto border-b border-border px-1">
        {TABS.map((x) => (
          <button
            key={x}
            role="tab"
            type="button"
            aria-selected={x === tab}
            onClick={() => open(x)}
            className={cn('-mb-px shrink-0 border-b-2 px-3 py-2 text-sm font-semibold', x === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg')}
          >
            {t(`tabs.${x}`)}
          </button>
        ))}
      </div>
      <div role="tabpanel" aria-label={t(`tabs.${tab}`)} className="flex flex-col gap-6">
        {narrows ? (
          <div className="flex flex-col gap-2" role="group" aria-label={t('filters.label')}>
            <div className="flex flex-wrap items-center gap-2">
              <span className="w-14 text-xs font-semibold text-muted">{t('filters.kind')}</span>
              {KINDS.map((k) => (
                <button
                  key={k}
                  type="button"
                  aria-pressed={kinds.includes(k)}
                  className={chip(kinds.includes(k))}
                  onClick={() => {
                    const next = toggle(kinds, k)
                    setKinds(next)
                    go({ kinds: next })
                  }}
                >
                  {t(`filters.kinds.${k}`)}
                </button>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span className="w-14 text-xs font-semibold text-muted">{t('filters.from')}</span>
              {SOURCES.map((s) => (
                <button
                  key={s}
                  type="button"
                  aria-pressed={sources.includes(s)}
                  className={chip(sources.includes(s))}
                  onClick={() => {
                    const next = toggle(sources, s)
                    setSources(next)
                    go({ sources: next })
                  }}
                >
                  {t(`filters.sources.${s}`)}
                </button>
              ))}
              {topic ? (
                <button
                  type="button"
                  aria-label={t('filters.clearTopic', { topic: topic.title })}
                  className={cn(chip(true), 'inline-flex items-center gap-1.5')}
                  onClick={() => {
                    setTopic(null)
                    go({ topic: null })
                  }}
                >
                  <BookBookmark className="size-3.5" aria-hidden />
                  {topic.title}
                  <X className="size-3.5" aria-hidden />
                </button>
              ) : null}
            </div>
          </div>
        ) : null}
        {!narrows && settled.length < 2 ? <p className="text-sm text-muted">{t(`hints.${tab}`)}</p> : null}
        {failed ? <LoadFailed onRetry={retry} /> : null}
        {tab === 'users' ? nothingHere(people.length) : null}
        {tab === 'groups' ? nothingHere(groups.length + classrooms.length) : null}
        {tab === 'resources' ? nothingHere(resources.length) : null}
        {tab === 'topics' ? nothingHere(topics.length) : null}
        {show('users') && people.length ? (
          <section aria-labelledby="people-heading" className="flex flex-col gap-2">
            {heading('people-heading', t('people'), 'users')}
            <ul className="flex flex-wrap gap-2">
              {people.map((p) => (
                <li key={p.id}>
                  <Link href={`/u/${p.handle}`} className="inline-flex items-center gap-2 rounded-full border border-border bg-surface py-1 pl-1 pr-3 text-sm hover:border-accent hover:text-accent">
                    <span aria-hidden className="grid size-7 place-items-center rounded-full bg-accent-soft text-xs font-semibold text-accent">
                      {p.displayName.slice(0, 1).toUpperCase()}
                    </span>
                    {p.displayName} <span className="text-muted">@{p.handle}</span>
                    {p.globalRole === 'TEACHER' ? <span className="rounded-[4px] bg-accent-soft px-1.5 text-[10px] font-semibold text-accent">{t('teacher')}</span> : null}
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
        {show('groups') && (groups.length || classrooms.length) ? (
          <section aria-labelledby="places-heading" className="flex flex-col gap-2">
            {heading('places-heading', t('places'), 'groups')}
            <ul className="grid gap-2 sm:grid-cols-2">
              {groups.map((g) => (
                <li key={g.id}>
                  <Link href={`/groups/${g.id}`} className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent/40">
                    <Users className="size-4 shrink-0 text-accent" aria-hidden />
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate font-medium">{g.name}</span>
                      <span className="text-xs text-muted">
                        {t(g.type === 'PROJECT' ? 'workspace' : g.privacy === 'PRIVATE' ? 'privateGroup' : 'group')} · {t('members', { count: g.memberCount })}
                      </span>
                    </span>
                  </Link>
                </li>
              ))}
              {classrooms.map((c) => (
                <li key={c.id}>
                  <Link href={`/classes/${c.id}`} className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent/40">
                    <GraduationCap className="size-4 shrink-0 text-accent" aria-hidden />
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate font-medium">{c.name}</span>
                      <span className="text-xs text-muted">
                        {t('classroom')} · {t('members', { count: c.memberCount })}
                      </span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
        {show('resources') && resources.length ? (
          <section aria-labelledby="resources-heading" className="flex flex-col gap-2">
            {heading('resources-heading', t('resources'), 'resources')}
            <ul className="grid gap-2 sm:grid-cols-2">
              {resources.map((r) => (
                <li key={r.id}>
                  <Link href={`/resources/${r.id}`} className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent/40">
                    <Library className="size-4 shrink-0 text-accent" aria-hidden />
                    <span className="flex min-w-0 flex-col">
                      <span className="truncate font-medium">{r.title}</span>
                      <span className="text-xs text-muted">
                        {r.author ? `${r.author} · ` : ''}
                        {r.host}
                      </span>
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
        {show('topics') && topics.length ? (
          <section aria-labelledby="topics-heading" className="flex flex-col gap-2">
            {heading('topics-heading', t('topics'), 'topics')}
            <div className="flex flex-wrap gap-2">
              {topics.map((tp) => (
                <button
                  key={tp.id}
                  type="button"
                  onClick={() => {
                    // A topic lists its notes: from the Topics tab, in Notes.
                    const chosen = { id: tp.id, title: tp.title }
                    const where = tab === 'topics' ? 'notes' : tab
                    setTopic(chosen)
                    setQuery('')
                    setTab(where)
                    go({ q: '', topic: chosen, tab: where })
                  }}
                  className="inline-flex items-center gap-1.5 rounded-[4px] border border-border bg-surface px-3 py-1.5 text-sm hover:border-accent hover:text-accent"
                >
                  <BookBookmark className="size-3.5" aria-hidden />
                  {tp.title} <span className="text-muted">· {tp.subject.title}</span>
                </button>
              ))}
            </div>
          </section>
        ) : null}
        {narrows ? (
          <section aria-labelledby="notes-heading" aria-busy={loading} className="flex flex-col gap-3">
            <h2 id="notes-heading" className="text-sm font-semibold text-muted">
              {settled.length < 2 && filtering ? t('newest') : t('notes')}
            </h2>
            {loading && !notes.length && settled ? <StudyLoader kind="search" compact className="py-4" /> : null}
            {searched && !notes.length ? <p className="text-sm text-muted">{settled ? t('nothing', { query: settled }) : t('nothingFiltered')}</p> : null}
            {!settled && !filtering ? <p className="text-sm text-muted">{t('hint')}</p> : null}
            <ul className="flex flex-col gap-3">
              {notes.map(({ note, snippet }) => {
                const Icon = VISIBILITY_ICON[note.visibility]
                return (
                  <li key={note.id}>
                    <Link href={`/notes/${note.id}`} className="group flex flex-col gap-1.5 rounded-2xl border border-border bg-surface p-4 transition-colors hover:border-accent/40 hover:border-fg/20">
                      <span className="flex items-center gap-2 font-semibold">
                        <FileText className="size-4 text-accent" aria-hidden />
                        {note.title || t('untitled')}
                        {note.kind !== 'NOTE' ? <span className="rounded-full bg-surface-2 px-2 text-[11px] font-medium text-muted">{t(`filters.kinds.${note.kind}`)}</span> : null}
                      </span>
                      {snippet ? <Snippet text={snippet} className="text-sm leading-6 text-muted" /> : null}
                      <span className="flex items-center gap-1.5 text-xs text-muted">
                        <Icon className="size-3.5" aria-hidden />
                        {t(`visibility.${note.visibility}`)} · {t('by', { name: note.owner.displayName })}
                      </span>
                    </Link>
                  </li>
                )
              })}
            </ul>
            {hasMore ? (
              <Button variant="secondary" className="self-center" disabled={loadingMore} onClick={() => void more()}>
                {loadingMore ? t('loadingMore') : t('more')}
              </Button>
            ) : null}
          </section>
        ) : null}
      </div>
    </div>
  )
}
