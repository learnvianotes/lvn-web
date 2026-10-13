'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { SavedResourcesDocument } from '@/graphql/generated/graphql'
import { ResourceCard } from './Catalogue'

/** The viewer's Saved resources (lvn-backend ADR-0075), newest first: private to them. */
export function SavedResources() {
  const t = useTranslations('resources.savedList')
  const { data } = useQuery(SavedResourcesDocument, { variables: { first: 60 }, fetchPolicy: 'cache-and-network' })
  const items = data?.savedResources.edges.map((e) => e.node) ?? []
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {data && !items.length ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-sm text-muted">
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
    </div>
  )
}
