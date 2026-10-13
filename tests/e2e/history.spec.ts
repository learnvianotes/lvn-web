import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Learning history (lvn-backend ADR-0067): days newest first with learning and reading time, reviews and quiz answers;
 * Rhythm days say so and the others are just days; topics by name (a /core topic by its key); notes still readable
 * link to them; older days on request; the time zone can be changed.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const NOTE = '01920000-0000-7000-8000-00000000a001'
const TOPIC = '01920000-0000-7000-8000-0000000070a1'
const day = (over: Record<string, unknown>) => ({ __typename: 'LearningHistoryDay', learningSeconds: 0, readingSeconds: 0, reviews: 0, quizAnswers: 0, counted: false, topics: [], notes: [], ...over })
const page1 = {
  __typename: 'LearningHistory',
  timeZone: 'Asia/Kolkata',
  nextBefore: '2026-10-10',
  days: [
    day({
      day: '2026-10-12',
      learningSeconds: 660,
      readingSeconds: 300,
      reviews: 12,
      counted: true,
      topics: [
        { __typename: 'LearningHistoryTopic', key: `topic:${TOPIC}`, seconds: 660, topic: { __typename: 'Topic', id: TOPIC, title: 'Graphs' } },
        { __typename: 'LearningHistoryTopic', key: 'core:dsa-basics/arrays', seconds: 300, topic: null },
      ],
      notes: [{ __typename: 'Note', id: NOTE, title: 'Dijkstra' }, null],
    }),
    day({ day: '2026-10-10', quizAnswers: 5 }),
  ],
}
const page2 = { __typename: 'LearningHistory', timeZone: 'Asia/Kolkata', nextBefore: null, days: [day({ day: '2026-10-02', readingSeconds: 1200 })] }

test('shows days newest first, what counts for Rhythm, topics and the notes still readable; older days on request', async ({ page }) => {
  const calls = await mockApi(page, { LearningHistory: (v) => ({ learningHistory: v.before ? page2 : page1 }) }, viewerExtras)
  await page.goto('/profile')
  await page.getByRole('link', { name: /Learning history/ }).click()
  await expect(page).toHaveURL(/\/history$/)
  const first = page.getByRole('article', { name: /Monday.*12/ })
  await expect(first.getByText('Counts for your Rhythm')).toBeVisible()
  await expect(first.getByText('Learning 11 min · Reading 5 min · 12 cards reviewed')).toBeVisible()
  await expect(first.getByRole('list', { name: 'Topics' }).getByText('Graphs · 11 min')).toBeVisible()
  await expect(first.getByRole('list', { name: 'Topics' }).getByText('dsa basics / arrays · 5 min')).toBeVisible()
  await expect(first.getByRole('link', { name: 'Dijkstra' })).toHaveAttribute('href', `/notes/${NOTE}`)
  const second = page.getByRole('article', { name: /Saturday.*10/ })
  await expect(second.getByText('5 quiz answers')).toBeVisible()
  await expect(second.getByText('Counts for your Rhythm')).toHaveCount(0)
  await page.getByRole('button', { name: 'Older days' }).click()
  await expect(page.getByRole('article', { name: /Friday.*2/ })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Older days' })).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'LearningHistory').at(-1)!.variables).toEqual({ before: '2026-10-10', days: 14 })
})

test('says days start at 4 in the person’s zone, and changes the zone', async ({ page }) => {
  const calls = await mockApi(page, {
    LearningHistory: () => ({ learningHistory: { ...page1, nextBefore: null, days: [] } }),
    SetLearningTimeZone: () => ({ setLearningTimeZone: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  }, viewerExtras)
  await page.goto('/history')
  await expect(page.getByText(/Nothing here yet/)).toBeVisible()
  await expect(page.getByText('Days are counted in Asia/Kolkata and start at 4 in the morning.')).toBeVisible()
  await page.getByRole('button', { name: 'Change' }).click()
  await page.getByLabel('Time zone').selectOption('Europe/London')
  await page.getByRole('button', { name: 'Save' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'SetLearningTimeZone')?.variables).toEqual({ input: { timeZone: 'Europe/London' } })
})
