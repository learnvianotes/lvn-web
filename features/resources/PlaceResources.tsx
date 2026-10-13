'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { RemoveResourceRecommendationDocument, ResourceRecommendationsDocument } from '@/graphql/generated/graphql'
import { ResourceCard } from './Catalogue'

/**
 * A group's or class's Resources tab (lvn-backend ADR-0075): what members recommended, each with who and why; its sender,
 * the group's moderators or the class's staff remove one.
 */
export function PlaceResources({ to }: { to: { groupId: string } | { classroomId: string } }) {
  const t = useTranslations('resources.place')
  const { data, refetch } = useQuery(ResourceRecommendationsDocument, { variables: { to, first: 30 }, fetchPolicy: 'cache-and-network' })
  const [remove] = useMutation(RemoveResourceRecommendationDocument)
  const items = data?.resourceRecommendations.edges.map((e) => e.node) ?? []
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm text-muted">{t('lead')}</p>
        <Link href="/resources" className="text-sm font-semibold text-accent hover:underline">
          {t('browse')}
        </Link>
      </div>
      {data && !items.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-sm text-muted">{t('none')}</p> : null}
      <ul className="grid gap-4 sm:grid-cols-2">
        {items.map((r) => (
          <li key={r.id} className="flex flex-col gap-2">
            <ResourceCard
              resource={r.resource}
              note={
                <span className="mt-2 rounded-lg bg-surface-2 px-2 py-1 text-xs">
                  <span className="font-semibold">{r.from.displayName}</span>
                  {r.reason ? `: ${r.reason}` : ''}
                </span>
              }
            />
            {r.viewerCanRemove ? (
              <button type="button" className="self-start text-xs font-semibold text-muted hover:text-red-600" onClick={async () => (await remove({ variables: { input: { id: r.id } } }), void refetch())}>
                {t('remove')}
              </button>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  )
}
