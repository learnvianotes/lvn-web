'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { X } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useRef, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import { putToStorage, UploadError } from '@/features/notes/media'
import { ApplyToTeachDocument, CompleteNoteUploadDocument, CreateNoteUploadDocument, MyTeacherApplicationDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { useUploadsEnabled } from '@/features/notes/uploads'

const PROOF_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf']
const MAX_PROOF = 3

/**
 * Becoming a teacher (lvn-backend ADR-0073), "try now, verify later": where and what the person teaches, a message and
 * proof go to the platform admins; meanwhile they set up classes, which take students once they are verified.
 */
export function Teach() {
  const t = useTranslations('teach')
  const format = useFormatter()
  const client = useApolloClient()
  const viewerQuery = useQuery(ViewerDocument)
  const viewer = viewerQuery.data?.viewer
  const app = useQuery(MyTeacherApplicationDocument, { fetchPolicy: 'cache-and-network' })
  const latest = app.data?.myTeacherApplication
  if (!viewer) return <QueryState loading={viewerQuery.loading} error={viewerQuery.error} onRetry={viewerQuery.refetch} />
  // Without the application a pending applicant would be offered the form again.
  if (!app.data) return <QueryState loading={app.loading} error={app.error} onRetry={app.refetch} />
  const status = viewer.teacherStatus
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {status === 'VERIFIED' ? (
        <section role="status" className="flex flex-col gap-2 rounded-2xl border border-accent/30 bg-accent-soft p-5">
          <h2 className="text-lg font-bold">{t('verifiedTitle')}</h2>
          <p className="text-sm">{t('verifiedLead')}</p>
          <Link href="/classes" className="text-sm font-semibold text-accent hover:underline">
            {t('newClass')} →
          </Link>
        </section>
      ) : status === 'PENDING' && latest ? (
        <section role="status" className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-5">
          <h2 className="text-lg font-bold">{t('pendingTitle')}</h2>
          <p className="text-sm text-muted">{t('pendingLead', { when: format.dateTime(new Date(latest.createdAt), { dateStyle: 'medium' }) })}</p>
          <Link href="/classes" className="text-sm font-semibold text-accent hover:underline">
            {t('newClass')} →
          </Link>
        </section>
      ) : viewer.restrictedMinor ? (
        <Alert>{t('minor')}</Alert>
      ) : (
        <>
          {status === 'DECLINED' && latest ? (
            <section role="status" className="rounded-2xl border border-border bg-surface-2 p-4 text-sm">
              <p className="font-semibold">{t('declinedTitle')}</p>
              <p className="text-muted">{t('declinedLead', { reason: latest.reason ?? '' })}</p>
            </section>
          ) : null}
          <ApplyForm onSent={() => void client.refetchQueries({ include: [MyTeacherApplicationDocument, ViewerDocument] })} />
        </>
      )}
    </div>
  )
}

function ApplyForm({ onSent }: { onSent: () => void }) {
  const t = useTranslations('teach')
  // Proof files are uploads and optional (0–3): offered only while uploads are on (lvn-backend ADR-0097).
  const uploadsOn = useUploadsEnabled()
  const client = useApolloClient()
  const input = useRef<HTMLInputElement>(null)
  const [institution, setInstitution] = useState('')
  const [subjects, setSubjects] = useState('')
  const [message, setMessage] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [apply] = useMutation(ApplyToTeachDocument)
  return (
    <form
      aria-label={t('submit')}
      className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-5"
      onSubmit={async (e) => {
        e.preventDefault()
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
          const res = await apply({ variables: { input: { institution, subjects: subjects.trim() || null, message: message.trim() || null, fileIds } } })
          const problem = res.data?.applyToTeach.userErrors[0]?.message
          if (problem) throw new UploadError(problem)
          onSent()
        } catch (err) {
          setError(err instanceof UploadError ? err.message : CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed'))
        } finally {
          setBusy(false)
        }
      }}
    >
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium">{t('institution')}</span>
        <input required maxLength={200} value={institution} placeholder={t('institutionHint')} onChange={(e) => setInstitution(e.target.value)} className="h-11 rounded-xl border border-border bg-bg px-3" />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium">{t('subjects')}</span>
        <input maxLength={200} value={subjects} onChange={(e) => setSubjects(e.target.value)} className="h-11 rounded-xl border border-border bg-bg px-3" />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium">{t('message')}</span>
        <textarea maxLength={500} rows={2} value={message} onChange={(e) => setMessage(e.target.value)} className="rounded-xl border border-border bg-bg px-3 py-2" />
      </label>
      {uploadsOn ? (
      <div className="flex flex-col gap-2">
        <span className="text-sm font-medium">{t('proof')}</span>
        <input
          ref={input}
          type="file"
          multiple
          accept={PROOF_TYPES.join(',')}
          className="sr-only"
          aria-label={t('chooseProof')}
          onChange={(e) => {
            const picked = [...(e.target.files ?? [])].filter((f) => PROOF_TYPES.includes(f.type))
            e.target.value = ''
            setFiles((list) => [...list, ...picked].slice(0, MAX_PROOF))
          }}
        />
        <Button type="button" size="sm" variant="secondary" className="w-fit" disabled={files.length >= MAX_PROOF} onClick={() => input.current?.click()}>
          {t('chooseProof')}
        </Button>
        {files.length ? (
          <ul className="flex flex-col gap-1 text-sm">
            {files.map((f, i) => (
              <li key={`${f.name}-${i}`} className="flex items-center gap-2">
                <span className="flex-1 truncate">{f.name}</span>
                <button type="button" aria-label={t('removeProof', { name: f.name })} onClick={() => setFiles((list) => list.filter((_, j) => j !== i))} className="rounded p-1 text-muted hover:bg-surface-2">
                  <X className="size-4" aria-hidden />
                </button>
              </li>
            ))}
          </ul>
        ) : null}
      </div>
      ) : null}
      {error ? <Alert tone="error">{error}</Alert> : null}
      <Button type="submit" className="self-start" disabled={busy || institution.trim().length < 2}>
        {t('submit')}
      </Button>
    </form>
  )
}
