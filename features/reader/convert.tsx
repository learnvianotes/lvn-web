'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { CircleCheck, LoaderCircle, TriangleAlert, FilePenLine, X } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { ConvertPdfToNoteDocument, PdfPagesThisMonthDocument, type ConversionFieldsFragment } from '@/graphql/generated/graphql'

/**
 * Converting a PDF into a note of cards (lvn-backend ADR-0025, ADR-0028): the dialog that asks for it, and the banner
 * that follows it in the new note's reader, where the cards are checked beside the PDF (ADR-0040).
 */

export const ACTIVE: ConversionFieldsFragment['status'][] = ['QUEUED', 'TRIAGE', 'PARSING', 'MAPPING']

export function ConvertDialog({ open, onClose, noteId, fileId, fileName }: { open: boolean; onClose: () => void; noteId: string; fileId: string; fileName: string }) {
  const t = useTranslations('reader.convert')
  const router = useRouter()
  const usage = useQuery(PdfPagesThisMonthDocument, { skip: !open, fetchPolicy: 'network-only' })
  const [convert, converting] = useMutation(ConvertPdfToNoteDocument)
  const [error, setError] = useState<string | null>(null)
  const pages = usage.data?.pdfPagesThisMonth
  const start = async () => {
    setError(null)
    const res = await convert({ variables: { noteId, fileId } }).catch(() => null)
    const payload = res?.data?.convertPdfToNote
    const note = payload?.conversion?.note?.id
    if (note) router.push(`/notes/${note}/read/${fileId}`)
    else setError(payload?.userErrors[0]?.message ?? (res?.error ? t('notAllowed') : t('failed')))
  }
  return (
    <Dialog open={open} onClose={onClose} title={t('title')}>
      <div className="flex flex-col gap-3 text-sm">
        <p>{t('lead', { name: fileName })}</p>
        <ul className="list-disc pl-5 text-muted">
          <li>{t('point1')}</li>
          <li>{t('point2')}</li>
          <li>{t('point3')}</li>
        </ul>
        {pages ? <p className="text-xs text-muted">{pages.limit === null ? t('usageUnlimited', { used: pages.used }) : t('usage', { used: pages.used, limit: pages.limit })}</p> : null}
        {error ? (
          <p role="alert" className="text-bad">
            {error}
          </p>
        ) : null}
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button className="gap-1.5" disabled={converting.loading} onClick={() => void start()}>
            <FilePenLine className="size-4" aria-hidden />
            {converting.loading ? t('starting') : t('start')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

/** Where a conversion is: working (with its stage), done (check the cards, and what AI read again) or failed (why). */
export function ConversionBanner({ conversion, onDismiss }: { conversion: ConversionFieldsFragment; onDismiss: () => void }) {
  const t = useTranslations('reader.convert')
  const active = ACTIVE.includes(conversion.status)
  if (active) {
    return (
      <div role="status" className="flex shrink-0 items-center gap-3 border-b border-border bg-accent-soft px-3 py-2 text-sm">
        <LoaderCircle className="size-4 shrink-0 animate-spin text-accent" aria-hidden />
        <span className="min-w-0 flex-1">
          <span className="font-semibold">{t(`stage.${conversion.status}`)}</span>
          {conversion.pages ? <span className="text-muted"> · {t('pages', { n: conversion.pages, scanned: conversion.scannedPages ?? 0 })}</span> : null}
        </span>
        <span className="h-1.5 w-24 overflow-hidden rounded-full bg-border sm:w-40" aria-hidden>
          <span className="block h-full rounded-[10px] bg-accent transition-[width] duration-500" style={{ width: `${conversion.progress}%` }} />
        </span>
      </div>
    )
  }
  const done = conversion.status === 'DONE'
  return (
    <div role="status" className="flex shrink-0 items-start gap-3 border-b border-border bg-surface px-3 py-2 text-sm">
      {done ? <CircleCheck className="mt-0.5 size-4 shrink-0 text-good" aria-hidden /> : <TriangleAlert className="mt-0.5 size-4 shrink-0 text-warn" aria-hidden />}
      <span className="min-w-0 flex-1">
        {done ? t('done', { cards: conversion.cards ?? 0, pages: conversion.pages ?? 0 }) : (conversion.error ?? t('failed'))}
        {/* Pages the vision model read again (ADR-0063), and where scanned text may need mending. */}
        {done && conversion.aiPages ? <> {t('aiPages', { n: conversion.aiPages, rejected: conversion.aiRejected ?? 0 })}</> : null}
        {done && conversion.scannedPages ? <span className="text-muted"> {t('cleanUpHint')}</span> : null}
      </span>
      <button type="button" aria-label={t('dismiss')} title={t('dismiss')} className="rounded-lg p-1 text-muted hover:bg-surface-2 hover:text-fg" onClick={onDismiss}>
        <X className="size-4" aria-hidden />
      </button>
    </div>
  )
}
