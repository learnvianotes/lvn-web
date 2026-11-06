'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { TriangleAlert, CircleCheck, Download, FileArchive, LoaderCircle, Upload } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  CompleteNoteUploadDocument,
  ConfirmNoteImportDocument,
  CreateImportUploadDocument,
  ImportNotesDocument,
  MyDataExportsDocument,
  NoteImportsDocument,
  RequestDataExportDocument,
  type NoteImportFieldsFragment,
} from '@/graphql/generated/graphql'
import { trackUsage } from '@/lib/analytics'
import { formatBytes, putToStorage, UploadError } from '@/features/notes/media'
import { safeLinkHref } from '@/lib/http-url'
import { useUploadsEnabled } from '@/features/notes/uploads'

const IMPORT_TYPES: Record<string, string> = { zip: 'application/zip', md: 'text/markdown', markdown: 'text/markdown', txt: 'text/plain' }

/**
 * Settings → Data (lvn-backend ADR-0018): download everything about you, and bring notes in from LearnViaNotes exports,
 * Markdown and ZIPs of Markdown (Obsidian, Notion, Joplin). Both run in the background; the page follows them.
 */
export function YourData() {
  const t = useTranslations('data')
  // Importing uploads the file: only while uploads are on (lvn-backend ADR-0097). Downloading never needs them.
  const uploadsOn = useUploadsEnabled()
  return (
    <section id="your-data" aria-labelledby="your-data-heading" className="flex scroll-mt-20 flex-col gap-4 rounded-2xl border border-border bg-surface p-5">
      <h2 id="your-data-heading" className="text-lg font-bold">
        {t('title')}
      </h2>
      <ExportPart />
      {uploadsOn ? (
        <>
          <hr className="border-border" />
          <ImportPart />
        </>
      ) : null}
    </section>
  )
}

function ExportPart() {
  const t = useTranslations('data.export')
  const exports = useQuery(MyDataExportsDocument, { fetchPolicy: 'cache-and-network' })
  const latest = exports.data?.myDataExports[0]
  // While one is being prepared, look again every few seconds.
  const preparing = latest?.status === 'PENDING'
  useQuery(MyDataExportsDocument, { skip: !preparing, pollInterval: 4_000, fetchPolicy: 'network-only' })
  const [request, requesting] = useMutation(RequestDataExportDocument, { refetchQueries: [MyDataExportsDocument] })
  const [error, setError] = useState<string | null>(null)
  const downloadHref = latest?.status === 'READY' ? safeLinkHref(latest.downloadUrl) : null

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1">
        <h3 className="font-semibold">{t('heading')}</h3>
        <p className="text-sm text-muted">{t('lead')}</p>
      </div>
      {downloadHref && latest?.status === 'READY' ? (
        <div className="flex flex-wrap items-center gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm">
          <CircleCheck className="size-5 text-emerald-600" aria-hidden />
          <span className="flex-1">{t('ready', { size: formatBytes(latest.sizeBytes ?? 0), date: new Date(latest.expiresAt!).toLocaleDateString() })}</span>
          <a href={downloadHref} onClick={() => trackUsage('download', { kind: 'data_export' })} className="inline-flex items-center gap-1.5 rounded-full bg-accent px-3 py-1.5 font-semibold text-accent-fg hover:opacity-90">
            <Download className="size-4" aria-hidden />
            {t('download')}
          </a>
        </div>
      ) : null}
      {preparing ? (
        <p role="status" className="flex items-center gap-2 text-sm text-muted">
          <LoaderCircle className="size-4 animate-spin" aria-hidden />
          {t('preparing')}
        </p>
      ) : null}
      {latest?.status === 'FAILED' ? <p className="text-sm text-red-600 dark:text-red-400">{t('failed')}</p> : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <Button
        variant="secondary"
        className="w-fit gap-2"
        disabled={requesting.loading || preparing}
        onClick={async () => {
          setError(null)
          const res = await request().catch(() => null)
          const problem = res?.data?.requestDataExport.userErrors[0]?.message
          if (problem || !res) setError(problem ?? t('failed'))
        }}
      >
        <FileArchive className="size-4" aria-hidden />
        {t('request')}
      </Button>
    </div>
  )
}

