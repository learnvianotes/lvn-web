'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { IdCard, X } from 'lucide-react'
import { useFormatter, useTranslations } from 'next-intl'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { putToStorage, UploadError } from '@/features/notes/media'
import {
  CreateStudentIdUploadIntentDocument,
  MyStudentIdVerificationDocument,
  StudentIdVerificationEnabledDocument,
  SubmitStudentIdVerificationDocument,
  WithdrawStudentIdVerificationDocument,
} from '@/graphql/generated/graphql'
import { STUDENT_ID_TYPES, studentIdErrorMessage, studentIdFileProblem, studentIdMime, type StudentIdErrorCopy } from './student-id'

/**
 * Ask an admin to verify the account with a college ID card (lvn-backend ADR-0099).
 * Hidden entirely while studentIdVerificationEnabled is false, and for a restricted minor.
 * The card is PUT, then submitStudentIdVerification checks it. completeUpload is not called.
 */
export function CollegeIdOption({ restrictedMinor }: { restrictedMinor: boolean }) {
  const t = useTranslations('verification.collegeId')
  const format = useFormatter()
  const client = useApolloClient()
  const input = useRef<HTMLInputElement>(null)
  const flag = useQuery(StudentIdVerificationEnabledDocument, { skip: restrictedMinor, fetchPolicy: 'cache-and-network' })
  const enabled = flag.data?.studentIdVerificationEnabled === true
  const mine = useQuery(MyStudentIdVerificationDocument, { skip: !enabled, fetchPolicy: 'cache-and-network' })
  const [withdraw] = useMutation(WithdrawStudentIdVerificationDocument)
  const [submit] = useMutation(SubmitStudentIdVerificationDocument)
  const [open, setOpen] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const copy = errorCopy(t)
  if (restrictedMinor || !enabled) return null

  const request = mine.data?.myStudentIdVerification ?? null
  const pending = request?.status === 'PENDING' ? request : null
  const send = async () => {
    if (!file) return
    const local = studentIdFileProblem(file)
    if (local) {
      setError(local === 'type' ? t('wrongType') : local === 'empty' ? t('empty') : t('tooBig'))
      return
    }
    setError(null)
    setBusy(true)
    try {
      const created = await client.mutate({
        mutation: CreateStudentIdUploadIntentDocument,
        variables: { input: { fileName: file.name || 'college-id', mimeType: studentIdMime(file), sizeBytes: file.size } },
      })
      const payload = created.data?.createStudentIdUploadIntent
      const upload = payload?.upload
      if (!upload) throw new UploadError(studentIdErrorMessage(payload?.userErrors[0] ?? {}, copy))
      await putToStorage(upload, file, () => undefined)
      const sent = await submit({ variables: { input: { fileId: upload.fileId } } })
      const problem = sent.data?.submitStudentIdVerification.userErrors[0]
      if (problem) throw new UploadError(studentIdErrorMessage(problem, copy))
      setFile(null)
      setOpen(false)
      await mine.refetch()
    } catch (e) {
      setError(shown(e, copy))
    } finally {
      setBusy(false)
    }
  }

  if (pending) {
    return (
      <div className="flex flex-col gap-2 rounded-xl border border-accent/30 bg-accent-soft/40 p-3 text-sm">
        <p className="font-semibold">{t('waiting')}</p>
        <p className="text-muted">{t('sent', { when: format.dateTime(new Date(pending.createdAt), { dateStyle: 'medium' }) })}</p>
        <Button
          size="sm"
          variant="secondary"
          className="w-fit"
          onClick={async () => {
            setError(null)
            try {
              const res = await withdraw({ variables: { requestId: pending.id } })
              const problem = res.data?.withdrawStudentIdVerification.userErrors[0]
              if (problem) setError(studentIdErrorMessage(problem, copy))
              else await mine.refetch()
            } catch (e) {
              setError(shown(e, copy))
            }
          }}
        >
          {t('withdraw')}
        </Button>
        {error ? <Problem>{error}</Problem> : null}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-2">
      {request?.status === 'REJECTED' ? (
        <p role="status" className="rounded-xl border border-bad/30 bg-bad/10 p-3 text-sm text-bad">
          {request.reason ? t('rejected', { reason: request.reason }) : t('rejectedNoReason')}
        </p>
      ) : null}
      {request?.status === 'APPROVED' ? (
        <p role="status" className="rounded-xl border border-good/30 bg-good/10 p-3 text-sm text-good">
          {t('approved')}
        </p>
      ) : null}
      <Button size="sm" variant={open ? 'primary' : 'secondary'} className="w-fit gap-1.5" onClick={() => setOpen((v) => !v)}>
        <IdCard className="size-4" aria-hidden />
        {t('ask')}
      </Button>
      {open ? (
        <div className="flex flex-col gap-2 rounded-xl border border-border p-3">
          <p className="text-sm text-muted">{t('lead')}</p>
          <input
            ref={input}
            type="file"
            accept={[...STUDENT_ID_TYPES, '.jpg', '.jpeg', '.png', '.webp', '.pdf'].join(',')}
            className="sr-only"
            aria-label={t('choose')}
            onChange={(e) => {
              const picked = e.target.files?.[0] ?? null
              e.target.value = ''
              setError(null)
              if (!picked) return setFile(null)
              const local = studentIdFileProblem(picked)
              if (local) {
                setFile(null)
                setError(local === 'type' ? t('wrongType') : local === 'empty' ? t('empty') : t('tooBig'))
                return
              }
              setFile(picked)
            }}
          />
          <Button size="sm" variant="secondary" className="w-fit" onClick={() => input.current?.click()}>
            {t('choose')}
          </Button>
          {file ? (
            <div className="flex items-center gap-2 text-sm">
              <span className="flex-1 truncate">{file.name}</span>
              <button type="button" aria-label={t('remove', { name: file.name })} onClick={() => setFile(null)} className="rounded p-1 text-muted hover:bg-surface-2">
                <X className="size-4" aria-hidden />
              </button>
            </div>
          ) : null}
          {error ? <Problem>{error}</Problem> : null}
          <Button size="sm" className="w-fit" disabled={!file || busy} onClick={() => void send()}>
            {busy ? t('sending') : t('send')}
          </Button>
        </div>
      ) : error ? (
        <Problem>{error}</Problem>
      ) : null}
    </div>
  )
}

function Problem({ children }: { children: string }) {
  return (
    <p role="alert" className="text-sm text-bad">
      {children}
    </p>
  )
}

function errorCopy(t: (key: 'unavailable' | 'ratePending' | 'rateWeek' | 'rateEither' | 'tooBig' | 'wrongType' | 'failed') => string): StudentIdErrorCopy {
  return {
    unavailable: t('unavailable'),
    pending: t('ratePending'),
    week: t('rateWeek'),
    eitherLimit: t('rateEither'),
    tooBig: t('tooBig'),
    wrongType: t('wrongType'),
    failed: t('failed'),
  }
}

function shown(e: unknown, copy: StudentIdErrorCopy): string {
  if (e instanceof UploadError) return e.message
  if (CombinedGraphQLErrors.is(e)) {
    const err = e.errors[0]
    const code = typeof err?.extensions?.code === 'string' ? err.extensions.code : null
    return studentIdErrorMessage({ code, message: err?.message }, copy)
  }
  return copy.failed
}
