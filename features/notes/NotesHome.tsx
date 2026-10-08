'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { BookOpen, ChevronRight, FileText, Folder, FolderPlus, Hash, Layers, ListChecks, MoreHorizontal, NotebookPen, Plus, RotateCcw, Search, Sparkles, Trash2, Inbox } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { NightSky } from '@/components/brand/NightSky'
import {
  CreateFolderDocument,
  CreateNoteDocument,
  DeleteFolderDocument,
  DeleteNoteForeverDocument,
  MyNotesDocument,
  OrganiseDocument,
  RestoreNoteDocument,
  UpdateFolderDocument,
  ViewerDocument,
  type NoteFilter,
  type NoteListFieldsFragment,
} from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { NotebookArt } from './art'
import { accentOf, ago, daypart } from './look'
import { TEMPLATE_KEYS, templateCards, type TemplateKey } from './templates'

type View = { kind: 'all' } | { kind: 'unfiled' } | { kind: 'trash' } | { kind: 'folder'; id: string } | { kind: 'tag'; id: string }

function viewFrom(params: URLSearchParams): View {
  const folder = params.get('folder')
  const tag = params.get('tag')
  const view = params.get('view')
  if (folder) return { kind: 'folder', id: folder }
  if (tag) return { kind: 'tag', id: tag }
  if (view === 'trash' || view === 'unfiled') return { kind: view }
  return { kind: 'all' }
}

const hrefOf = (v: View) => (v.kind === 'folder' ? `/notes?folder=${v.id}` : v.kind === 'tag' ? `/notes?tag=${v.id}` : v.kind === 'all' ? '/notes' : `/notes?view=${v.kind}`)
const filterOf = (v: View): NoteFilter => (v.kind === 'folder' ? { folderId: v.id } : v.kind === 'tag' ? { tagId: v.id } : v.kind === 'unfiled' ? { unfiled: true } : v.kind === 'trash' ? { trashed: true } : {})

const TEMPLATE_ICONS: Record<TemplateKey, typeof NotebookPen> = { lecture: NotebookPen, revision: ListChecks, flashcards: Layers, quiz: Sparkles }

