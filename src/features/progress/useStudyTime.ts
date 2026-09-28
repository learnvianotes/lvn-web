/* ============================================================
   useStudyTime — for signed-in learners, logs a visit and the
   time actually spent on a study page (tab visible and reader
   active in the last 45 s, or listening to read-aloud) into the
   day's activity log and the event log. Saved every 15 s and
   when leaving the page.
   ============================================================ */

import { useEffect } from 'react'
import { track } from '@/features/telemetry/track'
import { addStudyTime, recordVisit } from './activity'

const IDLE_AFTER_MS = 45_000
const SAVE_EVERY_S = 15

interface Options {
  subjectId: string
  topicId: string
  title: string
  subjectTitle: string
  enabled: boolean
}

export function useStudyTime({ subjectId, topicId, title, subjectTitle, enabled }: Options) {
  useEffect(() => {
    if (!enabled) return
    const key = `${subjectId}/${topicId}`
    recordVisit(key, title, subjectTitle)
    track('topic_view', { s: subjectId, k: topicId, l: title })
    let pending = 0
    let lastActive = Date.now()
    const save = () => {
      if (!pending) return
      addStudyTime(key, title, subjectTitle, pending)
      track('topic_time', { s: subjectId, k: topicId, v: pending })
      pending = 0
    }
    const markActive = () => { lastActive = Date.now() }
    const events = ['scroll', 'wheel', 'touchmove', 'keydown', 'pointerdown', 'mousemove'] as const
    events.forEach((e) => window.addEventListener(e, markActive, { passive: true }))
    const onHide = () => { if (document.visibilityState === 'hidden') save() }
    document.addEventListener('visibilitychange', onHide)

    const timer = window.setInterval(() => {
      const listening = document.documentElement.dataset.speaking === 'true'
      if (document.visibilityState === 'visible' && (listening || Date.now() - lastActive < IDLE_AFTER_MS)) {
        pending++
        if (pending >= SAVE_EVERY_S) save()
      }
    }, 1000)

    return () => {
      window.clearInterval(timer)
      events.forEach((e) => window.removeEventListener(e, markActive))
      document.removeEventListener('visibilitychange', onHide)
      save()
    }
  }, [subjectId, topicId, title, subjectTitle, enabled])
}
