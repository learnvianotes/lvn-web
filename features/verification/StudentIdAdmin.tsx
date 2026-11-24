'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { IdCard } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useCallback, useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Loading } from '@/components/ui/query-state'
import { ReviewStudentIdVerificationDocument, SetStudentIdVerificationEnabledDocument, StudentIdVerificationEnabledDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { canSeeSection } from '@/features/admin/AdminNav'
import { cn } from '@/lib/cn'
import { loadStudentIdQueue, studentIdCardUrl, type StudentIdReviewItem } from '@/lib/platform-api'
import { IdCardExtracted } from './IdCardExtracted'
import { ProofPreview } from './ProofPreview'
import { confidencePercent, verdictTone } from './proof'
import { studentIdErrorMessage, type StudentIdErrorCopy } from './student-id'

/**
 * College ID cards (lvn-backend ADR-0099): platform admins turn the option on. Only platform admins
 * and verified teachers review the queue. The card is fetched when someone chooses to look, then shown on the page.
 */
export function StudentIdAdmin() {
  const t = useTranslations('verification.collegeIdAdmin')
  const errors = useTranslations('verification.collegeId')
  const viewer = useQuery(ViewerDocument)
  const role = viewer.data?.viewer?.globalRole
  const allowed = canSeeSection(role, 'studentId', { verified: viewer.data?.viewer?.verified })
  const isAdmin = role === 'PLATFORM_ADMIN'
  const enabledQ = useQuery(StudentIdVerificationEnabledDocument, { skip: !isAdmin, fetchPolicy: 'cache-and-network' })
  const [items, setItems] = useState<StudentIdReviewItem[] | null>(null)
  const [queueError, setQueueError] = useState(false)
  const [setEnabled, saving] = useMutation(SetStudentIdVerificationEnabledDocument)
  const [switchError, setSwitchError] = useState<string | null>(null)
  const copy = errorCopy(errors)
  const load = useCallback(async () => {
    try {
      setItems(await loadStudentIdQueue())
      setQueueError(false)
    } catch {
      setItems([])
      setQueueError(true)
    }
  }, [])
  useEffect(() => {
    if (allowed) void load()
  }, [allowed, load])
  const forbidden = (viewer.data && !allowed) || (CombinedGraphQLErrors.is(enabledQ.error) && enabledQ.error.errors.some((e) => e.extensions?.code === 'FORBIDDEN'))

  if (!viewer.data && viewer.loading) return <Loading />
  if (forbidden) return <p className="text-muted">{t('notAllowed')}</p>

  const enabled = enabledQ.data?.studentIdVerificationEnabled
  const toggle = async () => {
    if (enabled === undefined) return
    setSwitchError(null)
    try {
      const res = await setEnabled({ variables: { enabled: !enabled } })
      const payload = res.data?.setStudentIdVerificationEnabled
      const problem = payload?.userErrors[0]
      if (problem || !payload?.ok) setSwitchError(problem ? studentIdErrorMessage(problem, copy) : t('failed'))
      else await enabledQ.refetch()
    } catch (e) {
      setSwitchError(shown(e, copy))
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="flex items-center gap-2 text-2xl font-semibold">
          <IdCard className="size-6 text-accent" aria-hidden />
          {t('title')}
        </h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {isAdmin ? (
        <div className="flex items-center justify-between gap-4 rounded-2xl border border-border bg-surface p-4">
          <div>
            <p id="student-id-switch-label" className="font-semibold">{t('switch')}</p>
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
      ) : null}
      {switchError ? <AlertText>{switchError}</AlertText> : null}
      <section aria-labelledby="student-id-queue" className="flex flex-col gap-3">
        <h2 id="student-id-queue" className="text-lg font-semibold">{t('queue')}</h2>
        {allowed && !items ? <Loading /> : null}
        {items && !items.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
        {queueError ? <AlertText>{t('failed')}</AlertText> : null}
        <ul className="flex flex-col gap-3">
          {(items ?? []).map((item) => (
            <li key={item.id}>
              <Card item={item} onDone={() => void load()} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

function Card({ item, onDone }: { item: StudentIdReviewItem; onDone: () => void }) {
  const t = useTranslations('verification.collegeIdAdmin')
  const reviewT = useTranslations('verification.review')
  const errors = useTranslations('verification.collegeId')
  const format = useFormatter()
  const [review, reviewing] = useMutation(ReviewStudentIdVerificationDocument)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [url, setUrl] = useState<string | null>(null)
  const [mime, setMime] = useState('image/jpeg')
  const copy = errorCopy(errors)
  const decide = async (approve: boolean) => {
    setError(null)
    if (!approve && !reason.trim()) return setError(reviewT('reasonNeeded'))
    try {
      const res = await review({ variables: { input: { requestId: item.id, approve, reason: reason.trim() || null } } })
      const problem = res.data?.reviewStudentIdVerification.userErrors[0]
      if (problem) setError(studentIdErrorMessage(problem, copy))
      else onDone()
    } catch (e) {
      setError(shown(e, copy))
    }
  }
  const openCard = async () => {
    if (url) return
    setError(null)
    try {
      const signed = await studentIdCardUrl(item.id)
      if (!signed) setError(t('failed'))
      else {
        const head = await fetch(signed, { method: 'HEAD' }).catch(() => null)
        setMime(head?.headers.get('content-type')?.split(';')[0] || 'application/octet-stream')
        setUrl(signed)
      }
    } catch (e) {
      setError(shown(e, copy))
    }
  }
  const percent = item.ai ? confidencePercent(item.ai.confidence) : null
  return (
    <article aria-label={item.requester.displayName} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Link href={`/u/${item.requester.handle}`} className="font-semibold hover:text-accent">{item.requester.displayName}</Link>
        <span className="text-sm text-muted">@{item.requester.handle}</span>
        <span className="ml-auto text-xs text-muted">{format.dateTime(new Date(item.createdAt), { dateStyle: 'medium' })}</span>
      </div>
      {item.ai ? (
        <p className="flex flex-wrap items-center gap-2 text-sm">
          <span className={cn('rounded-full px-2 py-0.5 text-xs font-semibold', item.ai && verdictTone(item.ai.verdict) === 'good' ? 'bg-good/10 text-good' : verdictTone(item.ai.verdict) === 'bad' ? 'bg-bad/10 text-bad' : 'bg-warn/10 text-warn')}>{item.ai.verdict}</span>
          {percent != null ? <span className="text-muted">{reviewT('confidence', { percent })}</span> : null}
          {item.ai.reason ? <span>{item.ai.reason}</span> : null}
        </p>
      ) : null}
      {item.ai ? <IdCardExtracted extracted={item.ai.extracted} profileName={item.requester.displayName} profileInstitution={item.requester.institutionName} /> : null}
      {url ? (
        <ProofPreview url={url} mime={mime} name={t('view')} openLabel={reviewT('openInNewTab')} failedLabel={reviewT('pdfFailed')} />
      ) : (
        <button type="button" onClick={() => void openCard()} className="inline-flex w-fit items-center gap-2 text-sm font-medium text-accent hover:underline">
          <IdCard className="size-4" aria-hidden />
          {t('view')}
        </button>
      )}
      <label className="flex flex-col gap-1">
        <span className="text-xs font-semibold text-muted">{t('reason')}</span>
        <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonHint')} className="h-10 rounded-xl border border-border bg-bg px-3 text-sm" />
      </label>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" disabled={reviewing.loading} onClick={() => void decide(true)}>{t('approve')}</Button>
        <Button size="sm" variant="secondary" disabled={reviewing.loading} onClick={() => void decide(false)}>{t('reject')}</Button>
      </div>
      {error ? <AlertText>{error}</AlertText> : null}
    </article>
  )
}

function AlertText({ children }: { children: string }) {
  return <p role="alert" className="text-sm text-bad">{children}</p>
}

function errorCopy(t: (key: 'unavailable' | 'ratePending' | 'rateWeek' | 'rateEither' | 'tooBig' | 'wrongType' | 'failed') => string): StudentIdErrorCopy {
  return { unavailable: t('unavailable'), pending: t('ratePending'), week: t('rateWeek'), eitherLimit: t('rateEither'), tooBig: t('tooBig'), wrongType: t('wrongType'), failed: t('failed') }
}

function shown(e: unknown, copy: StudentIdErrorCopy): string {
  if (CombinedGraphQLErrors.is(e)) {
    const err = e.errors[0]
    const code = typeof err?.extensions?.code === 'string' ? err.extensions.code : null
    return studentIdErrorMessage({ code, message: err?.message }, copy)
  }
  return copy.failed
}