/** The viewer's notes (lvn-backend §4.1, §4.5): a welcome, templates to start from, notes as cards, folders, tags and the trash. */
export function NotesHome() {
  const t = useTranslations('notes.home')
  const router = useRouter()
  const view = viewFrom(useSearchParams())
  const viewer = useQuery(ViewerDocument)
  const organise = useQuery(OrganiseDocument)
  const notes = useQuery(MyNotesDocument, { variables: { filter: filterOf(view), first: 30 }, fetchPolicy: 'cache-and-network' })
  const [create, creating] = useMutation(CreateNoteDocument)
  const [createFolder] = useMutation(CreateFolderDocument)
  const [updateFolder] = useMutation(UpdateFolderDocument)
  const [deleteFolder] = useMutation(DeleteFolderDocument)
  const [restore] = useMutation(RestoreNoteDocument)
  const [destroy] = useMutation(DeleteNoteForeverDocument)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const folders = organise.data?.myFolders ?? []
  const tags = organise.data?.myTags ?? []
  const all = useMemo(() => notes.data?.myNotes.edges.map((e) => e.node) ?? [], [notes.data])
  const q = query.trim().toLowerCase()
  const shown = q ? all.filter((n) => `${n.title} ${n.excerpt} ${n.tags.map((x) => x.name).join(' ')}`.toLowerCase().includes(q)) : all
  const refresh = () => Promise.all([organise.refetch(), notes.refetch()])
  const firstName = viewer.data?.viewer?.displayName.split(' ')[0] ?? ''

  const newNote = async (template?: TemplateKey) => {
    const res = await create({
      variables: { input: { ...(view.kind === 'folder' ? { folderId: view.id } : {}), ...(template ? { title: t(`templates.${template}.title`), cards: templateCards(template) } : {}) } },
    })
    const id = res.data?.createNote.note?.id
    if (id) router.push(`/notes/${id}`)
    else setError(res.data?.createNote.userErrors[0]?.message ?? t('createFailed'))
  }
  const addFolder = async (parentId: string | null) => {
    const name = window.prompt(t('folderName'))
    if (!name?.trim()) return
    const res = await createFolder({ variables: { name, parentId } })
    if (res.data?.createFolder.userErrors.length) setError(res.data.createFolder.userErrors[0]!.message)
    await organise.refetch()
  }
  const renameFolder = async (id: string, current: string) => {
    const name = window.prompt(t('folderName'), current)
    if (!name?.trim() || name === current) return
    const res = await updateFolder({ variables: { input: { id, name } } })
    if (res.data?.updateFolder.userErrors.length) setError(res.data.updateFolder.userErrors[0]!.message)
    await organise.refetch()
  }
  const removeFolder = async (id: string, name: string) => {
    if (!window.confirm(t('deleteFolderConfirm', { name }))) return
    await deleteFolder({ variables: { id } })
    if (view.kind === 'folder' && view.id === id) router.push('/notes')
    await refresh()
  }

  const depth = (id: string | null | undefined): number => (id ? 1 + depth(folders.find((f) => f.id === id)?.parentId) : 0)
  const ordered = (parentId: string | null): typeof folders => folders.filter((f) => (f.parentId ?? null) === parentId).flatMap((f) => [f, ...ordered(f.id)])
  const navItem = (v: View, label: string, Icon: typeof Folder, count?: number) => {
    const active = hrefOf(v) === hrefOf(view)
    return (
      <Link href={hrefOf(v)} aria-current={active ? 'page' : undefined} className={cn('group flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm transition-colors', active ? 'bg-accent-soft font-semibold text-accent' : 'text-muted hover:bg-surface-2 hover:text-fg')}>
        <Icon className="size-4 shrink-0" aria-hidden />
        <span className="min-w-0 flex-1 truncate">{label}</span>
        {count !== undefined ? <span className={cn('rounded-full px-1.5 text-xs', active ? 'bg-accent/10' : 'bg-surface-2')}>{count}</span> : null}
      </Link>
    )
  }
  const heading = view.kind === 'folder' ? (folders.find((f) => f.id === view.id)?.name ?? t('folder')) : view.kind === 'tag' ? `#${tags.find((x) => x.id === view.id)?.name ?? ''}` : t(`views.${view.kind}`)
  const latest = view.kind === 'all' ? all[0] : undefined

  return (
    <div className="grid gap-6 md:grid-cols-[15rem_minmax(0,1fr)]">
      <aside className="hidden flex-col gap-5 md:sticky md:top-20 md:flex md:self-start">
        <Button size="lg" className="w-full gap-2 shadow-lg shadow-accent/20" disabled={creating.loading || view.kind === 'trash'} onClick={() => void newNote()}>
          <Plus className="size-5" aria-hidden />
          {t('newNote')}
        </Button>
        <nav aria-label={t('views.label')} className="flex flex-col gap-0.5">
          {navItem({ kind: 'all' }, t('views.all'), BookOpen)}
          {navItem({ kind: 'unfiled' }, t('views.unfiled'), Inbox)}
          {navItem({ kind: 'trash' }, t('views.trash'), Trash2)}
        </nav>
        <section aria-labelledby="folders-heading" className="flex flex-col gap-0.5">
          <div className="flex items-center justify-between px-3 pb-1">
            <h2 id="folders-heading" className="text-xs font-semibold uppercase tracking-wider text-muted">
              {t('folders')}
            </h2>
            <button type="button" className="rounded-lg p-1 text-muted hover:bg-surface-2 hover:text-accent" aria-label={t('newFolder')} title={t('newFolder')} onClick={() => void addFolder(null)}>
              <FolderPlus className="size-4" aria-hidden />
            </button>
          </div>
          {ordered(null).map((f) => (
            <div key={f.id} className="group flex items-center" style={{ paddingLeft: `${depth(f.parentId) * 0.85}rem` }}>
              <div className="min-w-0 flex-1">{navItem({ kind: 'folder', id: f.id }, f.name, Folder, f.noteCount)}</div>
              <details className="relative">
                <summary className="cursor-pointer list-none rounded-lg p-1 text-muted opacity-60 hover:bg-surface-2 hover:opacity-100" aria-label={t('folderActions', { name: f.name })}>
                  <MoreHorizontal className="size-4" aria-hidden />
                </summary>
                <div className="absolute right-0 z-20 mt-1 flex w-44 flex-col rounded-xl border border-border bg-surface p-1 text-sm shadow-xl">
                  <button type="button" className="rounded-lg px-3 py-1.5 text-left hover:bg-surface-2" onClick={() => void addFolder(f.id)}>
                    {t('newSubfolder')}
                  </button>
                  <button type="button" className="rounded-lg px-3 py-1.5 text-left hover:bg-surface-2" onClick={() => void renameFolder(f.id, f.name)}>
                    {t('rename')}
                  </button>
                  <button type="button" className="rounded-lg px-3 py-1.5 text-left text-red-600 hover:bg-surface-2 dark:text-red-400" onClick={() => void removeFolder(f.id, f.name)}>
                    {t('delete')}
                  </button>
                </div>
              </details>
            </div>
          ))}
          {!folders.length && organise.data ? <p className="px-3 text-sm text-muted">{t('noFolders')}</p> : null}
        </section>
        {tags.length ? (
          <section aria-labelledby="tags-heading" className="flex flex-col gap-1.5 px-1">
            <h2 id="tags-heading" className="px-2 text-xs font-semibold uppercase tracking-wider text-muted">
              {t('tags')}
            </h2>
            <div className="flex flex-wrap gap-1.5">
              {tags.map((x) => {
                const active = view.kind === 'tag' && view.id === x.id
                return (
                  <Link key={x.id} href={hrefOf({ kind: 'tag', id: x.id })} aria-current={active ? 'page' : undefined} className={cn('inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs transition-colors', active ? 'border-accent bg-accent text-accent-fg' : 'border-border bg-surface text-muted hover:border-accent hover:text-accent')}>
                    <Hash className="size-3" aria-hidden />
                    {x.name}
                  </Link>
                )
              })}
            </div>
          </section>
        ) : null}
      </aside>

      <section aria-labelledby="notes-heading" className="flex min-w-0 flex-col gap-6">
        {view.kind === 'all' ? (
          <NightSky as="section" className="rounded-3xl px-6 py-7 sm:px-8">
            <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex animate-rise flex-col gap-1.5">
                <p className="text-sm font-medium text-[#C7D2FE]">{t(`greeting.${daypart()}`, { name: firstName })}</p>
                <h1 id="notes-heading" className="text-2xl font-extrabold tracking-tight sm:text-3xl">
                  {all.length ? t('heroWithNotes') : t('heroFirst')}
                </h1>
                <Button size="lg" className="mt-3 w-fit gap-2 bg-white text-[#1C1A3A] hover:bg-white/90 md:hidden" disabled={creating.loading} onClick={() => void newNote()}>
                  <Plus className="size-5" aria-hidden />
                  {t('newNote')}
                </Button>
                {latest ? (
                  <Link href={`/notes/${latest.id}`} className="mt-2 inline-flex w-fit max-w-full items-center gap-2 rounded-full bg-white/10 py-1.5 pl-3 pr-2 text-sm font-medium ring-1 ring-white/20 transition hover:bg-white/20">
                    <span className="truncate">
                      {t('continue')} <strong className="font-semibold">{latest.title || t('untitled')}</strong>
                    </span>
                    <ChevronRight className="size-4 shrink-0" aria-hidden />
                  </Link>
                ) : null}
              </div>
              <NotebookArt className="hidden w-36 shrink-0 drop-shadow-xl sm:block" />
            </div>
          </NightSky>
        ) : (
          <h1 id="notes-heading" className="text-2xl font-extrabold tracking-tight">
            {heading}
          </h1>
        )}

        {/* Phones: the views and folders as one row to scroll, instead of the sidebar. */}
        <nav aria-label={t('views.label')} className="-mx-4 flex gap-2 overflow-x-auto px-4 pb-1 [scrollbar-width:none] md:hidden">
          {[
            { v: { kind: 'all' } as View, label: t('views.all'), icon: BookOpen },
            { v: { kind: 'unfiled' } as View, label: t('views.unfiled'), icon: Inbox },
            ...folders.map((f) => ({ v: { kind: 'folder', id: f.id } as View, label: f.name, icon: Folder })),
            ...tags.map((x) => ({ v: { kind: 'tag', id: x.id } as View, label: `#${x.name}`, icon: Hash })),
            { v: { kind: 'trash' } as View, label: t('views.trash'), icon: Trash2 },
          ].map(({ v, label, icon: Icon }) => {
            const active = hrefOf(v) === hrefOf(view)
            return (
              <Link key={hrefOf(v)} href={hrefOf(v)} aria-current={active ? 'page' : undefined} className={cn('inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm', active ? 'border-accent bg-accent text-accent-fg' : 'border-border bg-surface text-muted')}>
                <Icon className="size-4" aria-hidden />
                {label}
              </Link>
            )
          })}
          <button type="button" className="inline-flex shrink-0 items-center gap-1.5 rounded-full border border-dashed border-border px-3 py-1.5 text-sm text-muted" onClick={() => void addFolder(null)}>
            <FolderPlus className="size-4" aria-hidden />
            {t('newFolder')}
          </button>
        </nav>

        {view.kind !== 'trash' ? (
          <section aria-labelledby="templates-heading" className="flex flex-col gap-3">
            <h2 id="templates-heading" className="text-sm font-semibold text-muted">
              {t('startFrom')}
            </h2>
            <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
              {TEMPLATE_KEYS.map((key, i) => {
                const Icon = TEMPLATE_ICONS[key]
                return (
                  <button
                    key={key}
                    type="button"
                    disabled={creating.loading}
                    onClick={() => void newNote(key)}
                    className="group flex animate-rise flex-col items-start gap-2 rounded-2xl border border-border bg-surface p-4 text-left transition hover:-translate-y-0.5 hover:border-accent/40 hover:shadow-lg hover:shadow-accent/10 active:scale-[0.98]"
                    style={{ animationDelay: `${60 * i}ms` }}
                  >
                    <span className="grid size-9 place-items-center rounded-xl bg-accent-soft text-accent transition group-hover:bg-accent group-hover:text-accent-fg">
                      <Icon className="size-5" aria-hidden />
                    </span>
                    <span className="text-sm font-semibold">{t(`templates.${key}.title`)}</span>
                    <span className="text-xs leading-5 text-muted">{t(`templates.${key}.lead`)}</span>
                  </button>
                )
              })}
            </div>
          </section>
        ) : null}

        <div className="flex flex-col gap-3">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-muted">{view.kind === 'all' ? t('recent') : view.kind === 'trash' ? t('trashHint') : t('inHere', { n: all.length })}</h2>
            {all.length > 3 ? (
              <label className="relative w-full sm:w-64">
                <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
                <span className="sr-only">{t('search')}</span>
                <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('search')} className="h-10 w-full rounded-full border border-border bg-surface pl-9 pr-3 text-sm placeholder:text-muted focus-visible:border-accent focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/30" />
              </label>
            ) : null}
          </div>
          {error ? (
            <p role="alert" className="rounded-xl border border-red-600/30 bg-red-50 px-4 py-3 text-sm text-red-900 dark:bg-red-950/40 dark:text-red-200">
              {error}
            </p>
          ) : null}
          {notes.loading && !notes.data ? (
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3" aria-hidden>
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-40 animate-pulse rounded-2xl bg-surface-2" />
              ))}
            </div>
          ) : null}
          {notes.data && !all.length ? (
            <div className="flex flex-col items-center gap-3 rounded-3xl border border-dashed border-border bg-surface/60 px-6 py-12 text-center">
              <NotebookArt className="w-40" />
              <p className="text-lg font-semibold">{t(view.kind === 'trash' ? 'emptyTrash' : 'empty')}</p>
              <p className="max-w-sm text-sm text-muted">{t(view.kind === 'trash' ? 'emptyTrashLead' : 'emptyLead')}</p>
            </div>
          ) : null}
          {q && !shown.length && all.length ? <p className="text-sm text-muted">{t('noMatch', { query })}</p> : null}
          <ul className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {shown.map((n, i) => (
              <li key={n.id} className="animate-rise" style={{ animationDelay: `${Math.min(i, 8) * 40}ms` }}>
                <NoteTile
                  note={n}
                  trash={view.kind === 'trash'}
                  onRestore={async () => {
                    await restore({ variables: { noteId: n.id } })
                    await refresh()
                  }}
                  onDestroy={async () => {
                    if (!window.confirm(t('deleteForeverConfirm'))) return
                    await destroy({ variables: { noteId: n.id } })
                    await refresh()
                  }}
                />
              </li>
            ))}
          </ul>
          {notes.data?.myNotes.pageInfo.hasNextPage ? (
            <Button
              variant="secondary"
              className="self-center"
              onClick={() =>
                void notes.fetchMore({
                  variables: { after: notes.data!.myNotes.pageInfo.endCursor },
                  updateQuery: (prev, { fetchMoreResult }) => ({ myNotes: { ...fetchMoreResult.myNotes, edges: [...prev.myNotes.edges, ...fetchMoreResult.myNotes.edges] } }),
                })
              }
            >
              {t('more')}
            </Button>
          ) : null}
        </div>
      </section>
    </div>
  )
}

