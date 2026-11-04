'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { Mic, Square } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { AiResultPanel } from '@/features/ai/AiAction'
import { uploadVoiceNote } from '@/features/beta/api'
import { MakeNotesFromTranscriptDocument, TranscribeAudioDocument, TranscribeCaptionClipDocument, VoiceCaptureDocument } from '@/graphql/generated/graphql'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { captionsFromEvent, speechRecognitionCtor, type SpeechRec } from './captions'
import { trackFeature } from '@/lib/analytics'

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

export function RecordDialog({ open, onClose, onDone, noteId }: { open: boolean; onClose: () => void; onDone: (file: File) => void; noteId?: string }) {
  const t = useTranslations('notes.record')
  const client = useApolloClient()
  const guide = useQuery(VoiceCaptureDocument, { variables: { input: { noteId: noteId ?? '' } }, skip: !open || !noteId, fetchPolicy: 'cache-first' })
  const [transcribeClip] = useMutation(TranscribeCaptionClipDocument)
  const [transcribeFile] = useMutation(TranscribeAudioDocument)
  const [makeNotes] = useMutation(MakeNotesFromTranscriptDocument)
  const [state, setState] = useState<State>('idle')
  const [seconds, setSeconds] = useState(0)
  const [recording, setRecording] = useState<{ blob: Blob; url: string } | null>(null)
  const [captions, setCaptions] = useState('')
  const [captionsLive, setCaptionsLive] = useState(false)
  const [transcript, setTranscript] = useState<string | null>(null)
  const [notes, setNotes] = useState<string | null>(null)
  const [aiError, setAiError] = useState<string | null>(null)
  const [aiBusy, setAiBusy] = useState(false)
  const recorder = useRef<MediaRecorder | null>(null)
  const stream = useRef<MediaStream | null>(null)
  const speech = useRef<SpeechRec | null>(null)
  const finals = useRef('')
  const timer = useRef<ReturnType<typeof setInterval> | undefined>(undefined)

  const release = () => {
    clearInterval(timer.current)
    stream.current?.getTracks().forEach((track) => track.stop())
    stream.current = null
    try {
      speech.current?.stop()
    } catch {
      /* already stopped */
    }
    speech.current = null
  }
  const reset = () => {
    release()
    if (recorder.current?.state === 'recording') recorder.current.stop()
    recorder.current = null
    setRecording((r) => (r && URL.revokeObjectURL(r.url), null))
    setSeconds(0)
    setCaptions('')
    setTranscript(null)
    setNotes(null)
    setAiError(null)
    finals.current = ''
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
    trackFeature('voice_note')
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
    finals.current = ''
    setCaptions('')
    const Ctor = speechRecognitionCtor()
    setCaptionsLive(!!Ctor)
    if (Ctor) {
      const heard = new Ctor()
      const speechGuide = guide.data?.voiceCapture.voiceCapture
      heard.continuous = speechGuide?.continuous ?? true
      heard.interimResults = speechGuide?.interimResults ?? true
      heard.lang = speechGuide?.languages[0] ?? 'en-US'
      heard.onresult = (event) => {
        const next = captionsFromEvent(event, finals.current)
        finals.current = next.finals
        setCaptions(next.line)
      }
      heard.onerror = () => setCaptionsLive(false)
      try {
        heard.start()
        speech.current = heard
      } catch {
        setCaptionsLive(false)
      }
    }
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
  const runAi = async (kind: 'transcribe' | 'notes') => {
    if (!noteId) return
    setAiBusy(true)
    setAiError(null)
    try {
      if (kind === 'transcribe') {
        let fileId: string | null = null
        if (recording) {
          const mime = recording.blob.type || 'audio/webm'
          const file = new File([recording.blob], `voice.${mime === 'audio/mp4' ? 'm4a' : 'webm'}`, { type: mime })
          fileId = await uploadVoiceNote(client, noteId, file).catch(() => null)
        }
        const clip = await transcribeClip({ variables: { input: { noteId, captions } } })
        const full = fileId ? await transcribeFile({ variables: { input: { noteId, fileId, captions } } }) : null
        const clipPayload = clip.data?.transcribeCaptionClip
        const fullPayload = full?.data?.transcribeAudio
        const problem = fullPayload?.userErrors[0]?.message ?? clipPayload?.userErrors[0]?.message
        const spoken = fullPayload?.transcript ?? clipPayload?.transcript
        const text = spoken?.text
        if (problem || !text) setAiError(problem ?? t('aiFailed'))
        else setTranscript(spoken?.cut ? `${text}\n\n${t('cut')}` : text)
      } else {
        const source = transcript || captions
        const made = await makeNotes({ variables: { input: { noteId, transcript: source } } })
        const payload = made.data?.makeNotesFromTranscript
        const problem = payload?.userErrors[0]?.message
        if (problem || !payload?.notes) setAiError(problem ?? t('aiFailed'))
        else setNotes([payload.notes.title, payload.notes.summary].filter(Boolean).join('\n\n') || t('notesReady'))
      }
    } catch {
      setAiError(t('aiFailed'))
    } finally {
      setAiBusy(false)
    }
  }
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
            <p aria-live="polite" className="min-h-10 w-full rounded-xl bg-surface-2 px-3 py-2 text-left text-sm">
              {captions || (captionsLive ? t('listening') : t('captionsFallback'))}
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
            <p aria-live="polite" className="w-full rounded-xl bg-surface-2 px-3 py-2 text-left text-sm">{captions || t('captionsFallback')}</p>
            <div className="flex flex-wrap justify-center gap-2">
              <Button variant="secondary" onClick={reset}>
                {t('again')}
              </Button>
              <Button onClick={add}>{t('add')}</Button>
              {noteId ? (
                <>
                  <Button variant="secondary" disabled={aiBusy} onClick={() => void runAi('transcribe')}>{t('transcribe')}</Button>
                  <Button variant="secondary" disabled={aiBusy} onClick={() => void runAi('notes')}>{t('makeNotes')}</Button>
                </>
              ) : null}
            </div>
            <AiResultPanel empty={!transcript && !notes && !aiError && !aiBusy} className="w-full text-left">
              {aiBusy ? <p className="text-sm text-muted">{t('working')}</p> : null}
              {aiError ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{aiError}</p> : null}
              {transcript ? <p className="whitespace-pre-wrap text-sm">{transcript}</p> : null}
              {notes ? <p className="whitespace-pre-wrap text-sm">{notes}</p> : null}
            </AiResultPanel>
          </>
        ) : null}
      </div>
    </Dialog>
  )
}
