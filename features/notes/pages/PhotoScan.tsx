'use client'

import { Camera, Contrast, Crop, ImagePlus } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { enhanceRgba, type RgbaRect } from './model'

/**
 * Photo scan: the camera on a phone (capture="environment" and getUserMedia), then crop and enhance before the picture
 * is placed on the page. A file is the fallback when the camera is refused.
 */
export function PhotoScan({ open, onClose, onImage }: { open: boolean; onClose: () => void; onImage: (href: string, name: string, file?: File) => void }) {
  const t = useTranslations('notes.pages')
  const video = useRef<HTMLVideoElement>(null)
  const stream = useRef<MediaStream | null>(null)
  const [shot, setShot] = useState<string | null>(null)
  const [crop, setCrop] = useState<RgbaRect | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState<{ x: number; y: number } | null>(null)

  const stop = () => {
    stream.current?.getTracks().forEach((track) => track.stop())
    stream.current = null
  }
  useEffect(() => {
    if (!open) {
      stop()
      setShot(null)
      setCrop(null)
      setError(null)
    }
    return stop
  }, [open])

  const start = async () => {
    setError(null)
    if (!navigator.mediaDevices?.getUserMedia) return setError(t('cameraUnsupported'))
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: 'environment' } }, audio: false })
      if (video.current) video.current.srcObject = stream.current
    } catch {
      setError(t('cameraDenied'))
    }
  }
  const snap = () => {
    const el = video.current
    if (!el?.videoWidth) return
    const canvas = document.createElement('canvas')
    canvas.width = el.videoWidth
    canvas.height = el.videoHeight
    canvas.getContext('2d')?.drawImage(el, 0, 0)
    setShot(canvas.toDataURL('image/png'))
    setCrop(null)
    stop()
  }
  const onFile = (file: File | undefined) => {
    if (!file) return
    if (!file.type.startsWith('image/')) return setError(t('notImage'))
    const reader = new FileReader()
    reader.onload = () => {
      setShot(typeof reader.result === 'string' ? reader.result : null)
      setCrop(null)
      stop()
    }
    reader.readAsDataURL(file)
  }
  const point = (event: React.PointerEvent<HTMLElement>) => {
    const box = event.currentTarget.getBoundingClientRect()
    return { x: (event.clientX - box.left) / box.width, y: (event.clientY - box.top) / box.height }
  }
  const apply = (enhance: boolean) => {
    if (!shot) return
    const image = new Image()
    image.onload = () => {
      const canvas = document.createElement('canvas')
      const rect = pixelRect(image.width, image.height, crop)
      canvas.width = rect.w
      canvas.height = rect.h
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(image, rect.x, rect.y, rect.w, rect.h, 0, 0, rect.w, rect.h)
      if (enhance) {
        const pixels = ctx.getImageData(0, 0, canvas.width, canvas.height)
        pixels.data.set(enhanceRgba(pixels.data))
        ctx.putImageData(pixels, 0, 0)
      }
      const href = canvas.toDataURL('image/png')
      onImage(href, 'Scan.png', fileFromDataUrl(href, 'Scan.png'))
      onClose()
    }
    image.src = shot
  }

  return (
    <Dialog open={open} onClose={onClose} title={t('scanTitle')} wide>
      <div className="flex flex-col gap-4">
        <p className="text-sm text-muted">{t('scanLead')}</p>
        {error ? <p role="alert" className="text-sm text-bad">{error}</p> : null}
        {!shot ? (
          <div className="flex flex-col gap-3">
            <video ref={video} autoPlay playsInline muted className="aspect-[3/4] w-full rounded-2xl bg-black object-cover sm:aspect-video" />
            <div className="flex flex-wrap gap-2">
              <Button type="button" className="gap-1.5" onClick={() => void start()}>
                <Camera className="size-4" aria-hidden />
                {t('openCamera')}
              </Button>
              <Button type="button" variant="secondary" className="gap-1.5" onClick={snap}>
                {t('takePhoto')}
              </Button>
              <label className="inline-flex h-11 cursor-pointer items-center gap-1.5 rounded-xl border border-border bg-surface px-4 text-sm font-medium">
                <ImagePlus className="size-4" aria-hidden />
                {t('choosePhoto')}
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  className="sr-only"
                  onChange={(event) => {
                    onFile(event.target.files?.[0])
                    event.target.value = ''
                  }}
                />
              </label>
            </div>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <div
              className="relative aspect-[3/4] w-full overflow-hidden rounded-2xl bg-black sm:aspect-video"
              onPointerDown={(event) => {
                event.currentTarget.setPointerCapture(event.pointerId)
                const at = point(event)
                setDragging(at)
                setCrop({ x: at.x, y: at.y, w: 0.02, h: 0.02 })
              }}
              onPointerMove={(event) => {
                if (!dragging) return
                const at = point(event)
                setCrop({ x: Math.min(dragging.x, at.x), y: Math.min(dragging.y, at.y), w: Math.abs(at.x - dragging.x), h: Math.abs(at.y - dragging.y) })
              }}
              onPointerUp={() => setDragging(null)}
            >
              {/* The scan is a local data URL the person just took. */}
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={shot} alt={t('scanPreview')} className="h-full w-full object-contain" />
              {crop && crop.w > 0.02 ? (
                <span aria-hidden className="absolute border-2 border-accent/40 bg-accent/20" style={{ left: `${crop.x * 100}%`, top: `${crop.y * 100}%`, width: `${crop.w * 100}%`, height: `${crop.h * 100}%` }} />
              ) : null}
            </div>
            <p className="text-xs text-muted">{t('cropHint')}</p>
            <div className="flex flex-wrap gap-2">
              <Button type="button" variant="secondary" className="gap-1.5" onClick={() => apply(false)}>
                <Crop className="size-4" aria-hidden />
                {t('useCrop')}
              </Button>
              <Button type="button" className="gap-1.5" onClick={() => apply(true)}>
                <Contrast className="size-4" aria-hidden />
                {t('enhance')}
              </Button>
              <Button type="button" variant="ghost" onClick={() => setShot(null)}>
                {t('retake')}
              </Button>
            </div>
          </div>
        )}
      </div>
    </Dialog>
  )
}

function fileFromDataUrl(href: string, name: string): File | undefined {
  const match = /^data:([^;,]+);base64,(.+)$/.exec(href)
  if (!match?.[1] || !match[2]) return undefined
  const bytes = Uint8Array.from(atob(match[2]), (char) => char.charCodeAt(0))
  return new File([bytes], name, { type: match[1] })
}

function pixelRect(width: number, height: number, crop: RgbaRect | null): RgbaRect {
  if (!crop || crop.w < 0.02 || crop.h < 0.02) return { x: 0, y: 0, w: width, h: height }
  return { x: Math.round(crop.x * width), y: Math.round(crop.y * height), w: Math.max(1, Math.round(crop.w * width)), h: Math.max(1, Math.round(crop.h * height)) }
}
