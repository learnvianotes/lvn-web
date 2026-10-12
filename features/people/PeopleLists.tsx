'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  MyPeopleDocument,
  RemoveFollowerDocument,
  UnblockUserDocument,
  UnfollowUserDocument,
  UnrestrictUserDocument,
  type PersonFieldsFragment,
} from '@/graphql/generated/graphql'

type Tab = 'followers' | 'following' | 'blocked' | 'restricted'

/**
 * The viewer's people (lvn-backend ADR-0043): who follows them (restricted minors counted, never named), whom they
 * follow, whom they blocked or restricted — each with the one thing to undo.
 */
export function PeopleLists() {
  const t = useTranslations('people.lists')
  const [tab, setTab] = useState<Tab>('followers')
  const { data, loading, refetch } = useQuery(MyPeopleDocument, { variables: { first: 100 }, fetchPolicy: 'cache-and-network' })
  const [removeFollower] = useMutation(RemoveFollowerDocument)
  const [unfollow] = useMutation(UnfollowUserDocument)
  const [unblock] = useMutation(UnblockUserDocument)
  const [unrestrict] = useMutation(UnrestrictUserDocument)
  const lists: Record<Tab, PersonFieldsFragment[]> = {
    followers: data?.myFollowers.edges.map((e) => e.node) ?? [],
    following: data?.myFollowing.edges.map((e) => e.node) ?? [],
    blocked: data?.myBlocked.map((e) => e.node) ?? [],
    restricted: data?.myRestricted.map((e) => e.node) ?? [],
  }
  const counts: Record<Tab, number> = {
    followers: data?.viewer?.followerCount ?? lists.followers.length,
    following: data?.viewer?.followingCount ?? lists.following.length,
    blocked: lists.blocked.length,
    restricted: lists.restricted.length,
  }
  const undo = async (p: PersonFieldsFragment) => {
    const variables = { input: { userId: p.id } }
    if (tab === 'followers') await removeFollower({ variables })
    if (tab === 'following') await unfollow({ variables })
    if (tab === 'blocked') await unblock({ variables })
    if (tab === 'restricted') await unrestrict({ variables })
    await refetch()
  }
  const hidden = tab === 'followers' ? counts.followers - lists.followers.length : 0
  return (
    <section className="mx-auto flex max-w-2xl flex-col gap-4">
      <header className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        {data?.viewer ? (
          <Link href={`/u/${data.viewer.handle}`} className="text-sm font-medium text-accent hover:underline">
            {t('yourProfile')}
          </Link>
        ) : null}
      </header>
      <div role="tablist" aria-label={t('title')} className="flex gap-1 overflow-x-auto border-b border-border">
        {(['followers', 'following', 'blocked', 'restricted'] as const).map((k) => (
          <button
            key={k}
            role="tab"
            type="button"
            aria-selected={k === tab}
            onClick={() => setTab(k)}
            className={`-mb-px whitespace-nowrap border-b-2 px-4 py-2 text-sm font-semibold ${k === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}
          >
            {t(`tab.${k}`)} <span className="font-normal">{counts[k]}</span>
          </button>
        ))}
      </div>
      <div role="tabpanel" className="flex flex-col gap-2">
        {!lists[tab].length && !loading ? <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-muted">{t(`empty.${tab}`)}</p> : null}
        {lists[tab].length ? (
          <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
            {lists[tab].map((p) => (
              <li key={p.id} className="flex items-center gap-3 px-4 py-3">
                <span aria-hidden className="grid size-9 shrink-0 place-items-center rounded-full bg-accent-soft font-bold text-accent">
                  {p.displayName.slice(0, 1).toUpperCase()}
                </span>
                <Link href={`/u/${p.handle}`} className="flex min-w-0 flex-1 flex-col hover:text-accent">
                  <span className="truncate font-semibold">{p.displayName}</span>
                  <span className="truncate text-xs text-muted">@{p.handle}</span>
                </Link>
                <Button variant="secondary" size="sm" onClick={() => void undo(p)}>
                  {t(`undo.${tab}`)}
                </Button>
              </li>
            ))}
          </ul>
        ) : null}
        {hidden > 0 ? <p className="text-xs text-muted">{t('notNamed', { count: hidden })}</p> : null}
      </div>
    </section>
  )
}
