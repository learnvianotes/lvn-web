'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { FileText } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ReviewVerificationRequestDocument, VerificationDocumentUrlDocument, VerificationRequestsToReviewDocument, type VerificationRequestsToReviewQuery } from '@/graphql/generated/graphql'

type Request = VerificationRequestsToReviewQuery['verificationRequestsToReview'][number]

/**
 * Requests to verify accounts (lvn-backend ADR-0019): a verified teacher sees the students who asked them to vouch;
 * platform admins see proof of enrolment, opened through short-lived, audited links. Approving verifies the account;
 * a refusal needs a reason the student reads. Nothing when there is nothing to answer.
 */
export function ReviewRequests({ admin, title }: { admin?: boolean; title?: boolean }) {
  const t = useTranslations('verification.review')
  const { data, error, refetch } = useQuery(VerificationRequestsToReviewDocument, { fetchPolicy: 'cache-and-network' })
  const requests = data?.verificationRequestsToReview ?? []
  if (CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')) return admin ? <p className="text-muted">{t('notAllowed')}</p> : null
  if (!admin && !requests.length) return null
  return (
    <section aria-labelledby="verify-requests" className="flex flex-col gap-3">
      <h2 id="verify-requests" className={title ? 'text-2xl font-extrabold tracking-tight' : 'text-lg font-semibold'}>
        {admin ? t('adminTitle') : t('teacherTitle')}
      </h2>
      <p className="text-sm text-muted">{admin ? t('adminLead') : t('teacherLead')}</p>
      {data && !requests.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {requests.map((r) => (
          <li key={r.id}>
            <RequestCard request={r} onDone={() => void refetch()} />
          </li>
        ))}
      </ul>
    </section>
  )
}

function RequestCard({ request: r, onDone }: { request: Request; onDone: () => void }) {
  const t = useTranslations('verification.review')
  const format = useFormatter()
  const client = useApolloClient()
  const [review, reviewing] = useMutation(ReviewVerificationRequestDocument)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const decide = async (approve: boolean) => {
    setError(null)
    if (!approve && !reason.trim()) return setError(t('reasonNeeded'))
    try {
      const res = await review({ variables: { input: { requestId: r.id, approve, reason: reason.trim() || null } } })
      const problem = res.data?.reviewVerificationRequest.userErrors[0]?.message
      if (problem) setError(problem)
      else onDone()
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  const open = async (fileId: string) => {
    const res = await client.query({ query: VerificationDocumentUrlDocument, variables: { requestId: r.id, fileId }, fetchPolicy: 'network-only' }).catch(() => null)
    const url = res?.data?.verificationDocumentUrl.url
    if (url) window.open(url, '_blank', 'noopener,noreferrer')
    else setError(t('failed'))
  }
  return (
    <article aria-label={r.requester.displayName} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Link href={`/u/${r.requester.handle}`} className="font-semibold hover:text-accent">
          {r.requester.displayName}
        </Link>
        <span className="text-sm text-muted">@{r.requester.handle}</span>
        {r.purpose === 'TEACHER_ROLE' ? <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">{t('teacherApplication')}</span> : null}
        <span className="ml-auto text-xs text-muted">{format.dateTime(new Date(r.createdAt), { dateStyle: 'medium' })}</span>
      </div>
      {r.purpose === 'TEACHER_ROLE' ? (
        <p className="text-sm">
          {t('teaches', { institution: r.institution ?? '' })}
          {r.subjects ? ` · ${r.subjects}` : ''}
        </p>
      ) : null}
      {r.message ? <blockquote className="rounded-xl bg-surface-2 px-3 py-2 text-sm">{r.message}</blockquote> : null}
      {r.documents.length ? (
        <ul className="flex flex-col gap-1">
          {r.documents.map((d) => (
            <li key={d.fileId}>
              <button type="button" onClick={() => void open(d.fileId)} className="inline-flex items-center gap-2 text-sm font-medium text-accent hover:underline">
                <FileText className="size-4" aria-hidden />
                {d.fileName}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
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
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </article>
  )
}
