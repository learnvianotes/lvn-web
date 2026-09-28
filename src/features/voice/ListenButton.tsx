/* "Listen" button — starts read-aloud of whatever `segments()` returns. */

import { Headphones, Square } from 'lucide-react'
import { speak, speechSupported, stop, useSpeech, type Segment } from '@/features/voice/speech'

interface Props {
  title: string
  segments: () => Segment[]
  label?: string
  compact?: boolean
}

export function ListenButton({ title, segments, label = 'Listen', compact = false }: Props) {
  const s = useSpeech()
  if (!speechSupported) return null
  const mine = s.status !== 'idle' && s.title === title
  return (
    <button
      className={`btn btn-sm listen-btn ${mine ? 'is-on' : ''}`}
      onClick={() => (mine ? stop() : speak(title, segments()))}
      aria-label={mine ? 'Stop reading aloud' : `${label}: read aloud`}
      title={mine ? 'Stop' : 'Read aloud'}
    >
      {mine ? <Square size={13} aria-hidden /> : <Headphones size={14} aria-hidden />}
      {!compact && <span>{mine ? 'Stop' : label}</span>}
    </button>
  )
}
