/* ============================================================
   useReadCompletion — marks a topic complete only when the reader
   has reached the end AND spent real reading time on it.

   Required time scales with the text length: 40 % of a normal
   reading pace (230 words/min), between 20 s and 4 min (never less
   than what useStudyTime needs to put the page in the history). Time only
   counts while the tab is visible and the reader is active
   (scrolled / touched / typed in the last 45 s), so flicking to
   the bottom doesn't count.
   ============================================================ */

import { useEffect, useRef, type RefObject } from 'react'
import { completeTopic } from '@/features/progress/store'
import { ENGAGED_AT_END_SECONDS } from '@/features/progress/useStudyTime'

const WORDS_PER_MINUTE = 230
const SHARE_OF_READING_TIME = 0.4
const IDLE_AFTER_MS = 45_000

export function requiredReadingSeconds(text: string) {
  const words = text.trim().split(/\s+/).filter(Boolean).length
  const seconds = (words / WORDS_PER_MINUTE) * 60 * SHARE_OF_READING_TIME
  return Math.round(Math.min(240, Math.max(ENGAGED_AT_END_SECONDS, seconds)))
}

interface Options {
  subjectId: string
  topicId: string
  /** plain text of the topic (used to size the required time) */
  text: string | undefined
  done: boolean
  /** element placed after the last line of the topic */
  endRef: RefObject<HTMLElement | null>
}

export function useReadCompletion({ subjectId, topicId, text, done, endRef }: Options) {
  const seconds = useRef(0)
  const reachedEnd = useRef(false)

  useEffect(() => {
    if (done || !text) return
    const required = requiredReadingSeconds(text)
    seconds.current = 0
    reachedEnd.current = false
    let lastActive = Date.now()

    const check = () => {
      if (reachedEnd.current && seconds.current >= required) completeTopic(subjectId, topicId)
    }
    const markActive = () => { lastActive = Date.now() }
    const events = ['scroll', 'wheel', 'touchmove', 'keydown', 'pointerdown', 'mousemove'] as const
    events.forEach((e) => window.addEventListener(e, markActive, { passive: true }))

    const timer = window.setInterval(() => {
      if (document.visibilityState === 'visible' && Date.now() - lastActive < IDLE_AFTER_MS) {
        seconds.current += 1
        check()
      }
    }, 1000)

    const observer = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        reachedEnd.current = true
        check()
      }
    })
    if (endRef.current) observer.observe(endRef.current)

    return () => {
      events.forEach((e) => window.removeEventListener(e, markActive))
      window.clearInterval(timer)
      observer.disconnect()
    }
  }, [subjectId, topicId, text, done, endRef])
}
