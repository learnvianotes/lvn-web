'use client'

import { Mic, Square } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'

/**
 * A voice note recorded in the browser (lvn-backend ADR-0062): MediaRecorder, Opus in WebM (MP4 where WebM is not
 * recorded, as on Safari). The recording becomes an ordinary audio card, uploaded like a dropped file; transcribing it
 * is one of the note's AI tasks.
 */

/** The longest recording, as the transcription's limit */
export const MAX_RECORDING_SECONDS = 30 * 60

type State = 'idle' | 'recording' | 'recorded' | 'denied' | 'unsupported'

const recordingType = () => (typeof MediaRecorder === 'undefined' ? null : ['audio/webm;codecs=opus', 'audio/webm', 'audio/mp4'].find((t) => MediaRecorder.isTypeSupported(t)) ?? null)
const clock = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

export function RecordDialog({ open, onClose, onDone }: { open: boolean; onClose: () => void; onDone: (file: File) => void }) {
  const t = useTranslations('notes.record')
  const [state, setState] = useState<State>('idle')
  const [seconds, setSeconds] = useState(0)
  const [recording, setRecording] = useState<{ blob: Blob; url: string } | null>(null)
  const recorder = useRef<MediaRecorder | null>(null)
  const stream = useRef<MediaStream | null>(null)
  const timer = useRef<ReturnType<typeof setInterval> | undefined>(undefined)

  const release = () => {
    clearInterval(timer.current)
    stream.current?.getTracks().forEach((track) => track.stop())
    stream.current = null
  }
  const reset = () => {
    release()
    if (recorder.current?.state === 'recording') recorder.current.stop()
    recorder.current = null
    setRecording((r) => (r && URL.revokeObjectURL(r.url), null))
    setSeconds(0)
    setState('idle')
  }
  useEffect(() => {
    if (!open) reset()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])
  useEffect(() => () => release(), [])

  const start = async () => {
    const type = recordingType()
    if (!type || !navigator.mediaDevices?.getUserMedia) return setState('unsupported')
    try {
      stream.current = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      return setState('denied')
    }
    const chunks: Blob[] = []
    const rec = new MediaRecorder(stream.current, { mimeType: type })
    rec.ondataavailable = (e) => e.data.size && chunks.push(e.data)
    rec.onstop = () => {
      release()
      const blob = new Blob(chunks, { type: type.split(';')[0] })
      setRecording({ blob, url: URL.createObjectURL(blob) })
      setState('recorded')
    }
    recorder.current = rec
    rec.start(1000)
    setSeconds(0)
    setState('recording')
    timer.current = setInterval(() => {
      setSeconds((s) => {
        if (s + 1 >= MAX_RECORDING_SECONDS) rec.stop()
        return s + 1
      })
    }, 1000)
  }
  const stop = () => recorder.current?.state === 'recording' && recorder.current.stop()
  const add = () => {
    if (!recording) return
    const mime = recording.blob.type || 'audio/webm'
    const stamp = new Date().toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }).replace(/[/:]/g, '-')
    onDone(new File([recording.blob], `Voice note ${stamp}.${mime === 'audio/mp4' ? 'm4a' : 'webm'}`, { type: mime }))
    reset()
  }

  return (
    <Dialog open={open} onClose={onClose} title={t('title')}>
      <div className="flex flex-col items-center gap-4 py-2 text-center">
        {state === 'denied' ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{t('denied')}</p> : null}
        {state === 'unsupported' ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{t('unsupported')}</p> : null}
        {state === 'idle' || state === 'denied' || state === 'unsupported' ? (
          <>
            <p className="text-sm text-muted">{t('lead')}</p>
            <Button size="lg" className="gap-2" disabled={state === 'unsupported'} onClick={() => void start()}>
              <Mic className="size-5" aria-hidden />
              {t('start')}
            </Button>
          </>
        ) : null}
        {state === 'recording' ? (
          <>
            <p role="status" className="flex items-center gap-2 font-mono text-3xl tabular-nums" aria-label={t('recordingFor', { time: clock(seconds) })}>
              <span className="size-3 animate-pulse rounded-full bg-red-500" aria-hidden />
              {clock(seconds)}
            </p>
            <Button size="lg" variant="secondary" className="gap-2" onClick={stop}>
              <Square className="size-5" aria-hidden />
              {t('stop')}
            </Button>
          </>
        ) : null}
        {state === 'recorded' && recording ? (
          <>
            <audio controls src={recording.url} className="w-full" aria-label={t('listen')} />
            <div className="flex gap-2">
              <Button variant="secondary" onClick={reset}>
                {t('again')}
              </Button>
              <Button onClick={add}>{t('add')}</Button>
            </div>
          </>
        ) : null}
      </div>
    </Dialog>
  )
}
