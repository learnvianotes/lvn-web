import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Rhythm (lvn-backend ADR-0030, ADR-0069): today's ring and what is left for today to count, a comeback after a missed
 * planned day, the week from Monday to Sunday (never red: a missed day is "not counted"), counters, the plan of 3–6
 * days, and pauses.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const PAUSE = '01920000-0000-7000-8000-0000000000a1'
const statuses = ['COUNTED', 'MISSED', 'REST', 'TODAY', 'AHEAD', 'AHEAD', 'AHEAD'] as const
const plan = [1, 2, 4, 6]
const rhythm = (over: Record<string, unknown> = {}, today: Record<string, unknown> = {}) => ({
  __typename: 'Rhythm',
  timeZone: 'Asia/Kolkata',
  plannedDays: plan,
  target: 4,
  countedDays: 1,
  met: false,
  week: statuses.map((status, i) => ({ __typename: 'RhythmDay', day: `2026-10-${String(12 + i).padStart(2, '0')}`, weekday: i + 1, planned: plan.includes(i + 1), counted: status === 'COUNTED', status })),
  today: { __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 240, reviews: 3, counted: false, comeback: true, cameBack: false, items: [{ __typename: 'RhythmItem', kind: 'REVIEWS', done: 3, total: 8, title: null, topicKey: null }], ...today },
  weeksThisTerm: 9,
  weeksAllTime: 23,
  countedDaysAllTime: 140,
  pauses: [],
  pauseDaysLeft: 14,
  suggestion: null, shareRhythm: false,
  ...over,
})
const ok = (name: string, userErrors: unknown[] = []) => ({ [name]: { __typename: 'OkPayload', ok: !userErrors.length, userErrors } })

test('shows today’s ring with what is left, a comeback, the week and the counters', async ({ page }) => {
  await mockApi(page, { Rhythm: () => ({ rhythm: rhythm() }) }, viewerExtras)
  await page.goto('/profile')
  await page.getByRole('link', { name: /^Rhythm/ }).click()
  await expect(page).toHaveURL(/\/rhythm$/)
  const today = page.getByRole('region', { name: 'Today' })
  await expect(today.getByRole('img', { name: 'Today’s ring: 40% of the way to a counted day' })).toBeVisible()
  await expect(today.getByText('Comeback day: the same 10 minutes put you back on rhythm.')).toBeVisible()
  await expect(today.getByText('6 more learning minutes, or 7 more reviews, and today counts.')).toBeVisible()
  await expect(today.getByText('Reviews: 3 of 8')).toBeVisible()
  await expect(today.getByRole('link', { name: 'Review now' })).toHaveAttribute('href', '/review')
  const week = page.getByRole('region', { name: 'This week' })
  await expect(week.getByRole('listitem', { name: 'Monday: counted, planned' })).toBeVisible()
  await expect(week.getByRole('listitem', { name: 'Tuesday: planned, not counted' })).toBeVisible()
  await expect(week.getByRole('listitem', { name: 'Wednesday: rest day' })).toBeVisible()
  await expect(week.getByRole('listitem', { name: 'Thursday: today, planned' })).toBeVisible()
  await expect(week.getByRole('listitem', { name: 'Sunday: rest day' })).toBeVisible()
  await expect(week.getByText('1 of 4 days this week')).toBeVisible()
  const counters = page.getByRole('region', { name: 'Counters' })
  await expect(counters.getByText('Rhythm weeks this term')).toBeVisible()
  await expect(counters.getByText('140')).toBeVisible()
  await expect(page.getByText(/lost|streak/i)).toHaveCount(1) // only the lead: "not a streak … nothing is ever lost"
  await expect(page.getByText('Days are counted in Asia/Kolkata and start at 4 in the morning.')).toBeVisible()
})