function ImportPart() {
  const t = useTranslations('data.import')
  const client = useApolloClient()
  const input = useRef<HTMLInputElement>(null)
  const imports = useQuery(NoteImportsDocument, { fetchPolicy: 'cache-and-network' })
  const latest = imports.data?.noteImports[0]
  const running = latest?.status === 'PENDING' || latest?.status === 'RUNNING'
  useQuery(NoteImportsDocument, { skip: !running, pollInterval: 2_000, fetchPolicy: 'network-only' })
  const [startImport] = useMutation(ImportNotesDocument, { refetchQueries: [NoteImportsDocument] })
  const [confirm, confirming] = useMutation(ConfirmNoteImportDocument, { refetchQueries: [NoteImportsDocument] })
  const [uploading, setUploading] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)

  const choose = async (file: File) => {
    setError(null)
    const mimeType = IMPORT_TYPES[file.name.split('.').pop()?.toLowerCase() ?? '']
    if (!mimeType) return setError(t('wrongType'))
    try {
      setUploading(0)
      const res = await client.mutate({ mutation: CreateImportUploadDocument, variables: { input: { fileName: file.name, mimeType, sizeBytes: file.size, purpose: 'IMPORT' } } })
      const intent = res.data?.createUploadIntent.intent
      if (!intent) throw new UploadError(res.data?.createUploadIntent.userErrors[0]?.message ?? t('failed'))
      await putToStorage(intent, file, setUploading)
      const done = await client.mutate({ mutation: CompleteNoteUploadDocument, variables: { fileId: intent.fileId } })
      if (!done.data?.completeUpload.ok) throw new UploadError(done.data?.completeUpload.userErrors[0]?.message ?? t('failed'))
      const started = await startImport({ variables: { fileId: intent.fileId } })
      const problem = started.data?.importNotes.userErrors[0]?.message
      if (problem) throw new UploadError(problem)
    } catch (e) {
      setError(e instanceof UploadError && !/^(network|storage answered)/.test(e.message) ? e.message : t('failed'))
    } finally {
      setUploading(null)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-1">
        <h3 className="font-semibold">{t('heading')}</h3>
        <p className="text-sm text-muted">{t('lead')}</p>
      </div>
      <input
        ref={input}
        type="file"
        accept=".zip,.md,.markdown,.txt"
        className="sr-only"
        aria-label={t('choose')}
        onChange={(e) => {
          const file = e.target.files?.[0]
          e.target.value = ''
          if (file) void choose(file)
        }}
      />
      <Button variant="secondary" className="w-fit gap-2" disabled={uploading !== null || running} onClick={() => input.current?.click()}>
        <Upload className="size-4" aria-hidden />
        {t('choose')}
      </Button>
      {uploading !== null ? <Progress label={t('uploading')} value={uploading * 100} /> : null}
      {running ? <Progress label={t('importing', { file: latest!.fileName })} value={latest!.progress} /> : null}
      {latest?.status === 'NEEDS_CONFIRMATION' ? (
        <div role="status" className="flex flex-wrap items-center gap-3 rounded-xl border border-amber-500/40 bg-amber-50 p-3 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">
          <TriangleAlert className="size-5" aria-hidden />
          <span className="flex-1">{t('duplicate', { file: latest.fileName })}</span>
          <Button size="sm" disabled={confirming.loading} onClick={() => void confirm({ variables: { id: latest.id } })}>
            {t('importAgain')}
          </Button>
        </div>
      ) : null}
      {latest?.status === 'DONE' || latest?.status === 'FAILED' ? <Report imp={latest} /> : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </div>
  )
}

function Progress({ label, value }: { label: string; value: number }) {
  return (
    <div role="status" className="flex flex-col gap-1.5">
      <span className="text-sm text-muted">{label}</span>
      <div className="h-2 overflow-hidden rounded-full bg-surface-2" aria-hidden>
        <div className="h-full rounded-full bg-accent transition-[width]" style={{ width: `${Math.round(value)}%` }} />
      </div>
    </div>
  )
}

function Report({ imp }: { imp: NoteImportFieldsFragment }) {
  const t = useTranslations('data.import')
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border bg-bg p-3 text-sm">
      {imp.status === 'FAILED' ? (
        <p className="font-medium text-red-600 dark:text-red-400">{imp.error ?? t('failed')}</p>
      ) : (
        <p className="font-medium">{t('done', { n: imp.created, file: imp.fileName })}</p>
      )}
      {imp.notes.length ? (
        <ul className="flex flex-wrap gap-2">
          {imp.notes.slice(0, 12).map((n) => (
            <li key={n.id}>
              <Link href={`/notes/${n.id}`} className="rounded-full bg-accent-soft px-2.5 py-1 text-accent hover:underline">
                {n.title || t('untitled')}
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
      {imp.skipped.length ? (
        <details>
          <summary className="cursor-pointer text-muted">{t('skipped', { n: imp.skipped.length })}</summary>
          <ul className="mt-2 flex flex-col gap-1">
            {imp.skipped.slice(0, 50).map((s, i) => (
              <li key={i} className="text-xs">
                <code>{s.path}</code> — {s.reason}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </div>
  )
}
