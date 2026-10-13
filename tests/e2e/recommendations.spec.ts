import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Recommendations (lvn-backend ADR-0071): each item with why, leading to the note or the notes on the topic; one can be
 * set aside.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const NOTE = '01920000-0000-7000-8000-00000000a001'
const TOPIC = '01920000-0000-7000-8000-0000000070a1'
const week = ['COUNTED', 'MISSED', 'REST', 'TODAY', 'AHEAD', 'AHEAD', 'AHEAD'].map((status, i) => ({ __typename: 'RhythmDay', day: `2026-10-${12 + i}`, weekday: i + 1, planned: [1, 2, 4, 6].includes(i + 1), counted: status === 'COUNTED', status }))
const rhythm = {
  __typename: 'Rhythm', timeZone: 'UTC', plannedDays: [1, 2, 4, 6], target: 4, countedDays: 1, met: false, week,
  today: { __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 0, reviews: 0, counted: false, comeback: false, cameBack: false, items: [] },
  weeksThisTerm: 0, weeksAllTime: 0, countedDaysAllTime: 1, pauses: [], pauseDaysLeft: 14, suggestion: null, shareRhythm: false,
}
const rec = (over: Record<string, unknown>) => ({ __typename: 'Recommendation', resource: null, score: 50, noteTitle: null, topicKey: null, topicTitle: null, note: null, topic: null, ...over })

test('shows recommendations with why, leading to the note or the topic’s notes, and sets one aside', async ({ page }) => {
  let items = [
    rec({ kind: 'EXAM_TOPIC', score: 95, reason: 'On your plan for Operating Systems, in 5 days', topicKey: `topic:${TOPIC}`, topicTitle: 'Paging', topic: { __typename: 'Topic', id: TOPIC } }),
    rec({ kind: 'CONTINUE_NOTE', score: 55, reason: 'You were reading this on Monday, 12 October', noteTitle: 'Dijkstra', note: { __typename: 'Note', id: NOTE } }),
  ]
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm }),
    Recommendations: () => ({ recommendations: items }),
    DismissRecommendation: () => {
      items = items.slice(1)
      return { dismissRecommendation: { __typename: 'OkPayload', ok: true, userErrors: [] } }
    },
  }, viewerExtras)
  await page.goto('/rhythm')
  const box = page.getByRole('region', { name: 'Recommended for you' })
  await expect(box.getByText('On your plan for Operating Systems, in 5 days')).toBeVisible()
  await expect(box.getByRole('link', { name: /Paging/ })).toHaveAttribute('href', `/search?topic=${TOPIC}&topicTitle=Paging`)
  await expect(box.getByRole('link', { name: /Dijkstra/ })).toHaveAttribute('href', `/notes/${NOTE}`)
  await box.getByRole('button', { name: 'Not now: Paging' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'DismissRecommendation')?.variables).toEqual({ input: { kind: 'EXAM_TOPIC', entityId: `topic:${TOPIC}` } })
  await expect(box.getByText('Paging')).toHaveCount(0)
})

test('says how recommendations come when there are none', async ({ page }) => {
  await mockApi(page, { Rhythm: () => ({ rhythm }), Recommendations: () => ({ recommendations: [] }) }, viewerExtras)
  await page.goto('/rhythm')
  await expect(page.getByRole('region', { name: 'Recommended for you' }).getByText(/Nothing to recommend yet/)).toBeVisible()
})
