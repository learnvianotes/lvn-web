/* ============================================================
   useStudyTime — for signed-in learners, logs the time actually
   spent on a study page (tab visible and reader active in the
   last 45 s, or listening to read-aloud).

   Opening a page is not studying it. The page enters the study
   history (and counts toward the streak) only once the reader
   has engaged with it:
     • reached the end of the page after at least 20 s of active
       reading, or
     • spent 60 s of active reading on it.
   Until then the time is held back; once engaged it's saved in
   full, then every 15 s and when leaving the page.
   ============================================================ */

import { useEffect, type RefObject } from 'react'
import { track } from '@/features/telemetry/track'
import { addStudyTime, recordVisit } from './activity'

const IDLE_AFTER_MS = 45_000
const SAVE_EVERY_S = 15
/** Active seconds on a page that count as having studied it. */
export const ENGAGED_SECONDS = 60
/** Active seconds that count, when the reader has also reached the end of the page. */
export const ENGAGED_AT_END_SECONDS = 20

interface Options {
  subjectId: string
  topicId: string
  title: string
  subjectTitle: string
  enabled: boolean
  /** element after the last line of the page — reaching it (with some reading time) counts as engaged */
  endRef?: RefObject<HTMLElement | null>
}

export function useStudyTime({ subjectId, topicId, title, subjectTitle, enabled, endRef }: Options) {
  useEffect(() => {
    if (!enabled) return
    const key = `${subjectId}/${topicId}`
    track('topic_open', { s: subjectId, k: topicId, l: title })
    let active = 0
    let pending = 0
    let reachedEnd = false
    let engaged = false
    let lastActive = Date.now()

    const save = () => {
      if (!engaged || !pending) return
      addStudyTime(key, title, subjectTitle, pending)
      track('topic_time', { s: subjectId, k: topicId, v: pending })
      pending = 0
    }
    const checkEngaged = () => {
      if (engaged) return
      if (active >= ENGAGED_SECONDS || (reachedEnd && active >= ENGAGED_AT_END_SECONDS)) {
        engaged = true
        recordVisit(key, title, subjectTitle)
        track('topic_view', { s: subjectId, k: topicId, l: title, v: active })
        save()
      }
    }
    const markActive = () => { lastActive = Date.now() }
    const events = ['scroll', 'wheel', 'touchmove', 'keydown', 'pointerdown', 'mousemove'] as const
    events.forEach((e) => window.addEventListener(e, markActive, { passive: true }))
    const onHide = () => { if (document.visibilityState === 'hidden') save() }
    document.addEventListener('visibilitychange', onHide)

    const timer = window.setInterval(() => {
      const listening = document.documentElement.dataset.speaking === 'true'
      if (document.visibilityState === 'visible' && (listening || Date.now() - lastActive < IDLE_AFTER_MS)) {
        active++
        pending++
        checkEngaged()
        if (pending >= SAVE_EVERY_S) save()
      }
    }, 1000)

    // The end marker may mount after the content loads, so look for it until it's there.
    let observer: IntersectionObserver | undefined
    let watchTimer: number | undefined
    const watchEnd = () => {
      const el = endRef?.current
      if (!el) return false
      observer = new IntersectionObserver((entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          reachedEnd = true
          checkEngaged()
        }
      })
      observer.observe(el)
      return true
    }
    if (endRef && !watchEnd()) watchTimer = window.setInterval(() => { if (watchEnd()) window.clearInterval(watchTimer) }, 1000)

    return () => {
      window.clearInterval(timer)
      window.clearInterval(watchTimer)
      observer?.disconnect()
      events.forEach((e) => window.removeEventListener(e, markActive))
      document.removeEventListener('visibilitychange', onHide)
      save()
    }
  }, [subjectId, topicId, title, subjectTitle, enabled, endRef])
}
