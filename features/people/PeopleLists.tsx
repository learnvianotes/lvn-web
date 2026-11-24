'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import {
  MyPeopleDocument,
  RemoveConnectionDocument,
  RemoveFollowerDocument,
  RespondToConnectionRequestDocument,
  UnblockUserDocument,
  UnfollowUserDocument,
  UnrestrictUserDocument,
  WithdrawConnectionRequestDocument,
  type PersonFieldsFragment,
} from '@/graphql/generated/graphql'

type Tab = 'followers' | 'following' | 'connections' | 'requests' | 'blocked' | 'restricted'

/**
 * The viewer's people (lvn-backend ADR-0043): who follows them (restricted minors counted, never named), whom they
 * follow, whom they blocked or restricted — each with the one thing to undo.
 */
export function PeopleLists() {
  const t = useTranslations('people.lists')
  const [tab, setTab] = useState<Tab>('followers')
  const { data, loading, error, refetch } = useQuery(MyPeopleDocument, { variables: { first: 100 }, fetchPolicy: 'cache-and-network' })
  const [removeFollower] = useMutation(RemoveFollowerDocument)
  const [unfollow] = useMutation(UnfollowUserDocument)
  const [unblock] = useMutation(UnblockUserDocument)
  const [unrestrict] = useMutation(UnrestrictUserDocument)
  const [removeConnection] = useMutation(RemoveConnectionDocument)
  const [respond] = useMutation(RespondToConnectionRequestDocument)
  const [withdraw] = useMutation(WithdrawConnectionRequestDocument)
  const requests = data?.myConnectionRequests ?? []
  const lists: Record<Tab, PersonFieldsFragment[]> = {
    followers: data?.myFollowers.edges.map((e) => e.node) ?? [],
    following: data?.myFollowing.edges.map((e) => e.node) ?? [],
    connections: data?.myConnections.map((e) => e.node) ?? [],
    requests: requests.map((r) => r.person),
    blocked: data?.myBlocked.map((e) => e.node) ?? [],
    restricted: data?.myRestricted.map((e) => e.node) ?? [],
  }
  const counts: Record<Tab, number> = {
    followers: data?.viewer?.followerCount ?? lists.followers.length,
    following: data?.viewer?.followingCount ?? lists.following.length,
    connections: lists.connections.length,
    requests: requests.length,
    blocked: lists.blocked.length,
    restricted: lists.restricted.length,
  }
  // Connections are for teachers (ADR-0013); their tabs show for teachers, or when there is something in them.
  const teacher = data?.viewer?.globalRole === 'TEACHER'
  const tabs = (['followers', 'following', 'connections', 'requests', 'blocked', 'restricted'] as const).filter((k) => (k === 'connections' || k === 'requests' ? teacher || counts[k] > 0 : true))
  const requestOf = (p: PersonFieldsFragment) => requests.find((r) => r.person.id === p.id)!
  const undo = async (p: PersonFieldsFragment) => {
    const variables = { input: { userId: p.id } }
    if (tab === 'followers') await removeFollower({ variables })
    if (tab === 'following') await unfollow({ variables })
    if (tab === 'connections') await removeConnection({ variables })
    if (tab === 'requests') {
      const r = requestOf(p)
      if (r.direction === 'OUTGOING') await withdraw({ variables: { input: { requestId: r.id } } })
      else await respond({ variables: { input: { requestId: r.id, accept: false } } })
    }
    if (tab === 'blocked') await unblock({ variables })
    if (tab === 'restricted') await unrestrict({ variables })
    await refetch()
  }
  const hidden = tab === 'followers' ? counts.followers - lists.followers.length : 0
  return (
    <section className="mx-auto flex max-w-2xl flex-col gap-4">
      <header className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        {data?.viewer ? (
          <Link href={`/u/${data.viewer.handle}`} className="text-sm font-medium text-accent hover:underline">
            {t('yourProfile')}
          </Link>
        ) : null}
      </header>
      <div role="tablist" aria-label={t('title')} className="flex gap-1 overflow-x-auto border-b border-border">
        {tabs.map((k) => (
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
        {!data ? <QueryState loading={loading} error={error} onRetry={refetch} /> : null}
        {data && !lists[tab].length ? <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-muted">{t(`empty.${tab}`)}</p> : null}
        {lists[tab].length ? (
          <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
            {lists[tab].map((p) => (
              <li key={p.id} className="flex items-center gap-3 px-4 py-3">
                <span aria-hidden className="grid size-9 shrink-0 place-items-center rounded-full bg-accent-soft font-semibold text-accent">
                  {p.displayName.slice(0, 1).toUpperCase()}
                </span>
                <Link href={`/u/${p.handle}`} className="flex min-w-0 flex-1 flex-col hover:text-accent">
                  <span className="truncate font-semibold">{p.displayName}</span>
                  <span className="truncate text-xs text-muted">@{p.handle}</span>
                </Link>
                {tab === 'requests' && requestOf(p).direction === 'INCOMING' ? (
                  <Button size="sm" onClick={() => void respond({ variables: { input: { requestId: requestOf(p).id, accept: true } } }).then(() => refetch())}>
                    {t('accept')}
                  </Button>
                ) : null}
                <Button variant="secondary" size="sm" onClick={() => void undo(p)}>
                  {tab === 'requests' ? t(requestOf(p).direction === 'OUTGOING' ? 'withdraw' : 'decline') : t(`undo.${tab}`)}
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
