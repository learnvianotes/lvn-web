'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { Ban, Bot, Check, EyeOff, Flag, MessageSquareWarning, ShieldCheck, Trash, User, Users, VolumeX } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ModerateContentDocument, ModerationQueueDocument, MuteGroupMemberDocument, ViewerDocument, type ModerationActionType, type ModerationQueueQuery, type ModerationScope } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { ago } from '@/features/notes/look'

type Case = ModerationQueueQuery['moderationQueue']['edges'][number]['node']

const NEEDS_REASON = new Set<ModerationActionType>(['HIDE', 'REMOVE', 'WARN', 'SUSPEND'])
/** How long a suspension lasts, in days (ADR-0053: 1 to 365). */
const SUSPEND_DAYS = [1, 3, 7, 14, 30, 90, 365] as const

/**
 * A moderation queue (§15.1, ADR-0037, ADR-0051): open cases oldest first, what was reported and why, the author's
 * appeal, and the decisions. Without `scope` it is the platform's, for PLATFORM_ADMIN accounts until the admin app
 * exists; with one, a group's (its moderators and mentor, who can also mute an author for a day) or a class's (its
 * staff), shown as a tab of that place.
 */
export function ModerationQueue({ scope, groupId }: { scope?: { scope: ModerationScope; id: string }; groupId?: string }) {
  const t = useTranslations('moderation.queue')
  const viewer = useQuery(ViewerDocument, { skip: !!scope })
  const isAdmin = viewer.data?.viewer?.globalRole === 'PLATFORM_ADMIN'
  const queue = useQuery(ModerationQueueDocument, { variables: { scope }, skip: !scope && !isAdmin, fetchPolicy: 'cache-and-network' })
  const cases = queue.data?.moderationQueue.edges.map((e) => e.node) ?? []
  const forbidden = (!scope && viewer.data && !isAdmin) || (CombinedGraphQLErrors.is(queue.error) && queue.error.errors.some((e) => e.extensions?.code === 'FORBIDDEN'))

  if (forbidden) {
    return (
      <div className="mx-auto max-w-md py-16 text-center">
        <h1 className="text-2xl font-bold">{t('notAllowed')}</h1>
        <p className="mt-2 text-sm text-muted">{scope ? t('notAllowedScoped') : t('notAllowedLead')}</p>
      </div>
    )
  }
  return (
    <div className="flex flex-col gap-6">
      {scope ? (
        <p className="text-sm text-muted">{t(`leadScoped.${scope.scope}`)}</p>
      ) : (
        <header className="flex flex-col gap-1">
          <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight">
            <ShieldCheck className="size-6 text-accent" aria-hidden />
            {t('title')}
          </h1>
          <p className="text-sm text-muted">{t('lead')}</p>
        </header>
      )}
      {queue.data && !cases.length ? (
        <div className="flex flex-col items-center gap-2 rounded-3xl border border-dashed border-border px-6 py-12 text-center">
          <Check className="size-8 text-emerald-500" aria-hidden />
          <p className="font-semibold">{t('empty')}</p>
        </div>
      ) : null}
      <ul className="flex flex-col gap-4">
        {cases.map((c) => (
          <li key={`${c.entityType}:${c.entityId}`}>
            <CaseCard item={c} groupId={groupId} platform={!scope} onDone={() => void queue.refetch()} />
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

type Choice = { action: ModerationActionType; label: string; icon: typeof Check; tone: string }

/** What a moderator can do with a case: notes and content can be put back, hidden or removed; accounts and groups less. */
function choicesFor(c: Case): Choice[] {
  const keep = !!c.appeal && (c.content?.moderation === 'HIDDEN' || c.content?.moderation === 'REMOVED' || c.note?.moderation === 'HIDDEN' || c.note?.moderation === 'REMOVED')
  const dismiss: Choice = { action: 'DISMISS', label: keep ? 'KEEP' : 'DISMISS', icon: Flag, tone: '' }
  const warn: Choice = { action: 'WARN', label: 'WARN', icon: MessageSquareWarning, tone: '' }
  const hide: Choice = { action: 'HIDE', label: 'HIDE', icon: EyeOff, tone: 'text-amber-700 dark:text-amber-400' }
  const remove: Choice = { action: 'REMOVE', label: 'REMOVE', icon: Trash, tone: 'text-red-600 dark:text-red-400' }
  const approve: Choice = { action: 'APPROVE', label: keep ? 'RESTORE' : 'APPROVE', icon: Check, tone: '' }
  // A new resource is approved or rejected (ADR-0074); people's reports on one in the catalogue are dismissed, or it is removed.
  if (c.entityType === 'RESOURCE') return c.reports.some((x) => x.reporter) ? [dismiss, remove] : [approve, { ...remove, label: 'REJECT' }]
  // Accounts are warned or suspended; a suspension is lifted or kept (ADR-0053).
  if (c.entityType === 'USER') return c.suspendedUntil ? [{ action: 'APPROVE', label: 'LIFT', icon: Check, tone: '' }, { ...dismiss, label: c.appeal ? 'KEEP' : 'DISMISS' }, warn] : [dismiss, warn, { action: 'SUSPEND', label: 'SUSPEND', icon: Ban, tone: 'text-red-600 dark:text-red-400' }]
  // A removed group is put back or stays removed.
  if (c.entityType === 'GROUP') return c.removedGroup ? [{ action: 'APPROVE', label: 'RESTORE', icon: Check, tone: '' }, { ...dismiss, label: 'KEEP' }] : [dismiss, warn, remove]
  // Approving content that is up changes nothing a dismissal doesn't.
  if (c.content && c.content.moderation === 'OK') return [dismiss, warn, hide, remove]
  return [approve, dismiss, warn, hide, remove]
}

function CaseCard({ item: c, groupId, platform, onDone }: { item: Case; groupId?: string; platform: boolean; onDone: () => void }) {
  const t = useTranslations('moderation.queue')
  const r = useTranslations('moderation.report.reasons')
  const [moderate, deciding] = useMutation(ModerateContentDocument)
  const [mute, muting] = useMutation(MuteGroupMemberDocument)
  const [reason, setReason] = useState('')
  const [days, setDays] = useState<number>(7)
  const [error, setError] = useState<string | null>(null)
  const [muted, setMuted] = useState(false)
  const format = useFormatter()
  const actions = choicesFor(c)
  const author = c.content?.author ?? c.note?.owner ?? null
  const state = c.content?.moderation ?? c.note?.moderation ?? null

  const decide = async (action: ModerationActionType) => {
    setError(null)
    if (NEEDS_REASON.has(action) && !reason.trim()) return setError(t('reasonNeeded'))
    try {
      const res = await moderate({ variables: { input: { entityType: c.entityType, entityId: c.entityId, action, reason: reason.trim() || null, ...(action === 'SUSPEND' ? { suspendDays: days } : {}) } } })
      const problem = res.data?.moderateContent.userErrors[0]?.message
      if (problem) setError(problem)
      else onDone()
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  const muteAuthor = async () => {
    if (!groupId || !c.content) return
    setError(null)
    try {
      const res = await mute({ variables: { groupId, userId: c.content.author.id, until: new Date(Date.now() + 86_400_000).toISOString() } })
      const problem = res.data?.muteGroupMember.userErrors[0]?.message
      if (problem) setError(problem)
      else setMuted(true)
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  const title = c.note ? c.note.title || t('untitled') : c.resource ? c.resource.title : c.group ? c.group.name : c.removedGroup ? c.removedGroup.name : c.user ? c.user.displayName : t(`entity.${c.entityType}`)
  return (
    <article className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-4 shadow-sm sm:p-5" aria-label={title}>
      <header className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex min-w-0 flex-col gap-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-muted">{t(`entity.${c.entityType}`)}</span>
          {c.note ? (
            <h2 className="text-lg font-bold">{title}</h2>
          ) : c.group ? (
            <h2 className="flex items-center gap-2 text-lg font-bold">
              <Users className="size-4" aria-hidden />
              <Link href={`/groups/${c.group.id}`} className="hover:text-accent">
                {c.group.name}
              </Link>
            </h2>
          ) : c.removedGroup ? (
            <h2 className="flex items-center gap-2 text-lg font-bold">
              <Users className="size-4" aria-hidden />
              {c.removedGroup.name}
            </h2>
          ) : c.user ? (
            <h2 className="flex items-center gap-2 text-lg font-bold">
              <User className="size-4" aria-hidden />
              {c.user.displayName} <span className="text-sm font-normal text-muted">@{c.user.handle}</span>
            </h2>
          ) : null}
          {c.resource ? (
            <h2 className="text-lg font-bold">
              <Link href={`/resources/${c.resource.id}`} className="hover:text-accent">
                {c.resource.title}
              </Link>
            </h2>
          ) : null}
          {author ? <p className="text-sm text-muted">{t('by', { name: author.displayName, handle: author.handle })}</p> : null}
          {c.resource ? <p className="text-sm text-muted">{t('by', { name: c.resource.submittedBy.displayName, handle: c.resource.submittedBy.handle })}</p> : null}
        </div>
        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          {platform && c.scope !== 'PLATFORM' ? <span className="rounded-full bg-accent-soft px-2 py-0.5 font-semibold text-accent">{t(`scope.${c.scope}`)}</span> : null}
          {state ? <span className="rounded-full bg-surface-2 px-2 py-0.5">{t(`state.${state}`)}</span> : null}
          {c.resource ? <span className="rounded-full bg-surface-2 px-2 py-0.5">{t(`resourceState.${c.resource.status}`)}</span> : null}
          {c.suspendedUntil ? <span className="rounded-full bg-red-100 px-2 py-0.5 font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-300">{t('suspendedUntil', { until: format.dateTime(new Date(c.suspendedUntil), { dateStyle: 'medium' }) })}</span> : null}
          {c.removedGroup ? <span className="rounded-full bg-red-100 px-2 py-0.5 font-semibold text-red-700 dark:bg-red-950/40 dark:text-red-300">{t(`state.REMOVED`)}</span> : null}
          <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{t('opened', { when: ago(c.openedAt) })}</span>
        </div>
      </header>
      {c.note?.excerpt ? <p className="line-clamp-6 whitespace-pre-line rounded-xl bg-surface-2 px-3 py-2 text-sm">{c.note.excerpt}</p> : null}
      {c.removedGroup ? <p className="rounded-xl bg-surface-2 px-3 py-2 text-sm">{t('removedReason', { reason: c.removedGroup.reason })}</p> : null}
      {c.resource ? <ResourceCase resource={c.resource} /> : null}
      {c.content ? (
        <div className="flex flex-col gap-1 rounded-xl bg-surface-2 px-3 py-2 text-sm">
          <p className="line-clamp-6 whitespace-pre-line">{c.content.deleted ? <em className="text-muted">{t('deleted')}</em> : c.content.excerpt}</p>
          <Link href={c.content.path} className="self-start text-xs font-semibold text-accent hover:underline">
            {t('open')}
          </Link>
        </div>
      ) : null}
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
          <input className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3 text-sm focus-visible:border-accent focus-visible:outline-none" value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonPlaceholder')} />
        </label>
        {actions.some((a) => a.action === 'SUSPEND') ? (
          <label className="flex items-center gap-2 text-xs font-semibold text-muted">
            {t('suspendFor')}
            <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="h-9 rounded-lg border border-border bg-bg px-2 text-sm font-normal text-fg">
              {SUSPEND_DAYS.map((d) => (
                <option key={d} value={d}>
                  {t('days', { count: d })}
                </option>
              ))}
            </select>
          </label>
        ) : null}
        <div className="flex flex-wrap gap-2">
          {actions.map(({ action, label, icon: Icon, tone }) => (
            <Button key={action} size="sm" variant={action === 'APPROVE' ? 'primary' : 'secondary'} className={cn('h-11 gap-1.5', tone)} disabled={deciding.loading} onClick={() => void decide(action)}>
              <Icon className="size-4" aria-hidden />
              {t(`actions.${label}`)}
            </Button>
          ))}
          {groupId && c.content ? (
            <Button size="sm" variant="ghost" className="gap-1.5" disabled={muted || muting.loading} onClick={() => void muteAuthor()}>
              <VolumeX className="size-4" aria-hidden />
              {muted ? t('muted') : t('muteDay')}
            </Button>
          ) : null}
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

/** What moderators judge a resource by (ADR-0074): what it is, where its link goes, and what the person said about it. */
function ResourceCase({ resource: r }: { resource: NonNullable<Case['resource']> }) {
  const t = useTranslations('moderation.queue')
  const types = useTranslations('resources.type')
  return (
    <div className="flex flex-col gap-2 rounded-xl bg-surface-2 px-3 py-2 text-sm">
      <p className="text-muted">{t('resourceLead')}</p>
      <p>
        <strong className="font-semibold">{types(r.type)}</strong>
        {r.author ? ` · ${r.author}` : ''}
        {r.isbn ? ` · ISBN ${r.isbn}` : ''}
      </p>
      <a href={r.url} rel="ugc nofollow noopener" target="_blank" className="break-all font-semibold text-accent hover:underline">
        {r.url}
      </a>
      {r.description ? <p className="line-clamp-6 whitespace-pre-line">{r.description}</p> : null}
      {r.topics.length ? <p className="text-xs text-muted">{r.topics.flatMap((x) => (x ? [x.title] : [])).join(' · ')}</p> : null}
    </div>
  )
}