/** One note as a card: its accent, title, first words, and where it lives. */
function NoteTile({ note: n, trash, onRestore, onDestroy }: { note: NoteListFieldsFragment; trash: boolean; onRestore: () => void; onDestroy: () => void }) {
  const t = useTranslations('notes.home')
  const accent = accentOf(n.id)
  const body = (
    <>
      <span aria-hidden className="absolute inset-x-0 top-0 h-1.5 rounded-t-2xl" style={{ background: `linear-gradient(90deg, ${accent.from}, ${accent.to})` }} />
      <span aria-hidden className="absolute -right-10 -top-10 size-28 rounded-full blur-2xl transition-opacity group-hover:opacity-100" style={{ background: accent.tint, opacity: 0.8 }} />
      <span className="relative flex items-start gap-3">
        <span className="grid size-9 shrink-0 place-items-center rounded-xl text-sm font-bold text-white shadow-sm" style={{ background: `linear-gradient(135deg, ${accent.from}, ${accent.to})` }} aria-hidden>
          {(n.title || t('untitled')).trim().charAt(0).toUpperCase()}
        </span>
        <span className="min-w-0 flex-1">
          <span className="line-clamp-2 font-semibold leading-snug">{n.title || t('untitled')}</span>
          <span className="mt-0.5 block text-xs text-muted">{t('edited', { when: ago(trash ? n.deletedAt : n.draftUpdatedAt) })}</span>
        </span>
      </span>
      <span className="relative line-clamp-3 min-h-[3.75rem] text-sm leading-5 text-muted">{n.excerpt || t('noWordsYet')}</span>
      <span className="relative mt-auto flex flex-wrap items-center gap-1.5 text-xs text-muted">
        <span className="inline-flex items-center gap-1 rounded-full bg-surface-2 px-2 py-0.5">
          <FileText className="size-3" aria-hidden />
          {t('cards', { n: n.cardCount })}
        </span>
        {n.folder ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-surface-2 px-2 py-0.5">
            <Folder className="size-3" aria-hidden />
            {n.folder.name}
          </span>
        ) : null}
        {n.publishedAt ? <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 font-medium text-emerald-700 dark:text-emerald-400">{t('published')}</span> : null}
        {n.tags.slice(0, 3).map((x) => (
          <span key={x.id} className="rounded-full px-1.5 py-0.5" style={{ background: accent.tint }}>
            #{x.name}
          </span>
        ))}
      </span>
    </>
  )
  const tile = 'group relative flex h-full flex-col gap-3 overflow-hidden rounded-2xl border border-border bg-surface p-4 pt-5 transition'
  if (trash) {
    return (
      <div className={tile}>
        {body}
        <span className="relative flex gap-2">
          <Button size="sm" variant="secondary" className="gap-1.5" onClick={onRestore}>
            <RotateCcw className="size-4" aria-hidden />
            {t('restore')}
          </Button>
          <Button size="sm" variant="ghost" onClick={onDestroy}>
            {t('deleteForever')}
          </Button>
        </span>
      </div>
    )
  }
  return (
    <Link href={`/notes/${n.id}`} className={cn(tile, 'hover:-translate-y-0.5 hover:shadow-xl hover:shadow-accent/10 focus-visible:-translate-y-0.5 active:scale-[0.99]')}>
      {body}
    </Link>
  )
}
