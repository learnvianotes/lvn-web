'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { FileUp, GraduationCap, X } from 'lucide-react'
import { useFormatter, useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { CollegeIdOption } from '@/features/verification/CollegeIdOption'
import { putToStorage, UploadError } from '@/features/notes/media'
import { CompleteNoteUploadDocument, CreateNoteUploadDocument, FindTeachersDocument, MyVerificationRequestsDocument, RequestDocumentVerificationDocument, RequestTeacherVerificationDocument, WithdrawVerificationRequestDocument } from '@/graphql/generated/graphql'
import { useUploadsEnabled } from '@/features/notes/uploads'

/** What proof of enrolment may be (lvn-backend files.service: pictures or PDF), at most three files. */
const DOCUMENT_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
const MAX_DOCUMENTS = 3

type Teacher = { id: string; handle: string; displayName: string }

/**
 * Verifying without a college email (lvn-backend ADR-0019), for an unverified account: ask a verified teacher to vouch,
 * or send proof of enrolment that platform admins review (not for restricted minors). One request waits at a time; it
 * can be withdrawn, and a refusal says why.
 */
export function VerifyAccount({ restrictedMinor }: { restrictedMinor: boolean }) {
  const t = useTranslations('verification')
  const format = useFormatter()
  const mine = useQuery(MyVerificationRequestsDocument, { fetchPolicy: 'cache-and-network' })
  const [withdraw] = useMutation(WithdrawVerificationRequestDocument)
  const [mode, setMode] = useState<'teacher' | 'documents' | null>(null)
  const [error, setError] = useState<string | null>(null)
  // Documents are uploads: offered only while uploads are on (lvn-backend ADR-0097); asking a teacher always works.
  const uploadsOn = useUploadsEnabled()
  const documents = !restrictedMinor && uploadsOn
  // Account verification only: applications to teach have their own page (lvn-backend ADR-0073).
  const requests = (mine.data?.myVerificationRequests ?? []).filter((r) => r.purpose === 'ACCOUNT')
  const pending = requests.find((r) => r.status === 'PENDING')
  const last = requests[0]
  const done = async () => {
    setMode(null)
    await mine.refetch()
  }
  if (pending) {
    return (
      <div className="flex flex-col gap-2 rounded-xl border border-accent/30 bg-accent-soft/40 p-3 text-sm">
        <p className="font-semibold">{pending.method === 'TEACHER' ? t('waitingTeacher', { name: pending.teacher?.displayName ?? '' }) : t('waitingDocuments')}</p>
        <p className="text-muted">{t('sent', { when: format.dateTime(new Date(pending.createdAt), { dateStyle: 'medium' }) })}</p>
        <Button
          size="sm"
          variant="secondary"
          className="w-fit"
          onClick={async () => {
            setError(null)
            try {
              const res = await withdraw({ variables: { requestId: pending.id } })
              const problem = res.data?.withdrawVerificationRequest.userErrors[0]?.message
              if (problem) setError(problem)
              await mine.refetch()
            } catch (e) {
              setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
            }
          }}
        >
          {t('withdraw')}
        </Button>
        {error ? (
          <p role="alert" className="text-red-600 dark:text-red-400">
            {error}
          </p>
        ) : null}
        <CollegeIdOption restrictedMinor={restrictedMinor} />
      </div>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {last?.status === 'REJECTED' ? (
        <p role="status" className="rounded-xl border border-red-500/30 bg-red-50 p-3 text-sm text-red-950 dark:bg-red-950/30 dark:text-red-100">
          {t('rejected', { reason: last.reason ?? '' })}
        </p>
      ) : null}
      <p className="text-sm text-muted">{t(documents ? 'lead' : 'leadTeacherOnly')}</p>
      <div className="flex flex-wrap gap-2">
        <Button size="sm" variant={mode === 'teacher' ? 'primary' : 'secondary'} className="gap-1.5" onClick={() => setMode(mode === 'teacher' ? null : 'teacher')}>
          <GraduationCap className="size-4" aria-hidden />
          {t('askTeacher')}
        </Button>
        {documents ? (
          <Button size="sm" variant={mode === 'documents' ? 'primary' : 'secondary'} className="gap-1.5" onClick={() => setMode(mode === 'documents' ? null : 'documents')}>
            <FileUp className="size-4" aria-hidden />
            {t('sendDocuments')}
          </Button>
        ) : null}
      </div>
      {mode === 'teacher' ? <AskTeacher onSent={() => void done()} /> : null}
      {mode === 'documents' ? <SendDocuments onSent={() => void done()} /> : null}
      <CollegeIdOption restrictedMinor={restrictedMinor} />
    </div>
  )
}

function AskTeacher({ onSent }: { onSent: () => void }) {
  const t = useTranslations('verification')
  const [query, setQuery] = useState('')
  const [settled, setSettled] = useState('')
  const [teacher, setTeacher] = useState<Teacher | null>(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [request, requesting] = useMutation(RequestTeacherVerificationDocument)
  useEffect(() => {
    const timer = setTimeout(() => setSettled(query.trim()), 250)
    return () => clearTimeout(timer)
  }, [query])
  const found = useQuery(FindTeachersDocument, { variables: { query: settled }, skip: settled.length < 2 })
  const teachers = (found.data?.search.people ?? []).filter((p) => p.globalRole === 'TEACHER')
  const send = async () => {
    if (!teacher) return
    setError(null)
    try {
      const res = await request({ variables: { input: { teacherId: teacher.id, message: message.trim() || null } } })
      const problem = res.data?.requestTeacherVerification.userErrors[0]?.message
      if (problem) setError(problem)
      else onSent()
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border p-3">
      {teacher ? (
        <div className="flex items-center gap-2 text-sm">
          <span className="flex-1">{t('teacherChosen', { name: teacher.displayName, handle: teacher.handle })}</span>
          <Button size="sm" variant="ghost" aria-label={t('changeTeacher')} onClick={() => setTeacher(null)}>
            <X className="size-4" aria-hidden />
          </Button>
        </div>
      ) : (
        <>
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium">{t('findTeacher')}</span>
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('findTeacherHint')} className="h-10 rounded-xl border border-border bg-bg px-3 text-sm" />
          </label>
          {settled.length >= 2 && found.data ? (
            teachers.length ? (
              <ul className="flex flex-col gap-1">
                {teachers.map((p) => (
                  <li key={p.id}>
                    <button type="button" onClick={() => setTeacher(p)} className="w-full rounded-lg px-2 py-1.5 text-left text-sm hover:bg-surface-2">
                      {p.displayName} <span className="text-muted">@{p.handle}</span>
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted">{t('noTeachers')}</p>
            )
          ) : null}
        </>
      )}
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium">{t('message')}</span>
        <textarea value={message} maxLength={500} rows={2} onChange={(e) => setMessage(e.target.value)} placeholder={t('messageHint')} className="rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
      </label>
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <Button size="sm" className="w-fit" disabled={!teacher || requesting.loading} onClick={() => void send()}>
        {t('sendRequest')}
      </Button>
    </div>
  )
}

function SendDocuments({ onSent }: { onSent: () => void }) {
  const t = useTranslations('verification')
  const client = useApolloClient()
  const input = useRef<HTMLInputElement>(null)
  const [files, setFiles] = useState<File[]>([])
  const [message, setMessage] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [request] = useMutation(RequestDocumentVerificationDocument)
  const send = async () => {
    setError(null)
    setBusy(true)
    try {
      const fileIds: string[] = []
      for (const file of files) {
        const res = await client.mutate({ mutation: CreateNoteUploadDocument, variables: { input: { fileName: file.name, mimeType: file.type, sizeBytes: file.size, purpose: 'VERIFICATION_DOCUMENT' } } })
        const intent = res.data?.createUploadIntent.intent
        if (!intent) throw new UploadError(res.data?.createUploadIntent.userErrors[0]?.message ?? t('failed'))
        await putToStorage(intent, file, () => undefined)
        const done = await client.mutate({ mutation: CompleteNoteUploadDocument, variables: { fileId: intent.fileId } })
        if (!done.data?.completeUpload.ok) throw new UploadError(done.data?.completeUpload.userErrors[0]?.message ?? t('failed'))
        fileIds.push(intent.fileId)
      }
      const res = await request({ variables: { input: { fileIds, message: message.trim() || null } } })
      const problem = res.data?.requestDocumentVerification.userErrors[0]?.message
      if (problem) throw new UploadError(problem)
      onSent()
    } catch (e) {
      setError(e instanceof UploadError ? e.message : CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border p-3">
      <p className="text-sm text-muted">{t('documentsLead')}</p>
      <input
        ref={input}
        type="file"
        multiple
        accept={DOCUMENT_TYPES.join(',')}
        className="sr-only"
        aria-label={t('chooseDocuments')}
        onChange={(e) => {
          const picked = [...(e.target.files ?? [])].filter((f) => DOCUMENT_TYPES.includes(f.type))
          e.target.value = ''
          setFiles((list) => [...list, ...picked].slice(0, MAX_DOCUMENTS))
        }}
      />
      <Button size="sm" variant="secondary" className="w-fit" disabled={files.length >= MAX_DOCUMENTS} onClick={() => input.current?.click()}>
        {t('chooseDocuments')}
      </Button>
      {files.length ? (
        <ul className="flex flex-col gap-1 text-sm">
          {files.map((f, i) => (
            <li key={`${f.name}-${i}`} className="flex items-center gap-2">
              <span className="flex-1 truncate">{f.name}</span>
              <button type="button" aria-label={t('removeDocument', { name: f.name })} onClick={() => setFiles((list) => list.filter((_, j) => j !== i))} className="rounded p-1 text-muted hover:bg-surface-2">
                <X className="size-4" aria-hidden />
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium">{t('message')}</span>
        <textarea value={message} maxLength={500} rows={2} onChange={(e) => setMessage(e.target.value)} className="rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
      </label>
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <Button size="sm" className="w-fit" disabled={!files.length || busy} onClick={() => void send()}>
        {busy ? t('sending') : t('sendRequest')}
      </Button>
    </div>
  )
}
