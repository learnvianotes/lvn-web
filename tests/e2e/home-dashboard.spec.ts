import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/** Home for a signed-in learner (P6h): today's ring and week, the note to continue, the next exam, recommendations. */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const NOTE = '01920000-0000-7000-8000-00000000a001'
const EXAM = '01920000-0000-7000-8000-0000000e0001'
const week = ['COUNTED', 'MISSED', 'REST', 'TODAY', 'AHEAD', 'AHEAD', 'AHEAD'].map((status, i) => ({ __typename: 'RhythmDay', day: `2026-10-${12 + i}`, weekday: i + 1, planned: [1, 2, 4, 6].includes(i + 1), counted: status === 'COUNTED', status }))
const rhythm = {
  __typename: 'Rhythm', timeZone: 'UTC', plannedDays: [1, 2, 4, 6], target: 4, countedDays: 1, met: false, week,
  today: { __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 300, reviews: 0, counted: false, comeback: false, cameBack: false, items: [] },
  weeksThisTerm: 2, weeksAllTime: 5, countedDaysAllTime: 30, pauses: [], pauseDaysLeft: 14, suggestion: null, shareRhythm: false,
}
const exam = { __typename: 'Exam', id: EXAM, name: 'Operating Systems', date: '2026-10-25', daysLeft: 10, past: false, readiness: 34, target: 80, targetToday: 40, topics: [], tasks: [] }
const continueRec = { __typename: 'Recommendation', resource: null, kind: 'CONTINUE_NOTE', score: 55, reason: 'You were reading this on Monday, 12 October', noteTitle: 'Dijkstra', topicKey: null, topicTitle: null, note: { __typename: 'Note', id: NOTE }, topic: null }

test('Home greets the learner and shows today, the week, the note to continue, the next exam and recommendations', async ({ page }) => {
  await mockApi(page, { Rhythm: () => ({ rhythm }), Exams: () => ({ exams: [exam] }), Recommendations: () => ({ recommendations: [continueRec] }) }, viewerExtras)
  await page.goto('/home')
  await expect(page.getByRole('heading', { name: /^Good (morning|afternoon|evening), Asha!/ })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Today' }).getByRole('img', { name: /50% of the way/ })).toBeVisible()
  // One region per name: Today and This week are Rhythm's own (no wrapper named Today around them).
  await expect(page.getByRole('region', { name: 'Today', exact: true })).toHaveCount(1)
  await expect(page.getByRole('region', { name: 'This week' }).getByText('1 of 4 days this week')).toBeVisible()
  await expect(page.getByRole('region', { name: 'Continue learning' }).getByRole('link', { name: /Dijkstra/ })).toHaveAttribute('href', `/notes/${NOTE}`)
  await expect(page.getByRole('region', { name: 'Continue learning' }).getByText('You were reading this on Monday, 12 October')).toBeVisible()
  const nextExam = page.getByRole('region', { name: 'Next exam' })
  await expect(nextExam.getByText('Operating Systems')).toBeVisible()
  await expect(nextExam.getByRole('link', { name: 'View Plan' })).toHaveAttribute('href', `/exams/${exam.id}`)
  await expect(page.getByRole('region', { name: 'Weekly goal' }).getByText('1 / 4 days')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Open Rhythm' })).toHaveAttribute('href', '/rhythm')
})

test('Home offers to add an exam when there is none; the signed-in landing card opens Home', async ({ page }) => {
  await mockApi(page, { Rhythm: () => ({ rhythm }), Exams: () => ({ exams: [] }), Recommendations: () => ({ recommendations: [] }) }, viewerExtras)
  await page.goto('/')
  await page.getByRole('link', { name: 'Open your home' }).click()
  await expect(page).toHaveURL(/\/home$/)
  await expect(page.getByText(/No exam coming up/)).toBeVisible()
  await expect(page.getByRole('region', { name: 'Next exam' }).getByRole('link', { name: 'Add an exam' })).toHaveAttribute('href', '/exams')
})
