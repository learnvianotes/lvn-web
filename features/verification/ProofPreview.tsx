'use client'

import { useEffect, useRef, useState } from 'react'
import { Dialog } from '@/components/ui/dialog'
import { proofKind } from './proof'

/**
 * A proof file from a short-lived signed URL. Pictures zoom. PDFs render with pdf.js (the same build the reader
 * uses) and always offer the file in a new tab when the preview cannot load.
 */
export function ProofPreview({ url, mime, name, openLabel, failedLabel }: { url: string; mime: string; name: string; openLabel: string; failedLabel: string }) {
  const kind = proofKind(mime, name)
  return (
    <div className="flex flex-col gap-2">
      {kind === 'image' ? <ZoomImage url={url} name={name} /> : null}
      {kind === 'pdf' ? <PdfEmbed url={url} name={name} failedLabel={failedLabel} /> : null}
      <a href={url} target="_blank" rel="noopener noreferrer" className="inline-flex min-h-11 w-fit items-center text-sm font-medium text-accent hover:underline">
        {openLabel}
      </a>
    </div>
  )
}

function ZoomImage({ url, name }: { url: string; name: string }) {
  const [open, setOpen] = useState(false)
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} className="w-fit max-w-full rounded-xl border border-border bg-bg p-1" aria-label={name}>
        {/* The signed URL is the file itself. next/image cannot optimise an arbitrary storage host. */}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={url} alt={name} className="max-h-48 max-w-full rounded-lg object-contain" />
      </button>
      <Dialog open={open} onClose={() => setOpen(false)} title={name} wide>
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={url} alt={name} className="max-h-[70dvh] w-full object-contain" />
      </Dialog>
    </>
  )
}

function PdfEmbed({ url, name, failedLabel }: { url: string; name: string; failedLabel: string }) {
  const host = useRef<HTMLDivElement>(null)
  const [failed, setFailed] = useState(false)
  useEffect(() => {
    const box = host.current
    if (!box) return
    let cancelled = false
    let task: { destroy: () => Promise<void> } | null = null
    void (async () => {
      try {
        const pdfjs = await import('pdfjs-dist')
        pdfjs.GlobalWorkerOptions.workerSrc = `/pdfjs/${pdfjs.version}/pdf.worker.min.mjs`
        const loading = pdfjs.getDocument({ url, disableRange: true, disableStream: true })
        task = loading
        const doc = await loading.promise
        if (cancelled) return
        const pages = Math.min(doc.numPages, 3)
        box.replaceChildren()
        for (let number = 1; number <= pages; number++) {
          const page = await doc.getPage(number)
          if (cancelled) return
          const viewport = page.getViewport({ scale: 1.25 })
          const canvas = document.createElement('canvas')
          canvas.width = viewport.width
          canvas.height = viewport.height
          canvas.className = 'h-auto w-full bg-white'
          canvas.setAttribute('aria-label', `${name}, page ${number}`)
          const context = canvas.getContext('2d')
          if (!context) throw new Error('canvas')
          await page.render({ canvas, canvasContext: context, viewport }).promise
          box.appendChild(canvas)
        }
      } catch {
        if (!cancelled) setFailed(true)
      }
    })()
    return () => {
      cancelled = true
      void task?.destroy().catch(() => undefined)
    }
  }, [url, name])
  if (failed) return <p className="text-sm text-muted">{failedLabel}</p>
  return <div ref={host} className="flex max-h-[28rem] flex-col gap-2 overflow-auto rounded-xl border border-border bg-surface-2 p-2" />
}
