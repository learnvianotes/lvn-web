/** Live captions while a voice note is recording (Web Speech API, when the browser has it). */

export interface SpeechAlternative {
  transcript: string
}

export interface SpeechResultLike {
  isFinal: boolean
  0: SpeechAlternative
  length: number
}

export interface SpeechEventLike {
  resultIndex: number
  results: ArrayLike<SpeechResultLike>
}

export interface SpeechRec {
  continuous: boolean
  interimResults: boolean
  lang: string
  onresult: ((event: SpeechEventLike) => void) | null
  onerror: (() => void) | null
  start: () => void
  stop: () => void
}

/** Final phrases plus the latest interim hypothesis, as one line. */
export function captionsFromEvent(event: SpeechEventLike, finals: string): { finals: string; line: string } {
  let committed = finals
  let interim = ''
  for (let i = event.resultIndex; i < event.results.length; i++) {
    const result = event.results[i]
    const text = result?.[0]?.transcript ?? ''
    if (result?.isFinal) committed = joinCaption(committed, text)
    else interim = joinCaption(interim, text)
  }
  return { finals: committed, line: joinCaption(committed, interim) }
}

export function joinCaption(left: string, right: string): string {
  return `${left} ${right}`.replace(/\s+/g, ' ').trim()
}

export function speechRecognitionCtor(): (new () => SpeechRec) | null {
  if (typeof window === 'undefined') return null
  const host = window as Window & { SpeechRecognition?: new () => SpeechRec; webkitSpeechRecognition?: new () => SpeechRec }
  return host.SpeechRecognition ?? host.webkitSpeechRecognition ?? null
}
