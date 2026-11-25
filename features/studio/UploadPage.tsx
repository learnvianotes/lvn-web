'use client'

import { Camera, FileUp } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useRef, useState } from 'react'
import { AiButton } from '@/features/ai/AiPanel'
import { AiResultPanel } from '@/features/ai/AiAction'
import { CaptureDialog } from '@/features/notes/capture/CaptureDialog'
import { useReadPdf } from '@/features/reader/readPdf'
import { StudyLoader } from '@/components/ui/study-loader'
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
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <h1 className="text-2xl font-medium sm:text-3xl">{t('title')}</h1>
          <p className="max-w-xl text-sm text-muted">{t('lead')}</p>
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
        className={`flex min-h-64 flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed px-4 py-10 text-center transition-colors ${over ? 'border-accent/50 bg-accent-soft' : 'border-border bg-surface'}`}
      >
        {pdf.uploading ? (
          <StudyLoader kind="upload" label={t('uploading', { name: pdf.uploading.name })} progress={pdf.uploading.progress} />
        ) : (
          <>
        <FileUp className="size-8 text-muted" strokeWidth={1.5} aria-hidden />
        <p className="text-lg font-medium">{t('drop')}</p>
        <div className="flex flex-wrap justify-center gap-2">
          <button type="button" className="inline-flex h-10 items-center gap-2 rounded-[4px] bg-accent px-4 text-sm font-medium text-accent-fg transition-colors hover:bg-[var(--accent-hover)]" onClick={() => input.current?.click()}>
            <FileUp className="size-4" aria-hidden />
            {t('pdf')}
          </button>
          <button type="button" className="inline-flex h-10 items-center gap-2 rounded-[4px] border border-border bg-surface px-4 text-sm font-medium transition-colors hover:bg-surface-2" onClick={() => setCapture(true)}>
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
          </>
        )}
        {pdf.error ? <p role="alert" className="text-sm text-bad">{pdf.error}</p> : null}
      </div>
      <AiResultPanel empty={!ai.busy && !ai.result && !ai.error}>
        {ai.busy ? <StudyLoader kind="nova" compact /> : null}
        {ai.error ? <p role="alert" className="text-sm text-bad">{ai.error}</p> : null}
        {ai.result ? <p className="whitespace-pre-wrap text-sm leading-6">{ai.result}</p> : null}
      </AiResultPanel>
      {capture ? <CaptureDialog open onClose={() => setCapture(false)} folderId={null} /> : null}
    </div>
  )
}
