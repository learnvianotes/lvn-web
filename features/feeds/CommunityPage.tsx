'use client'

import { useQuery } from '@apollo/client/react'
import { BookOpen, CircleQuestionMark, FileText, GitBranch, GraduationCap, Lightbulb, Megaphone, MessageSquare, Users } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import { ago } from '@/features/notes/look'
import { RichDoc } from '@/features/notes/render/RichText'
import { publicNotePath } from '@/features/public-notes/paths'
import { ActivityFeedDocument, FollowingFeedDocument, ForYouFeedDocument, TrendingFeedDocument, type ActivityFeedQuery } from '@/graphql/generated/graphql'
import { PostCard } from './PostCard'
import type { Doc } from '@/lib/contracts/validation'
import { safeLinkHref } from '@/lib/http-url'

type Tab = 'forYou' | 'trending' | 'following' | 'activity'
const TABS: Tab[] = ['forYou', 'trending', 'following', 'activity']
type Item = ActivityFeedQuery['activityFeed']['edges'][number]['node']

/**
 * /community (lvn-backend ADR-0049, ADR-0076): For You (public notes on your topics), Trending (the most reacted to and
 * discussed this week), Following (people you follow) and what happened in your groups and classes.
 */
export function CommunityPage() {
  const t = useTranslations('community')
  const [tab, setTab] = useState<Tab>('forYou')
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold tracking-tight">{t('title')}</h1>
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
      <div role="tablist" aria-label={t('feeds')} className="-mx-1 flex gap-1 overflow-x-auto border-b border-border px-1 [scrollbar-width:none]">
        {TABS.map((k) => (
          <button key={k} role="tab" type="button" aria-selected={k === tab} onClick={() => setTab(k)} className={`-mb-px shrink-0 border-b-2 px-4 py-2 text-sm font-semibold ${k === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}>
            {t(`tab.${k}`)}
          </button>
        ))}
      </div>
      <div role="tabpanel">{tab === 'forYou' ? <ForYou /> : tab === 'trending' ? <Trending onForYou={() => setTab('forYou')} /> : tab === 'activity' ? <Activity /> : <Following />}</div>
    </div>
  )
}

function Activity() {
  const t = useTranslations('community')
  const { data, loading, error, refetch, fetchMore } = useQuery(ActivityFeedDocument, { fetchPolicy: 'cache-and-network' })
  const feed = data?.activityFeed
  if (!feed) return <QueryState loading={loading} error={error} onRetry={refetch} />
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

const ICON = { GROUP_POST: MessageSquare, IDEA: Lightbulb, DOUBT: CircleQuestionMark, CLASS_ANNOUNCEMENT: Megaphone, SHARED_NOTE: FileText, REPOSITORY: GitBranch } as const

/** One thing that happened, in words written here from ids (ADR-0049). */
function ActivityCard({ item }: { item: Item }) {
  const t = useTranslations('community')
  const Icon = ICON[item.kind]
  const place = item.group ? { name: item.group.name, href: `/groups/${item.group.id}` } : item.classroom ? { name: item.classroom.name, href: `/classes/${item.classroom.id}` } : null
  const actor = item.actor?.displayName ?? item.repositoryEvent?.authorLogin ?? t('someone')
  const body = item.post?.body ?? item.announcement?.body
  const href = item.doubt && item.group ? `/groups/${item.group.id}/doubts/${item.doubt.id}` : item.note ? `/notes/${item.note.id}` : (place?.href ?? '#')
  const eventUrl = item.repositoryEvent ? safeLinkHref(item.repositoryEvent.url) : null
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
      {item.repositoryEvent ? (
        eventUrl ? (
          <a href={eventUrl} target="_blank" rel="noopener noreferrer nofollow" className="font-semibold hover:text-accent">
            {item.repositoryEvent.number ? `#${item.repositoryEvent.number} ` : ''}
            {item.repositoryEvent.title}
          </a>
        ) : (
          <span className="font-semibold">
            {item.repositoryEvent.number ? `#${item.repositoryEvent.number} ` : ''}
            {item.repositoryEvent.title}
          </span>
        )
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
  const { data, loading, error, refetch, fetchMore } = useQuery(FollowingFeedDocument, { fetchPolicy: 'cache-and-network' })
  const feed = data?.followingFeed
  if (!feed) return <QueryState loading={loading} error={error} onRetry={refetch} />
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
              <span className="text-lg font-semibold">{node.title || t('untitled')}</span>
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

function Empty({ children }: { children: React.ReactNode }) {
  return <div className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border px-6 py-8 text-center text-sm text-muted">{children}</div>
}

/** For You (ADR-0076): public notes on the person's topics, newest first; with no topics, the ways to have some. */
function ForYou() {
  const t = useTranslations('community')
  const { data, loading, error, fetchMore, refetch } = useQuery(ForYouFeedDocument, { fetchPolicy: 'cache-and-network' })
  const feed = data?.forYouFeed
  if (!feed) return <QueryState loading={loading} error={error} onRetry={refetch} />
  if (!feed.edges.length) {
    return (
      <Empty>
        <p>{feed.basedOn.length ? t('forYou.noneYet') : t('forYou.noTopics')}</p>
        <div className="flex flex-wrap justify-center gap-3">
          <Link href="/profile#interests" className="font-semibold text-accent hover:underline">
            {t('forYou.choose')}
          </Link>
          <Link href="/exams" className="font-semibold text-accent hover:underline">
            {t('forYou.exam')}
          </Link>
        </div>
      </Empty>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {feed.basedOn.length ? (
        <p className="text-xs text-muted">
          {t('forYou.basedOn', { topics: feed.basedOn.slice(0, 5).map((x) => x?.title).filter(Boolean).join(', ') })}{' '}
          <Link href="/profile#interests" className="font-semibold text-accent hover:underline">
            {t('forYou.change')}
          </Link>
        </p>
      ) : null}
      <ul className="grid gap-4 sm:grid-cols-2">
        {feed.edges.map(({ node, topic }) =>
          node ? (
            <li key={node.id}>
              <PostCard note={node} topic={topic} onChanged={() => void refetch()} />
            </li>
          ) : null,
        )}
      </ul>
      {feed.pageInfo.hasNextPage ? (
        <Button variant="secondary" className="self-center" onClick={() => void fetchMore({ variables: { after: feed.pageInfo.endCursor }, updateQuery: (prev, { fetchMoreResult }) => ({ forYouFeed: { ...fetchMoreResult.forYouFeed, edges: [...prev.forYouFeed.edges, ...fetchMoreResult.forYouFeed.edges] } }) })}>
          {t('more')}
        </Button>
      ) : null}
    </div>
  )
}

/** Trending (ADR-0076): the public notes most reacted to and discussed this week. */
function Trending({ onForYou }: { onForYou: () => void }) {
  const t = useTranslations('community')
  const { data, loading, error, fetchMore, refetch } = useQuery(TrendingFeedDocument, { fetchPolicy: 'cache-and-network' })
  const feed = data?.trendingFeed
  if (!feed) return <QueryState loading={loading} error={error} onRetry={refetch} />
  if (!feed.edges.length) {
    return (
      <Empty>
        <p>{t('trending.none')}</p>
        <button type="button" onClick={onForYou} className="font-semibold text-accent hover:underline">
          {t('trending.forYou')}
        </button>
      </Empty>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      <ol className="grid gap-4 sm:grid-cols-2">
        {feed.edges.map(({ node }) =>
          node ? (
            <li key={node.id}>
              <PostCard note={node} onChanged={() => void refetch()} />
            </li>
          ) : null,
        )}
      </ol>
      {feed.pageInfo.hasNextPage ? (
        <Button
          variant="secondary"
          className="self-center"
          onClick={() =>
            void fetchMore({
              variables: { after: feed.pageInfo.endCursor },
              // Pages go by position: a note that moved up since is shown once.
              updateQuery: (prev, { fetchMoreResult }) => {
                const seen = new Set(prev.trendingFeed.edges.map((e) => e.node?.id))
                return { trendingFeed: { ...fetchMoreResult.trendingFeed, edges: [...prev.trendingFeed.edges, ...fetchMoreResult.trendingFeed.edges.filter((e) => !seen.has(e.node?.id))] } }
              },
            })
          }
        >
          {t('more')}
        </Button>
      ) : null}
    </div>
  )
}
