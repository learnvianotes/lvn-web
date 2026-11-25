'use client'

import { useQuery } from '@apollo/client/react'
import { FileText } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useCallback, useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { ViewerDocument } from '@/graphql/generated/graphql'
import { canSeeSection } from '@/features/admin/AdminNav'
import { cn } from '@/lib/cn'
import { PlatformError, loadVerificationQueue, reviewVerification, verificationDocumentUrl, type AiVerdictView, type ReviewRequestView } from '@/lib/platform-api'
import { IdCardExtracted } from './IdCardExtracted'
import { ProofPreview } from './ProofPreview'
import { confidencePercent, verdictTone } from './proof'

/**
 * Requests to verify accounts. Platform admins and verified teachers review them.
 * A teacher sees students of their institution (the API scopes the list). Approving verifies the account;
 * declining needs a reason the student reads. Teacher applications stay with platform admins.
 */
export function ReviewRequests({ title }: { title?: boolean }) {
  const t = useTranslations('verification.review')
  const viewerQuery = useQuery(ViewerDocument)
  const viewer = viewerQuery.data?.viewer
  const allowed = !!viewer && canSeeSection(viewer.globalRole, 'verification', { verified: viewer.verified })
  const teacher = viewer?.globalRole === 'TEACHER'
  const [requests, setRequests] = useState<ReviewRequestView[] | null>(null)
  const [forbidden, setForbidden] = useState(false)
  const [failed, setFailed] = useState(false)
  const load = useCallback(async () => {
    try {
      setRequests(await loadVerificationQueue())
      setForbidden(false)
      setFailed(false)
    } catch (error) {
      setRequests([])
      setForbidden(error instanceof PlatformError && error.forbidden)
      setFailed(!(error instanceof PlatformError && error.forbidden))
    }
  }, [])
  useEffect(() => {
    if (!allowed) return
    void load()
  }, [allowed, load])
  if (!viewer && viewerQuery.loading) return <p className="text-muted">{t('loading')}</p>
  if (!allowed || forbidden) return <p className="text-muted">{t('notAllowed')}</p>
  if (!requests) return <p className="text-muted">{t('loading')}</p>
  return (
    <section aria-labelledby="verify-requests" className="flex flex-col gap-3">
      {title ? (
        <h1 id="verify-requests" className="text-2xl font-semibold">
          {teacher ? t('teacherTitle') : t('adminTitle')}
        </h1>
      ) : (
        <h2 id="verify-requests" className="text-lg font-semibold">
          {teacher ? t('teacherTitle') : t('adminTitle')}
        </h2>
      )}
      <p className="text-sm text-muted">{teacher ? t('teacherLead') : t('adminLead')}</p>
      {failed ? <p role="alert" className="text-sm text-bad">{t('failed')}</p> : null}
      {!failed && !requests.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {requests.map((request) => (
          <li key={request.id}>
            <RequestCard request={request} canDecideRole={viewer?.globalRole === 'PLATFORM_ADMIN'} onDone={() => void load()} />
          </li>
        ))}
      </ul>
    </section>
  )
}

function RequestCard({ request: r, canDecideRole, onDone }: { request: ReviewRequestView; canDecideRole: boolean; onDone: () => void }) {
  const t = useTranslations('verification.review')
  const format = useFormatter()
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const locked = r.purpose === 'TEACHER_ROLE' && !canDecideRole
  const decide = async (approve: boolean) => {
    setError(null)
    if (!approve && !reason.trim()) return setError(t('reasonNeeded'))
    setBusy(true)
    try {
      const problem = await reviewVerification({ requestId: r.id, approve, reason: reason.trim() || null })
      if (problem) setError(problem)
      else onDone()
    } catch (e) {
      setError(e instanceof PlatformError ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  return (
    <article aria-label={r.requester.displayName} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Link href={`/u/${r.requester.handle}`} className="font-semibold hover:text-accent">
          {r.requester.displayName}
        </Link>
        <span className="text-sm text-muted">@{r.requester.handle}</span>
        {r.purpose === 'TEACHER_ROLE' ? <span className="rounded-[4px] bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">{t('teacherApplication')}</span> : null}
        <span className="ml-auto text-xs text-muted">{format.dateTime(new Date(r.createdAt), { dateStyle: 'medium' })}</span>
      </div>
      {r.purpose === 'TEACHER_ROLE' ? (
        <p className="text-sm">
          {t('teaches', { institution: r.institution ?? '' })}
          {r.subjects ? ` · ${r.subjects}` : ''}
        </p>
      ) : null}
      {r.requester.institutionName || r.requester.department ? (
        <p className="text-sm text-muted">{[r.requester.institutionName, r.requester.department].filter(Boolean).join(' · ')}</p>
      ) : null}
      {r.message ? <blockquote className="rounded-xl bg-surface-2 px-3 py-2 text-sm">{r.message}</blockquote> : null}
      {r.ai ? <AiVerdict ai={r.ai} profileName={r.requester.displayName} profileInstitution={r.requester.institutionName} /> : null}
      {r.documents.length ? (
        <ul className="flex flex-col gap-3">
          {r.documents.map((document) => (
            <li key={document.fileId}>
              <DocumentProof requestId={r.id} fileId={document.fileId} name={document.fileName} mime={document.mimeType} onError={setError} />
            </li>
          ))}
        </ul>
      ) : null}
      {locked ? <p className="text-sm text-muted">{t('adminOnly')}</p> : null}
      {locked ? null : (
        <>
          <label className="flex flex-col gap-1">
            <span className="text-xs font-semibold text-muted">{t('reason')}</span>
            <input value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonHint')} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3 text-sm" />
          </label>
          <div className="flex flex-wrap gap-2">
            <Button size="sm" className="h-11" disabled={busy} onClick={() => void decide(true)}>
              {t('approve')}
            </Button>
            <Button size="sm" variant="secondary" className="h-11" disabled={busy} onClick={() => void decide(false)}>
              {t('reject')}
            </Button>
          </div>
        </>
      )}
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </article>
  )
}

function DocumentProof({ requestId, fileId, name, mime, onError }: { requestId: string; fileId: string; name: string; mime: string; onError: (message: string) => void }) {
  const t = useTranslations('verification.review')
  const [url, setUrl] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const open = async () => {
    if (url) return
    setBusy(true)
    try {
      const signed = await verificationDocumentUrl(requestId, fileId)
      if (!signed) onError(t('failed'))
      else setUrl(signed)
    } catch {
      onError(t('failed'))
    } finally {
      setBusy(false)
    }
  }
  if (!url) {
    return (
      <button type="button" onClick={() => void open()} disabled={busy} className="inline-flex min-h-11 max-w-full items-center gap-2 break-all text-left text-sm font-medium text-accent hover:underline">
        <FileText className="size-4 shrink-0" aria-hidden />
        {name}
      </button>
    )
  }
  return <ProofPreview url={url} mime={mime} name={name} openLabel={t('openInNewTab')} failedLabel={t('pdfFailed')} />
}

const TONE = {
  good: 'bg-good/10 text-good',
  bad: 'bg-bad/10 text-bad',
  pending: 'bg-warn/10 text-warn',
} as const

function AiVerdict({ ai, profileName, profileInstitution }: { ai: AiVerdictView; profileName: string; profileInstitution: string | null }) {
  const t = useTranslations('verification.review')
  const format = useFormatter()
  const percent = confidencePercent(ai.confidence)
  const checked = ai.checkedAt ? format.dateTime(new Date(ai.checkedAt), { dateStyle: 'medium', timeStyle: 'short' }) : null
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border bg-bg p-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className={cn('rounded-full px-2 py-0.5 text-xs font-semibold', TONE[verdictTone(ai.verdict)])}>{ai.verdict}</span>
        {percent != null ? <span className="text-sm text-muted">{t('confidence', { percent })}</span> : null}
        {checked ? <span className="text-sm text-muted">{t('checkedAt', { when: checked })}</span> : null}
      </div>
      {ai.reason ? <p className="text-sm">{ai.reason}</p> : null}
      <IdCardExtracted extracted={ai.extracted} profileName={profileName} profileInstitution={profileInstitution} />
    </div>
  )
}