test('a counted comeback says back on rhythm, and a full week says met', async ({ page }) => {
  await mockApi(page, { Rhythm: () => ({ rhythm: rhythm({ met: true, countedDays: 4 }, { learningSeconds: 700, counted: true, comeback: false, cameBack: true }) }) }, viewerExtras)
  await page.goto('/rhythm')
  const today = page.getByRole('region', { name: 'Today' })
  await expect(today.getByText('Today counts')).toBeVisible()
  await expect(today.getByText('Back on rhythm.')).toBeVisible()
  await expect(today.getByText(/and today counts/)).toHaveCount(0)
  await expect(today.getByRole('img', { name: /100%/ })).toBeVisible()
  await expect(page.getByRole('region', { name: 'This week' }).getByText('Week met')).toBeVisible()
})

test('changes the planned days, 3 to 6 of them', async ({ page }) => {
  let current = rhythm()
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm: current }),
    SetRhythmPlan: (v) => {
      const days = (v as { input: { plannedDays: number[] } }).input.plannedDays
      current = rhythm({ plannedDays: days, target: days.length })
      return ok('setRhythmPlan')
    },
  }, viewerExtras)
  await page.goto('/rhythm')
  const planBox = page.getByRole('region', { name: 'Your planned days' })
  const save = planBox.getByRole('button', { name: 'Save days' })
  await expect(planBox.getByRole('button', { name: 'Monday' })).toHaveAttribute('aria-pressed', 'true')
  await expect(save).toBeDisabled()
  await planBox.getByRole('button', { name: 'Tuesday' }).click()
  await planBox.getByRole('button', { name: 'Thursday' }).click()
  await expect(save).toBeDisabled() // two days are too few
  await planBox.getByRole('button', { name: 'Wednesday' }).click()
  await planBox.getByRole('button', { name: 'Friday' }).click()
  await save.click()
  await expect.poll(() => calls.find((c) => c.op === 'SetRhythmPlan')?.variables).toEqual({ input: { plannedDays: [1, 3, 5, 6] } })
  await expect(planBox.getByRole('status')).toHaveText('Saved. This week now aims for 4 days.')
})

test('pauses Rhythm, says why one cannot, and ends a pause', async ({ page }) => {
  let current = rhythm()
  let refuse = true
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm: current }),
    PauseRhythm: (v) => {
      if (refuse) {
        refuse = false
        return ok('pauseRhythm', [{ __typename: 'UserError', message: 'Rhythm can pause for 14 days a term; this would go past that.', code: 'VALIDATION' }])
      }
      const input = (v as { input: { from: string; to: string; reason: string } }).input
      current = rhythm({ pauses: [{ __typename: 'RhythmPause', id: PAUSE, ...input, active: true }], pauseDaysLeft: 11, target: 3 })
      return ok('pauseRhythm')
    },
    EndRhythmPause: () => {
      current = rhythm()
      return ok('endRhythmPause')
    },
  }, viewerExtras)
  await page.goto('/rhythm')
  const pauses = page.getByRole('region', { name: 'Pauses' })
  await expect(pauses.getByText(/14 of 14 pause days left this term/)).toBeVisible()
  await pauses.getByRole('button', { name: 'Pause Rhythm' }).click()
  await pauses.getByLabel('To').fill('2026-11-10')
  await pauses.getByLabel('Why').selectOption('TRAVEL')
  await pauses.getByRole('button', { name: 'Pause', exact: true }).click()
  await expect(pauses.getByText('Rhythm can pause for 14 days a term; this would go past that.')).toBeVisible()
  await pauses.getByLabel('To').fill('2026-10-17')
  await pauses.getByRole('button', { name: 'Pause', exact: true }).click()
  await expect.poll(() => calls.filter((c) => c.op === 'PauseRhythm').at(-1)?.variables).toEqual({ input: { from: '2026-10-15', to: '2026-10-17', reason: 'TRAVEL' } })
  await expect(pauses.getByText('Travel: Oct 15 to Oct 17')).toBeVisible()
  await expect(pauses.getByText('Paused now')).toBeVisible()
  await expect(pauses.getByText(/11 of 14 pause days left/)).toBeVisible()
  await pauses.getByRole('button', { name: 'Cancel the pause' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'EndRhythmPause')?.variables).toEqual({ input: { id: PAUSE } })
  await expect(pauses.getByText('No pauses.')).toBeVisible()
})
