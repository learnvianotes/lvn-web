'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { IdCard } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Loading } from '@/components/ui/query-state'
import { cn } from '@/lib/cn'
import {
  ReviewStudentIdVerificationDocument,
  SetStudentIdVerificationEnabledDocument,
  StudentIdCardUrlDocument,
  StudentIdVerificationEnabledDocument,
  StudentIdVerificationQueueDocument,
  ViewerDocument,
  type StudentIdVerificationQueueQuery,
} from '@/graphql/generated/graphql'
import { studentIdErrorMessage, type StudentIdErrorCopy } from './student-id'

type Item = StudentIdVerificationQueueQuery['studentIdVerificationQueue'][number]

/**
 * College ID cards for platform admins (lvn-backend ADR-0099): the on/off switch, the queue,
 * and approve or reject. The card is opened on demand through a short-lived URL that is not cached.
 */
export function StudentIdAdmin() {
  const t = useTranslations('verification.collegeIdAdmin')
  const errors = useTranslations('verification.collegeId')
  const viewer = useQuery(ViewerDocument)
  const isAdmin = viewer.data?.viewer?.globalRole === 'PLATFORM_ADMIN'
  const enabledQ = useQuery(StudentIdVerificationEnabledDocument, { skip: !isAdmin, fetchPolicy: 'cache-and-network' })
  const queue = useQuery(StudentIdVerificationQueueDocument, { variables: { first: 30 }, skip: !isAdmin, fetchPolicy: 'cache-and-network' })
  const [setEnabled, saving] = useMutation(SetStudentIdVerificationEnabledDocument)
  const [switchError, setSwitchError] = useState<string | null>(null)
  const copy = errorCopy(errors)
  const forbidden =
    (viewer.data && !isAdmin) ||
    [enabledQ.error, queue.error].some((error) => CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN'))

  if (!viewer.data && viewer.loading) return <Loading />
  if (forbidden) return <p className="text-muted">{t('notAllowed')}</p>

  const enabled = enabledQ.data?.studentIdVerificationEnabled
  const items = queue.data?.studentIdVerificationQueue ?? []
  const toggle = async () => {
    if (enabled === undefined) return
    setSwitchError(null)
    try {
      const res = await setEnabled({ variables: { input: { enabled: !enabled } } })
      const problem = res.data?.setStudentIdVerificationEnabled.userErrors[0]
      if (problem) setSwitchError(studentIdErrorMessage(problem, copy))
      else await enabledQ.refetch()
    } catch (e) {
      setSwitchError(shown(e, copy))
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight">
          <IdCard className="size-6 text-accent" aria-hidden />
          {t('title')}
        </h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <div className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-surface p-4">
        <div>
          <p id="student-id-switch-label" className="font-semibold">
            {t('switch')}
          </p>
          <p className="text-sm text-muted">{enabled === undefined ? t('loading') : enabled ? t('switchOn') : t('switchOff')}</p>
        </div>
        <button
          type="button"
          role="switch"
          aria-labelledby="student-id-switch-label"
          aria-checked={enabled === true}
          disabled={enabled === undefined || saving.loading}
          onClick={() => void toggle()}
          className={cn('relative h-7 w-12 shrink-0 rounded-full transition-colors disabled:opacity-50', enabled ? 'bg-accent' : 'bg-border')}
        >
          <span className={cn('absolute top-0.5 size-6 rounded-full bg-bg shadow', enabled ? 'left-5' : 'left-0.5')} />
        </button>
      </div>
      {switchError ? <AlertText>{switchError}</AlertText> : null}
      <section aria-labelledby="student-id-queue" className="flex flex-col gap-3">
        <h2 id="student-id-queue" className="text-lg font-semibold">
          {t('queue')}
        </h2>
        {queue.loading && !queue.data ? <Loading /> : null}
        {queue.data && !items.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
        <ul className="flex flex-col gap-3">
          {items.map((item) => (
            <li key={item.id}>
              <Card item={item} onDone={() => void queue.refetch()} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

function Card({ item, onDone }: { item: Item; onDone: () => void }) {
  const t = useTranslations('verification.collegeIdAdmin')
  const errors = useTranslations('verification.collegeId')
  const format = useFormatter()
  const client = useApolloClient()
  const [review, reviewing] = useMutation(ReviewStudentIdVerificationDocument)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const copy = errorCopy(errors)
  const decide = async (approve: boolean) => {
    setError(null)
    try {
      const res = await review({ variables: { input: { requestId: item.id, approve, reason: reason.trim() || null } } })
      const problem = res.data?.reviewStudentIdVerification.userErrors[0]
      if (problem) setError(studentIdErrorMessage(problem, copy))
      else onDone()
    } catch (e) {
      setError(shown(e, copy))
    }
  }
  // The URL lives only for this click. no-cache so Apollo does not keep it, and nothing asks for it earlier.
  const openCard = async () => {
    setError(null)
    const res = await client
      .query({ query: StudentIdCardUrlDocument, variables: { requestId: item.id }, fetchPolicy: 'no-cache' })
      .catch((e: unknown) => {
        setError(shown(e, copy))
        return null
      })
    const url = res?.data?.studentIdCardUrl.url
    if (!url) {
      if (res) setError(t('failed'))
      return
    }
    const opened = window.open(url, '_blank', 'noopener,noreferrer')
    if (!opened) setError(t('popup'))
  }
  return (
    <article aria-label={item.requester.displayName} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Link href={`/u/${item.requester.handle}`} className="font-semibold hover:text-accent">
          {item.requester.displayName}
        </Link>
        <span className="text-sm text-muted">@{item.requester.handle}</span>
        <span className="ml-auto text-xs text-muted">{format.dateTime(new Date(item.createdAt), { dateStyle: 'medium' })}</span>
      </div>
      <button type="button" onClick={() => void openCard()} className="inline-flex w-fit items-center gap-2 text-sm font-medium text-accent hover:underline">
        <IdCard className="size-4" aria-hidden />
        {t('view')}
      </button>
      <label className="flex flex-col gap-1">
        <span className="text-xs font-semibold text-muted">{t('reason')}</span>
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonHint')} className="h-10 rounded-xl border border-border bg-bg px-3 text-sm" />
      </label>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={reviewing.loading} onClick={() => void decide(true)}>
          {t('approve')}
        </Button>
        <Button size="sm" variant="secondary" disabled={reviewing.loading} onClick={() => void decide(false)}>
          {t('reject')}
        </Button>
      </div>
      {error ? <AlertText>{error}</AlertText> : null}
    </article>
  )
}

function AlertText({ children }: { children: string }) {
  return (
    <p role="alert" className="text-sm text-red-600 dark:text-red-400">
      {children}
    </p>
  )
}

function errorCopy(t: (key: 'unavailable' | 'ratePending' | 'rateWeek' | 'rateEither' | 'tooBig' | 'wrongType' | 'failed') => string): StudentIdErrorCopy {
  return {
    unavailable: t('unavailable'),
    pending: t('failed'),
    week: t('failed'),
    eitherLimit: t('failed'),
    tooBig: t('failed'),
    wrongType: t('failed'),
    failed: t('failed'),
  }
}

function shown(e: unknown, copy: StudentIdErrorCopy): string {
  if (CombinedGraphQLErrors.is(e)) {
    const err = e.errors[0]
    const code = typeof err?.extensions?.code === 'string' ? err.extensions.code : null
    return studentIdErrorMessage({ code, message: err?.message }, copy)
  }
  return copy.failed
}
