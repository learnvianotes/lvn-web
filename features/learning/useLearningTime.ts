'use client'

import { useEffect } from 'react'
import type { TimeSpentActivity } from '@/lib/contracts/domain/enums'
import { flush, track } from '@/lib/learning'

/** Visible time shorter than this is a glance, not reading. */
const MIN_MS = 5_000
/** Long sessions are reported in pieces, so a closed laptop loses at most this much. */
const PIECE_MS = 5 * 60_000

/**
 * Time with something open, while the page is visible (lvn-backend ADR-0067): `opened` once (NOTE_OPENED,
 * TOPIC_VIEWED), then TIME_SPENT pieces of the visible time with their activity. Reading is history only; Rhythm
 * counts only learning activities (ADR-0030).
 */
export function useLearningTime(subject: { entityType: string; entityId: string; topicKeys?: string[] } | null, opened: 'NOTE_OPENED' | 'TOPIC_VIEWED' | null, activity: TimeSpentActivity = 'READING') {
  const entityId = subject?.entityId
  const topics = subject?.topicKeys?.join(',') ?? ''
  useEffect(() => {
    if (!subject) return
    const fields = { entityType: subject.entityType, entityId: subject.entityId, topicKeys: subject.topicKeys?.length ? subject.topicKeys.slice(0, 10) : undefined }
    if (opened) track(opened, fields)
    let since: number | null = document.visibilityState === 'visible' ? Date.now() : null
    let total = 0
    const pause = () => {
      if (since !== null) total += Date.now() - since
      since = null
    }
    const report = () => {
      pause()
      if (total >= MIN_MS) track('TIME_SPENT', { ...fields, durationMs: total, metadata: { activity } })
      total = 0
    }
    const onVisibility = () => {
      if (document.visibilityState === 'visible') since ??= Date.now()
      else {
        report()
        void flush({ keepalive: true })
      }
    }
    const every = setInterval(() => {
      report()
      if (document.visibilityState === 'visible') since = Date.now()
    }, PIECE_MS)
    document.addEventListener('visibilitychange', onVisibility)
    return () => {
      clearInterval(every)
      document.removeEventListener('visibilitychange', onVisibility)
      report()
    }
    // The subject is named by its id and topics; a new object for the same note is the same subject.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [entityId, topics, opened, activity])
}
