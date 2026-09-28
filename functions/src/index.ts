/* ============================================================
   LEARNVIANOTES BACKEND — Cloud Functions (Firebase, Node 22)

   cleanupUserData    auth trigger: when an account is deleted,
                      delete everything under users/{uid}
                      (the app also does this; this catches
                      deletions made from the console or admin SDK)
   rollupStudyStats   daily job: aggregates yesterday's learner
                      events into topicStats/* and trending/current
                      — the first building block for recommendations

   Requires the Blaze (pay-as-you-go) plan to deploy. The app
   works without these functions; they add server-side cleanup
   and aggregates. Document shapes: ../schema/firestore.ts
   ============================================================ */

import { initializeApp } from 'firebase-admin/app'
import { FieldValue, getFirestore } from 'firebase-admin/firestore'
import * as functionsV1 from 'firebase-functions/v1'
import { setGlobalOptions } from 'firebase-functions/v2'
import { logger } from 'firebase-functions'
import { onSchedule } from 'firebase-functions/v2/scheduler'
import { docId, type EventBatchDoc, type TopicStatsDoc, type TrendingDoc } from './schema/firestore.js'

/** Keep functions next to the Firestore database (change if yours is elsewhere). */
const REGION = 'asia-south1'
const TIME_ZONE = 'Asia/Kolkata'
const KEEP_DAILY = 30
const TRENDING_DAYS = 7
const TRENDING_SIZE = 20

setGlobalOptions({ region: REGION, maxInstances: 5 })
initializeApp()
const db = getFirestore()

/* ── account deletion ────────────────────────────────────── */

export const cleanupUserData = functionsV1
  .region(REGION)
  .auth.user()
  .onDelete(async (user) => {
    await db.recursiveDelete(db.doc(`users/${user.uid}`))
    logger.info('Deleted data for removed account', { uid: user.uid })
  })

/* ── daily aggregates ────────────────────────────────────── */

function dayKey(d: Date) {
  // YYYY-MM-DD in the app's time zone (events are keyed by the learner's local day).
  return new Intl.DateTimeFormat('en-CA', { timeZone: TIME_ZONE, year: 'numeric', month: '2-digit', day: '2-digit' }).format(d)
}

interface Acc { title: string; subject: string; views: number; seconds: number; completes: number; users: Set<string> }

export const rollupStudyStats = onSchedule({ schedule: 'every day 03:30', timeZone: TIME_ZONE }, async () => {
  const day = dayKey(new Date(Date.now() - 24 * 60 * 60 * 1000))
  const marker = db.doc(`rollups/${day}`)
  if ((await marker.get()).exists) {
    logger.info('Already rolled up', { day })
    return
  }

  // 1. Aggregate the day's events per topic.
  const snap = await db.collectionGroup('events').where('day', '==', day).get()
  const acc = new Map<string, Acc>()
  for (const doc of snap.docs) {
    const uid = doc.ref.parent.parent?.id ?? ''
    const batch = doc.data() as EventBatchDoc
    for (const e of batch.events ?? []) {
      if (!e.s || !e.k) continue
      const key = `${e.s}/${e.k}`
      const a = acc.get(key) ?? { title: '', subject: e.s, views: 0, seconds: 0, completes: 0, users: new Set<string>() }
      if (e.type === 'topic_view') { a.views++; if (e.l) a.title = e.l }
      else if (e.type === 'topic_time') a.seconds += Math.max(0, Math.min(e.v ?? 0, 4 * 60 * 60))
      else if (e.type === 'topic_complete') a.completes++
      else continue
      a.users.add(uid)
      acc.set(key, a)
    }
  }

  // 2. Update per-topic stats (keep the last KEEP_DAILY days of daily numbers).
  const cutoff = dayKey(new Date(Date.now() - KEEP_DAILY * 24 * 60 * 60 * 1000))
  const entries = [...acc.entries()]
  for (let i = 0; i < entries.length; i += 400) {
    const writes = db.batch()
    const refs = entries.slice(i, i + 400).map(([key]) => db.doc(`topicStats/${docId(key)}`))
    const existing = refs.length ? await db.getAll(...refs) : []
    entries.slice(i, i + 400).forEach(([key, a], j) => {
      const prev = existing[j].data() as TopicStatsDoc | undefined
      const daily = Object.fromEntries(Object.entries(prev?.daily ?? {}).filter(([d]) => d > cutoff))
      daily[day] = { views: a.views, seconds: a.seconds, users: a.users.size }
      writes.set(refs[j], {
        key,
        title: a.title || prev?.title || key,
        subject: a.subject,
        views: FieldValue.increment(a.views),
        seconds: FieldValue.increment(a.seconds),
        completes: FieldValue.increment(a.completes),
        daily,
        updatedAt: Date.now(),
      }, { merge: true })
    })
    await writes.commit()
  }

  // 3. Trending: most studied topics over the last TRENDING_DAYS days.
  const since = dayKey(new Date(Date.now() - TRENDING_DAYS * 24 * 60 * 60 * 1000))
  const recent = await db.collection('topicStats').where('updatedAt', '>', Date.now() - TRENDING_DAYS * 24 * 60 * 60 * 1000).get()
  const topics = recent.docs
    .map((d) => {
      const s = d.data() as TopicStatsDoc
      let score = 0
      for (const [k, v] of Object.entries(s.daily ?? {})) if (k > since) score += v.users * 5 + v.views + v.seconds / 300
      return { key: s.key, title: s.title, subject: s.subject, score: Math.round(score) }
    })
    .filter((t) => t.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, TRENDING_SIZE)
  const trending: TrendingDoc = { topics, updatedAt: Date.now() }
  await db.doc('trending/current').set(trending)

  await marker.set({ day, events: snap.size, topics: acc.size, at: Date.now() })
  logger.info('Rolled up study stats', { day, batches: snap.size, topics: acc.size })
})
