'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { trackFeature } from '@/lib/analytics'

/**
 * Read aloud (ADR-0025): the browser's own text-to-speech (Web Speech API) — free, offline, nothing leaves the device.
 * Cards are read in order; the current one is reported so the page can highlight it. Long cards are split into
 * sentences, because some engines stop long utterances half-way.
 */

export interface SpokenCard {
  id: string
  text: string
}

export type ReadAloudState = 'idle' | 'playing' | 'paused'

const chunks = (text: string): string[] =>
  text
    .split(/(?<=[.!?])\s+|\n+/)
    .map((s) => s.trim())
    .filter(Boolean)
    .flatMap((s) => (s.length <= 220 ? [s] : (s.match(/.{1,220}(\s|$)/g) ?? [s])))

export function useReadAloud(cards: () => SpokenCard[]) {
  const [state, setState] = useState<ReadAloudState>('idle')
  const [current, setCurrent] = useState<string | null>(null)
  const [rate, setRate] = useState(1)
  const run = useRef(0)
  // Known only in the browser and after hydration: the server's HTML never offers it, so the first render matches.
  const [supported, setSupported] = useState(false)
  useEffect(() => setSupported('speechSynthesis' in window), [])

  const stop = useCallback(() => {
    run.current++
    if (supported) window.speechSynthesis.cancel()
    setState('idle')
    setCurrent(null)
  }, [supported])

  const play = useCallback(
    (fromId?: string) => {
      if (!supported) return
      trackFeature('read_aloud')
      window.speechSynthesis.cancel()
      const mine = ++run.current
      const list = cards().filter((c) => c.text.trim())
      const start = Math.max(0, fromId ? list.findIndex((c) => c.id === fromId) : 0)
      const queue = list.slice(start).flatMap((card) => chunks(card.text).map((text) => ({ id: card.id, text })))
      if (!queue.length) return
      setState('playing')
      queue.forEach((item, i) => {
        const u = new SpeechSynthesisUtterance(item.text)
        u.rate = rate
        u.onstart = () => mine === run.current && setCurrent(item.id)
        if (i === queue.length - 1) u.onend = () => mine === run.current && (setState('idle'), setCurrent(null))
        window.speechSynthesis.speak(u)
      })
    },
    [cards, rate, supported],
  )

  const pause = useCallback(() => {
    if (!supported) return
    window.speechSynthesis.pause()
    setState('paused')
  }, [supported])

  const resume = useCallback(() => {
    if (!supported) return
    window.speechSynthesis.resume()
    setState('playing')
  }, [supported])

  useEffect(() => () => {
    run.current++
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) window.speechSynthesis.cancel()
  }, [])

  return { supported, state, current, rate, setRate, play, pause, resume, stop }
}
