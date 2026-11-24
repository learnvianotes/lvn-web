'use client'

import { useQuery } from '@apollo/client/react'
import { FileText } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { SavedNotesDocument } from '@/graphql/generated/graphql'
import { SavedResourcesList } from '@/features/resources/SavedResources'

/**
 * Bookmarks (lvn-backend ADR-0076): the notes and resources the person saved, private to them, newest first. Each
 * section offers a way to find more when it is empty.
 */
export function SavedPage() {
  const t = useTranslations('saved')
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <SavedNotes />
      <section aria-labelledby="saved-resources" className="flex flex-col gap-3">
        <h2 id="saved-resources" className="text-lg font-semibold">
          {t('resources')}
        </h2>
        <SavedResourcesList />
      </section>
    </div>
  )
}

function SavedNotes() {
  const t = useTranslations('saved')
  const { data, fetchMore } = useQuery(SavedNotesDocument, { variables: { first: 30 }, fetchPolicy: 'cache-and-network' })
  const notes = data?.savedNotes.edges.map((e) => e.node) ?? []
  const page = data?.savedNotes.pageInfo
  return (
    <section aria-labelledby="saved-notes" className="flex flex-col gap-3">
      <h2 id="saved-notes" className="text-lg font-semibold">
        {t('notes')}
      </h2>
      {data && !notes.length && !page?.hasNextPage ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-sm text-muted">
          {t('noNotes')}{' '}
          <Link href="/search" className="font-semibold text-accent hover:underline">
            {t('findNotes')}
          </Link>
        </p>
      ) : null}
      <ul className="grid gap-3 sm:grid-cols-2">
        {notes.map((n) => (
          <li key={n.id}>
            <Link href={`/notes/${n.id}`} className="flex h-full gap-3 rounded-2xl border border-border bg-surface p-4 hover:border-accent">
              <FileText className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
              <span className="flex min-w-0 flex-col gap-1">
                <span className="truncate font-semibold">{n.title || t('untitled')}</span>
                {n.excerpt ? <span className="line-clamp-2 text-sm text-muted">{n.excerpt}</span> : null}
                <span className="text-xs text-muted">{t('by', { name: n.owner.displayName })}</span>
              </span>
            </Link>
          </li>
        ))}
      </ul>
      {page?.hasNextPage ? (
        <button type="button" className="self-start text-sm font-semibold text-accent hover:underline" onClick={() => void fetchMore({ variables: { after: page.endCursor }, updateQuery: (prev, { fetchMoreResult }) => ({ savedNotes: { ...fetchMoreResult.savedNotes, edges: [...prev.savedNotes.edges, ...fetchMoreResult.savedNotes.edges] } }) })}>
          {t('more')}
        </button>
      ) : null}
    </section>
  )
}
