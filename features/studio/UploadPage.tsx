'use client'

import { Camera, FileUp } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useRef, useState } from 'react'
import { AiButton } from '@/features/ai/AiPanel'
import { AiResultPanel } from '@/features/ai/AiAction'
import { CaptureDialog } from '@/features/notes/capture/CaptureDialog'
import { useReadPdf } from '@/features/reader/readPdf'
import { useStudioAsk } from './useStudioAsk'

/** Upload is its own place: a drop zone for a PDF or a photo, not another note tile. */
export function UploadPage() {
  const t = useTranslations('studio.upload')
  const pdf = useReadPdf()
  const input = useRef<HTMLInputElement>(null)
  const [capture, setCapture] = useState(false)
  const [over, setOver] = useState(false)
  const ai = useStudioAsk(t('noteTitle'), t('aiSeed'))
  const take = (file: File | undefined) => {
    if (file) void pdf.start(file)
  }
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
      <header className="flex flex-wrap items-start justify-between gap-3 rounded-3xl border border-sky-700/25 bg-sky-50 px-4 py-4 text-sky-950 dark:bg-sky-950/40 dark:text-sky-50">
        <div className="flex min-w-0 flex-col gap-1">
          <p className="text-xs font-bold uppercase tracking-wider">{t('kicker')}</p>
          <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight sm:text-3xl">
            <FileUp className="size-7 shrink-0" aria-hidden />
            {t('title')}
          </h1>
          <p className="max-w-xl text-sm text-sky-900/80 dark:text-sky-100/80">{t('lead')}</p>
        </div>
        <AiButton onClick={() => void ai.ask()} />
      </header>
      <div
        onDragOver={(event) => {
          event.preventDefault()
          setOver(true)
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(event) => {
          event.preventDefault()
          setOver(false)
          take(event.dataTransfer.files[0])
        }}
        className={`flex min-h-64 flex-col items-center justify-center gap-4 rounded-3xl border-2 border-dashed px-4 py-10 text-center ${over ? 'border-sky-600 bg-sky-50 dark:bg-sky-950/30' : 'border-sky-700/30 bg-surface'}`}
      >
        <FileUp className="size-10 text-sky-700" aria-hidden />
        <p className="text-lg font-semibold">{t('drop')}</p>
        <div className="flex flex-wrap justify-center gap-2">
          <button type="button" className="inline-flex items-center gap-2 rounded-xl bg-sky-700 px-4 py-2 text-sm font-semibold text-white" onClick={() => input.current?.click()}>
            <FileUp className="size-4" aria-hidden />
            {t('pdf')}
          </button>
          <button type="button" className="inline-flex items-center gap-2 rounded-xl border border-sky-700 px-4 py-2 text-sm font-semibold text-sky-800 dark:text-sky-100" onClick={() => setCapture(true)}>
            <Camera className="size-4" aria-hidden />
            {t('photos')}
          </button>
        </div>
        <input
          ref={input}
          type="file"
          accept="application/pdf,.pdf"
          className="sr-only"
          aria-label={t('pdf')}
          onChange={(event) => {
            take(event.target.files?.[0])
            event.target.value = ''
          }}
        />
        {pdf.uploading ? <p className="text-sm text-muted">{t('uploading', { name: pdf.uploading.name })}</p> : null}
        {pdf.error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{pdf.error}</p> : null}
      </div>
      <AiResultPanel empty={!ai.busy && !ai.result && !ai.error}>
        {ai.busy ? <p className="text-sm text-muted">{t('working')}</p> : null}
        {ai.error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{ai.error}</p> : null}
        {ai.result ? <p className="whitespace-pre-wrap text-sm leading-6">{ai.result}</p> : null}
      </AiResultPanel>
      {capture ? <CaptureDialog open onClose={() => setCapture(false)} folderId={null} /> : null}
    </div>
  )
}
