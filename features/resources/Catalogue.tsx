'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Bookmark, BookmarkCheck, BookOpen, Cpu, GraduationCap, Library, Plus, Wrench } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import { ResourcesDocument, SaveResourceDocument, UnsaveResourceDocument, type ResourceFieldsFragment, type ResourceSort, type ResourceType } from '@/graphql/generated/graphql'
import { useSession } from '@/state/session'
import { RESOURCE_TYPES } from './ResourceForm'

export const TYPE_ICON: Record<ResourceType, typeof BookOpen> = { BOOK: BookOpen, COURSE: GraduationCap, TOOL: Wrench, SOFTWARE: Cpu, HARDWARE: Cpu, OTHER: Library }

/** The catalogue (lvn-backend ADR-0075): approved resources for everyone, filtered by type and words, most saved first. */
export function Catalogue() {
  return (
    <AuthProvider>
      <Inner />
    </AuthProvider>
  )
}

function Inner() {
  const t = useTranslations('resources.catalogue')
  const types = useTranslations('resources.type')
  const status = useSession((s) => s.status)
  const [typed, setTyped] = useState('')
  const [query, setQuery] = useState('')
  const [type, setType] = useState<ResourceType | null>(null)
  const [sort, setSort] = useState<ResourceSort>('POPULAR')
  useEffect(() => {
    const timer = setTimeout(() => setQuery(typed.trim()), 250)
    return () => clearTimeout(timer)
  }, [typed])
  const { data, fetchMore, loading, error, refetch } = useQuery(ResourcesDocument, { variables: { filter: { type, query: query || null }, sort, first: 24 }, skip: status === 'unknown', fetchPolicy: 'cache-and-network' })
  const items = data?.resources.edges.map((e) => e.node) ?? []
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8">
      <header className="flex flex-wrap items-end justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-3xl font-semibold tracking-tight">{t('title')}</h1>
          <p className="max-w-2xl text-sm text-muted">{t('lead')}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {status === 'signed-in' ? (
            <Button asChild variant="secondary" size="sm">
              <Link href="/saved">{t('saved')}</Link>
            </Button>
          ) : null}
          <Button asChild size="sm" className="gap-1.5">
            <Link href="/resources/new">
              <Plus className="size-4" aria-hidden />
              {t('add')}
            </Link>
          </Button>
        </div>
      </header>
      <div className="flex flex-col gap-3">
        <input type="search" value={typed} onChange={(e) => setTyped(e.target.value)} placeholder={t('search')} aria-label={t('search')} className="h-11 rounded-xl border border-border bg-surface px-3 text-sm" />
        <div className="flex flex-wrap items-center gap-2">
          <div role="radiogroup" aria-label={t('typeFilter')} className="flex flex-wrap gap-2">
            {[null, ...RESOURCE_TYPES].map((v) => (
              <button key={v ?? 'all'} type="button" role="radio" aria-checked={type === v} onClick={() => setType(v)} className={`rounded-full border px-3 py-1.5 text-sm ${type === v ? 'border-accent bg-accent-soft font-semibold text-accent' : 'border-border bg-surface hover:border-accent'}`}>
                {v ? types(v) : t('all')}
              </button>
            ))}
          </div>
          <label className="ml-auto flex items-center gap-2 text-sm text-muted">
            {t('sort')}
            <select value={sort} onChange={(e) => setSort(e.target.value as ResourceSort)} className="h-9 rounded-lg border border-border bg-surface px-2 text-fg">
              <option value="POPULAR">{t('popular')}</option>
              <option value="NEWEST">{t('newest')}</option>
            </select>
          </label>
        </div>
      </div>
      {!data ? <QueryState loading={loading || status === 'unknown'} error={error} onRetry={refetch} /> : null}
      {data && !items.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-12 text-center text-sm text-muted">{t('none')}</p> : null}
      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((r) => (
          <li key={r.id}>
            <ResourceCard resource={r} />
          </li>
        ))}
      </ul>
      {data?.resources.pageInfo.hasNextPage ? (
        <Button
          variant="secondary"
          className="self-center"
          disabled={loading}
          onClick={() =>
            void fetchMore({
              variables: { after: data.resources.pageInfo.endCursor },
              updateQuery: (prev, { fetchMoreResult }) => ({ resources: { ...fetchMoreResult.resources, edges: [...prev.resources.edges, ...fetchMoreResult.resources.edges] } }),
            })
          }
        >
          {t('more')}
        </Button>
      ) : null}
    </div>
  )
}

/** One resource in a list: its picture or type, title, by, site and saves, with the viewer's Save. */
export function ResourceCard({ resource: r, note }: { resource: ResourceFieldsFragment; note?: React.ReactNode }) {
  const types = useTranslations('resources.type')
  const t = useTranslations('resources')
  const Icon = TYPE_ICON[r.type]
  return (
    <article aria-label={r.title} className="flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-surface shadow-sm transition hover:border-accent">
      <Link href={`/resources/${r.id}`} className="flex flex-1 flex-col">
        <div className="flex h-32 items-center justify-center bg-accent-soft">
          {r.coverUrl ? (
            // eslint-disable-next-line @next/next/no-img-element -- a short-lived read URL from storage
            <img src={r.coverUrl} alt="" className="h-full w-full object-contain p-2" />
          ) : (
            <Icon className="size-10 text-accent" aria-hidden />
          )}
        </div>
        <div className="flex flex-1 flex-col gap-1 p-4">
          <span className="text-xs font-semibold text-accent">{types(r.type)}</span>
          <span className="line-clamp-2 font-semibold">{r.title}</span>
          {r.author ? <span className="truncate text-sm text-muted">{t('by', { author: r.author })}</span> : null}
          <span className="mt-auto text-xs text-muted">{r.host}</span>
          {note}
        </div>
      </Link>
      <div className="flex items-center justify-between border-t border-border px-4 py-2">
        <span className="text-xs text-muted">{t('saves', { count: r.saveCount })}</span>
        <SaveButton resource={r} />
      </div>
    </article>
  )
}

/** Save and unsave (private: only the count is public); signed out, it asks to sign in. */
export function SaveButton({ resource: r, size = 'sm' }: { resource: Pick<ResourceFieldsFragment, 'id' | 'viewerSaved' | 'saveCount' | 'status'>; size?: 'sm' | 'md' }) {
  const t = useTranslations('resources')
  const status = useSession((s) => s.status)
  const path = usePathname()
  const [save, saving] = useMutation(SaveResourceDocument)
  const [unsave, unsaving] = useMutation(UnsaveResourceDocument)
  if (r.status !== 'APPROVED') return null
  if (status !== 'signed-in') {
    return (
      <Link href={`/sign-in?next=${encodeURIComponent(path)}`} className="inline-flex items-center gap-1 text-sm font-semibold text-accent hover:underline">
        <Bookmark className="size-4" aria-hidden />
        {t('save')}
      </Link>
    )
  }
  const Icon = r.viewerSaved ? BookmarkCheck : Bookmark
  return (
    <Button
      type="button"
      size={size}
      variant={r.viewerSaved ? 'secondary' : 'ghost'}
      aria-pressed={r.viewerSaved}
      disabled={saving.loading || unsaving.loading}
      className="gap-1.5"
      onClick={() => void (r.viewerSaved ? unsave : save)({ variables: { input: { id: r.id } } })}
    >
      <Icon className="size-4" aria-hidden />
      {r.viewerSaved ? t('savedOne') : t('save')}
    </Button>
  )
}
