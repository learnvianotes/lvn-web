'use client'

import { useQuery } from '@apollo/client/react'
import { BookOpen, CircleHelp, FileText, GraduationCap, Lightbulb, Megaphone, MessageSquare, Users } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ago } from '@/features/notes/look'
import { RichDoc } from '@/features/notes/render/RichText'
import { publicNotePath } from '@/features/public-notes/paths'
import { ActivityFeedDocument, FollowingFeedDocument, type ActivityFeedQuery } from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'

type Tab = 'activity' | 'following'
type Item = ActivityFeedQuery['activityFeed']['edges'][number]['node']

/**
 * /community (lvn-backend ADR-0049): what happened in your groups and classes, and the public notes of people you
 * follow; with the way to your groups and classes.
 */
export function CommunityPage() {
  const t = useTranslations('community')
  const [tab, setTab] = useState<Tab>('activity')
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <nav aria-label={t('places')} className="flex gap-2">
          <Link href="/groups" className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-sm font-semibold hover:border-accent">
            <Users className="size-4" aria-hidden />
            {t('groups')}
          </Link>
          <Link href="/classes" className="inline-flex items-center gap-1.5 rounded-full border border-border px-3 py-1.5 text-sm font-semibold hover:border-accent">
            <GraduationCap className="size-4" aria-hidden />
            {t('classes')}
          </Link>
        </nav>
      </header>
      <div role="tablist" aria-label={t('feeds')} className="flex gap-1 border-b border-border">
        {(['activity', 'following'] as const).map((k) => (
          <button key={k} role="tab" type="button" aria-selected={k === tab} onClick={() => setTab(k)} className={`-mb-px border-b-2 px-4 py-2 text-sm font-semibold ${k === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}>
            {t(`tab.${k}`)}
          </button>
        ))}
      </div>
      <div role="tabpanel">{tab === 'activity' ? <Activity /> : <Following />}</div>
    </div>
  )
}

function Activity() {
  const t = useTranslations('community')
  const { data, fetchMore } = useQuery(ActivityFeedDocument, { fetchPolicy: 'cache-and-network' })
  const feed = data?.activityFeed
  if (!feed) return null
  if (!feed.edges.length) return <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noActivity')}</p>
  return (
    <div className="flex flex-col gap-3">
      <ul className="flex flex-col gap-3">
        {feed.edges.map(({ node }) => (
          <li key={node.key}>
            <ActivityCard item={node} />
          </li>
        ))}
      </ul>
      {feed.pageInfo.hasNextPage ? (
        <Button
          variant="secondary"
          className="self-center"
          onClick={() =>
            void fetchMore({
              variables: { after: feed.pageInfo.endCursor },
              updateQuery: (prev, { fetchMoreResult }) => ({ activityFeed: { ...fetchMoreResult.activityFeed, edges: [...prev.activityFeed.edges, ...fetchMoreResult.activityFeed.edges] } }),
            })
          }
        >
          {t('more')}
        </Button>
      ) : null}
    </div>
  )
}

const ICON = { GROUP_POST: MessageSquare, IDEA: Lightbulb, DOUBT: CircleHelp, CLASS_ANNOUNCEMENT: Megaphone, SHARED_NOTE: FileText } as const

/** One thing that happened, in words written here from ids (ADR-0049). */
function ActivityCard({ item }: { item: Item }) {
  const t = useTranslations('community')
  const Icon = ICON[item.kind]
  const place = item.group ? { name: item.group.name, href: `/groups/${item.group.id}` } : item.classroom ? { name: item.classroom.name, href: `/classes/${item.classroom.id}` } : null
  const actor = item.actor?.displayName ?? t('someone')
  const body = item.post?.body ?? item.announcement?.body
  const href = item.doubt && item.group ? `/groups/${item.group.id}/doubts/${item.doubt.id}` : item.note ? `/notes/${item.note.id}` : (place?.href ?? '#')
  // A shared note the viewer can no longer read resolves to nothing; nothing is shown for it.
  if (item.kind === 'SHARED_NOTE' && !item.note) return null
  return (
    <article className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <Icon className="size-4 text-accent" aria-hidden />
        <span>
          {t(`did.${item.kind}`, { actor })}
          {place ? (
            <>
              {' '}
              <Link href={place.href} className="font-semibold hover:text-accent">
                {place.name}
              </Link>
            </>
          ) : null}
        </span>
        <span className="ml-auto text-xs text-muted">{ago(item.at)}</span>
      </div>
      {item.doubt ? (
        <Link href={href} className="font-semibold hover:text-accent">
          {item.doubt.title}
        </Link>
      ) : null}
      {item.note ? (
        <Link href={href} className="inline-flex w-fit items-center gap-2 font-semibold hover:text-accent">
          <BookOpen className="size-4" aria-hidden />
          {item.note.title || t('untitled')}
        </Link>
      ) : null}
      {body ? (
        <Link href={href} className="line-clamp-4 text-sm hover:opacity-80">
          <RichDoc doc={body as Doc} />
        </Link>
      ) : null}
      {item.post?.discussion.commentCount ? <span className="text-xs text-muted">{t('comments', { count: item.post.discussion.commentCount })}</span> : null}
    </article>
  )
}

function Following() {
  const t = useTranslations('community')
  const { data, fetchMore } = useQuery(FollowingFeedDocument, { fetchPolicy: 'cache-and-network' })
  const feed = data?.followingFeed
  if (!feed) return null
  if (!feed.edges.length) return <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noFollowing')}</p>
  return (
    <div className="flex flex-col gap-3">
      <ul className="flex flex-col gap-3">
        {feed.edges.map(({ node }) => (
          <li key={node.id}>
            <Link href={publicNotePath(node)} className="flex flex-col gap-1 rounded-2xl border border-border bg-surface p-4 hover:border-accent/50">
              <span className="flex flex-wrap items-center gap-2 text-xs text-muted">
                <span className="rounded-full bg-surface-2 px-2 py-0.5 font-semibold">{t(`kind.${node.kind}`)}</span>
                {node.owner.displayName}
                {node.publishedAt ? <span>· {ago(node.publishedAt)}</span> : null}
              </span>
              <span className="text-lg font-bold">{node.title || t('untitled')}</span>
            </Link>
          </li>
        ))}
      </ul>
      {feed.pageInfo.hasNextPage ? (
        <Button
          variant="secondary"
          className="self-center"
          onClick={() =>
            void fetchMore({
              variables: { after: feed.pageInfo.endCursor },
              updateQuery: (prev, { fetchMoreResult }) => ({ followingFeed: { ...fetchMoreResult.followingFeed, edges: [...prev.followingFeed.edges, ...fetchMoreResult.followingFeed.edges] } }),
            })
          }
        >
          {t('more')}
        </Button>
      ) : null}
    </div>
  )
}
