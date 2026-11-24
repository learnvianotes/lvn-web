'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { Ban, MessageSquareWarning, ShieldAlert } from 'lucide-react'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { AppealModerationDocument, MyStandingDocument, RemovedGroupDocument, type ReportEntityType } from '@/graphql/generated/graphql'

/** The one appeal, inline: a suspended account's (entityType USER) or a removed group's owner's (GROUP). */
function AppealForm({ entityType, entityId, onDone }: { entityType: ReportEntityType; entityId: string; onDone: () => void }) {
  const t = useTranslations('moderation.standing')
  const [appeal, appealing] = useMutation(AppealModerationDocument)
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const submit = async () => {
    setError(null)
    try {
      const res = await appeal({ variables: { input: { entityType, entityId, message } } })
      const problem = res.data?.appealModeration.userErrors[0]?.message
      if (problem) setError(problem)
      else onDone()
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  if (!open)
    return (
      <Button size="sm" variant="secondary" className="w-fit" onClick={() => setOpen(true)}>
        {t('appeal')}
      </Button>
    )
  return (
    <form
      className="flex flex-col gap-2"
      onSubmit={(e) => {
        e.preventDefault()
        void submit()
      }}
    >
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium">{t('appealMessage')}</span>
        <textarea required maxLength={2000} value={message} onChange={(e) => setMessage(e.target.value)} className="min-h-24 rounded-xl border border-border bg-surface px-3 py-2 text-sm text-fg focus-visible:border-accent focus-visible:outline-none" />
      </label>
      <p className="text-xs opacity-80">{t('appealOnce')}</p>
      {error ? (
        <p role="alert" className="text-sm text-red-700 dark:text-red-300">
          {error}
        </p>
      ) : null}
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={!message.trim() || appealing.loading}>
          {t('sendAppeal')}
        </Button>
        <Button type="button" size="sm" variant="ghost" onClick={() => setOpen(false)}>
          {t('cancel')}
        </Button>
      </div>
    </form>
  )
}

/**
 * The account's standing on its own page (lvn-backend ADR-0053): a suspension while it lasts, until when and why, what
 * it still allows, and the one appeal; the moderators' warnings of the last 90 days. Nothing when there is nothing.
 */
export function AccountStanding({ userId }: { userId: string }) {
  const t = useTranslations('moderation.standing')
  const format = useFormatter()
  const { data, refetch } = useQuery(MyStandingDocument, { fetchPolicy: 'cache-and-network' })
  const s = data?.myStanding
  if (!s || (!s.suspendedUntil && !s.warnings.length)) return null
  return (
    <section aria-labelledby="standing" className="flex flex-col gap-3">
      <h2 id="standing" className="sr-only">
        {t('title')}
      </h2>
      {s.suspendedUntil ? (
        <div role="alert" className="flex items-start gap-3 rounded-2xl border border-red-500/40 bg-red-50 px-4 py-3 text-sm text-red-950 dark:bg-red-950/30 dark:text-red-100">
          <Ban className="mt-0.5 size-5 shrink-0" aria-hidden />
          <div className="flex min-w-0 flex-1 flex-col gap-2">
            <p className="font-semibold">{t('suspended', { until: format.dateTime(new Date(s.suspendedUntil), { dateStyle: 'long', timeStyle: 'short' }) })}</p>
            {s.suspensionReason ? <p>{s.suspensionReason}</p> : null}
            <p className="opacity-80">{t('suspendedLead')}</p>
            {s.canAppeal ? <AppealForm entityType="USER" entityId={userId} onDone={() => void refetch()} /> : <p className="font-medium">{t('appealed')}</p>}
          </div>
        </div>
      ) : null}
      {s.warnings.length ? (
        <div className="flex items-start gap-3 rounded-2xl border border-amber-500/40 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">
          <MessageSquareWarning className="mt-0.5 size-5 shrink-0" aria-hidden />
          <div className="flex min-w-0 flex-1 flex-col gap-2">
            <p className="font-semibold">{t('warnings', { count: s.warnings.length })}</p>
            <ul className="flex flex-col gap-1.5">
              {s.warnings.map((w, i) => (
                <li key={i}>
                  {w.reason} <span className="opacity-70">· {format.dateTime(new Date(w.at), { dateStyle: 'medium' })}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
    </section>
  )
}

/** Where a group platform moderators removed used to be, for its owner (ADR-0053): why, and the one appeal. */
export function RemovedGroupNotice({ id, fallback }: { id: string; fallback: React.ReactNode }) {
  const t = useTranslations('moderation.standing')
  const { data, loading, refetch } = useQuery(RemovedGroupDocument, { variables: { id }, fetchPolicy: 'cache-and-network' })
  const g = data?.removedGroup
  if (!g) return loading ? null : <>{fallback}</>
  return (
    <div role="alert" className="mx-auto flex max-w-2xl items-start gap-3 rounded-2xl border border-red-500/40 bg-red-50 px-4 py-4 text-sm text-red-950 dark:bg-red-950/30 dark:text-red-100">
      <ShieldAlert className="mt-0.5 size-5 shrink-0" aria-hidden />
      <div className="flex min-w-0 flex-1 flex-col gap-2">
        <h1 className="text-lg font-semibold">{t('groupRemoved', { name: g.name })}</h1>
        <p>{g.reason}</p>
        <p className="opacity-80">{t('groupRemovedLead')}</p>
        {g.canAppeal ? <AppealForm entityType="GROUP" entityId={g.id} onDone={() => void refetch()} /> : <p className="font-medium">{t('appealed')}</p>}
      </div>
    </div>
  )
}
