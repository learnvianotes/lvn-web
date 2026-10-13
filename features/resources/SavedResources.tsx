'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { SavedResourcesDocument } from '@/graphql/generated/graphql'
import { ResourceCard } from './Catalogue'

/** The viewer's saved resources (lvn-backend ADR-0075), newest first, private to them: a section of Bookmarks. */
export function SavedResourcesList() {
  const t = useTranslations('resources.savedList')
  const { data } = useQuery(SavedResourcesDocument, { variables: { first: 60 }, fetchPolicy: 'cache-and-network' })
  const items = data?.savedResources.edges.map((e) => e.node) ?? []
  return (
    <>
      {data && !items.length ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-sm text-muted">
          {t('none')}{' '}
          <Link href="/resources" className="font-semibold text-accent hover:underline">
            {t('browse')}
          </Link>
        </p>
      ) : null}
      <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((r) => (
          <li key={r.id}>
            <ResourceCard resource={r} />
          </li>
        ))}
      </ul>
    </>
  )
}
