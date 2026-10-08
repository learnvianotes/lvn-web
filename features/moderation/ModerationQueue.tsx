'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { Bot, Check, EyeOff, Flag, MessageSquareWarning, ShieldCheck, Trash2, User } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ModerateContentDocument, ModerationQueueDocument, ViewerDocument, type ModerationActionType, type ModerationQueueQuery } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { ago } from '@/features/notes/look'

type Case = ModerationQueueQuery['moderationQueue']['edges'][number]['node']

const NEEDS_REASON = new Set<ModerationActionType>(['HIDE', 'REMOVE', 'WARN'])

/**
 * The interim platform moderation queue (§15.1, ADR-0037), for PLATFORM_ADMIN accounts until the admin app exists:
 * open cases oldest first, what was reported and why, the author's appeal, and the decisions.
 */
export function ModerationQueue() {
  const t = useTranslations('moderation.queue')
  const viewer = useQuery(ViewerDocument)
  const isAdmin = viewer.data?.viewer?.globalRole === 'PLATFORM_ADMIN'
  const queue = useQuery(ModerationQueueDocument, { skip: !isAdmin, fetchPolicy: 'cache-and-network' })
  const cases = queue.data?.moderationQueue.edges.map((e) => e.node) ?? []

  if (viewer.data && !isAdmin) {
    return (
      <div className="mx-auto max-w-md py-16 text-center">
        <h1 className="text-2xl font-bold">{t('notAllowed')}</h1>
        <p className="mt-2 text-sm text-muted">{t('notAllowedLead')}</p>
      </div>
    )
  }
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight">
          <ShieldCheck className="size-6 text-accent" aria-hidden />
          {t('title')}
        </h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {queue.data && !cases.length ? (
        <div className="flex flex-col items-center gap-2 rounded-3xl border border-dashed border-border px-6 py-12 text-center">
          <Check className="size-8 text-emerald-500" aria-hidden />
          <p className="font-semibold">{t('empty')}</p>
        </div>
      ) : null}
      <ul className="flex flex-col gap-4">
        {cases.map((c) => (
          <li key={`${c.entityType}:${c.entityId}`}>
            <CaseCard item={c} onDone={() => void queue.refetch()} />
          </li>
        ))}
      </ul>
      {queue.data?.moderationQueue.pageInfo.hasNextPage ? (
        <Button
          variant="secondary"
          className="self-center"
          onClick={() =>
            void queue.fetchMore({
              variables: { after: queue.data!.moderationQueue.pageInfo.endCursor },
              updateQuery: (prev, { fetchMoreResult }) => ({ moderationQueue: { ...fetchMoreResult.moderationQueue, edges: [...prev.moderationQueue.edges, ...fetchMoreResult.moderationQueue.edges] } }),
            })
          }
        >
          {t('more')}
        </Button>
      ) : null}
    </div>
  )
}

function CaseCard({ item: c, onDone }: { item: Case; onDone: () => void }) {
  const t = useTranslations('moderation.queue')
  const r = useTranslations('moderation.report.reasons')
  const [moderate, deciding] = useMutation(ModerateContentDocument)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const actions: { action: ModerationActionType; icon: typeof Check; tone: string }[] =
    c.entityType === 'NOTE'
      ? [
          { action: 'APPROVE', icon: Check, tone: '' },
          { action: 'DISMISS', icon: Flag, tone: '' },
          { action: 'WARN', icon: MessageSquareWarning, tone: '' },
          { action: 'HIDE', icon: EyeOff, tone: 'text-amber-700 dark:text-amber-400' },
          { action: 'REMOVE', icon: Trash2, tone: 'text-red-600 dark:text-red-400' },
        ]
      : [
          { action: 'DISMISS', icon: Flag, tone: '' },
          { action: 'WARN', icon: MessageSquareWarning, tone: '' },
        ]

  const decide = async (action: ModerationActionType) => {
    setError(null)
    if (NEEDS_REASON.has(action) && !reason.trim()) return setError(t('reasonNeeded'))
    try {
      const res = await moderate({ variables: { input: { entityType: c.entityType, entityId: c.entityId, action, reason: reason.trim() || null } } })
      const problem = res.data?.moderateContent.userErrors[0]?.message
      if (problem) setError(problem)
      else onDone()
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  return (
    <article className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-4 shadow-sm sm:p-5" aria-label={c.note?.title ?? c.user?.displayName ?? c.entityId}>
      <header className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex min-w-0 flex-col gap-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t(`entity.${c.entityType}`)}</span>
          {c.note ? (
            <>
              <h2 className="text-lg font-bold">{c.note.title || t('untitled')}</h2>
              <p className="text-sm text-muted">{t('by', { name: c.note.owner.displayName, handle: c.note.owner.handle })}</p>
            </>
          ) : (
            <h2 className="flex items-center gap-2 text-lg font-bold">
              <User className="size-4" aria-hidden />
              {c.user?.displayName} <span className="text-sm font-normal text-muted">@{c.user?.handle}</span>
            </h2>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          {c.note ? <span className="rounded-full bg-surface-2 px-2 py-0.5">{t(`state.${c.note.moderation}`)}</span> : null}
          <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{t('opened', { when: ago(c.openedAt) })}</span>
        </div>
      </header>
      {c.note?.excerpt ? <p className="line-clamp-6 whitespace-pre-line rounded-xl bg-surface-2 px-3 py-2 text-sm">{c.note.excerpt}</p> : null}
      {c.reports.length ? (
        <ul className="flex flex-col gap-2" aria-label={t('reports')}>
          {c.reports.map((rep, i) => (
            <li key={i} className="flex items-start gap-2 text-sm">
              {rep.reporter ? <Flag className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden /> : <Bot className="mt-0.5 size-4 shrink-0 text-muted" aria-hidden />}
              <span>
                <strong className="font-semibold">{r(rep.reason)}</strong> · {rep.reporter ? rep.reporter.displayName : t('scorer')}
                {rep.details ? <span className="block text-muted">{rep.details}</span> : null}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
      {c.appeal ? (
        <blockquote className="rounded-xl border-l-4 border-accent bg-accent-soft px-3 py-2 text-sm">
          <span className="block text-xs font-semibold uppercase tracking-wider text-accent">{t('appeal')}</span>
          {c.appeal.message}
        </blockquote>
      ) : null}
      <div className="flex flex-col gap-2">
        <label className="flex flex-col gap-1">
          <span className="text-xs font-semibold text-muted">{t('reason')}</span>
          <input className="h-10 rounded-xl border border-border bg-bg px-3 text-sm focus-visible:border-accent focus-visible:outline-none" value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonPlaceholder')} />
        </label>
        <div className="flex flex-wrap gap-2">
          {actions.map(({ action, icon: Icon, tone }) => (
            <Button key={action} size="sm" variant={action === 'APPROVE' ? 'primary' : 'secondary'} className={cn('gap-1.5', tone)} disabled={deciding.loading} onClick={() => void decide(action)}>
              <Icon className="size-4" aria-hidden />
              {t(`actions.${action}`)}
            </Button>
          ))}
        </div>
        {error ? (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        ) : null}
      </div>
    </article>
  )
}
