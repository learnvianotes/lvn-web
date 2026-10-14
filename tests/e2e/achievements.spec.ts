import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Achievements, level and points (lvn-backend ADR-0080): the person's page shows their level and how far the next one
 * is, the achievements they earned, their points history (each line opening what earned it) and, for an adult, the
 * choice to show them on their profile; a minor reads that they stay private. The account links to it.
 */
const ME = '01920000-0000-7000-8000-00000000aaaa'
const NOTE = '01920000-0000-7000-8000-00000000c0c1'
const RES = '01920000-0000-7000-8000-00000000c0c2'
const badge = (id: string, kind: string, title: string) => ({ __typename: 'Achievement', id, kind, tier: 1, title, description: `${title}, explained`, subjectTitle: null, earnedAt: new Date().toISOString() })
const entry = (id: string, delta: number, rule: string, sourceType: string, sourceId: string) => ({ __typename: 'PointsEntry', id, delta, rule, sourceType, sourceId, subjectTitle: sourceType === 'NOTE' ? 'Data Structures' : null, createdAt: new Date().toISOString() })
const mine = (achievements: unknown[], settings: { showAchievements: boolean; canShow: boolean }) => () => ({
  viewer: { __typename: 'User', id: ME, achievements, contribution: { __typename: 'Contribution', points: 30, level: 'NEWCOMER', nextLevelAt: 50 } },
  achievementSettings: { __typename: 'AchievementSettings', ...settings },
})
const history = () => ({
  myPoints: {
    __typename: 'PointsEntryConnection',
    edges: [entry('01920000-0000-7000-8000-0000000000e1', 10, 'RESOURCE_APPROVED', 'RESOURCE', RES), entry('01920000-0000-7000-8000-0000000000e2', -1, 'REACTION', 'NOTE', NOTE), entry('01920000-0000-7000-8000-0000000000e3', 1, 'REACTION', 'NOTE', NOTE)].map((node, i) => ({ __typename: 'PointsEntryEdge', cursor: String(i), node })),
    pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null },
  },
})

test('an adult sees their level, achievements and points, and chooses to show them on their profile', async ({ page }) => {
  let shown = false
  const calls = await mockApi(page, {
    MyAchievements: (v) => mine([badge('01920000-0000-7000-8000-0000000000a1', 'QUIZ_MASTER', 'Quiz master'), badge('01920000-0000-7000-8000-0000000000a2', 'RHYTHM_WEEKS', '4 Rhythm weeks')], { showAchievements: shown, canShow: true })(v),
    MyPoints: history,
    SetAchievementsShown: (v) => ((shown = v.show as boolean), { setAchievementsShown: { __typename: 'AchievementSettingsPayload', settings: { __typename: 'AchievementSettings', showAchievements: shown, canShow: true }, userErrors: [] } }),
  })
  await page.goto('/achievements')
  await expect(page.getByRole('heading', { name: 'Achievements', level: 1 })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Newcomer' })).toBeVisible()
  await expect(page.getByText('30 points')).toBeVisible()
  await expect(page.getByRole('progressbar', { name: '20 more points to the next level' })).toHaveAttribute('aria-valuenow', '60')
  const earned = page.getByRole('region', { name: 'Earned' })
  await expect(earned.getByRole('listitem')).toHaveCount(2)
  await expect(earned.getByText('Quiz master', { exact: true })).toBeVisible()

  const lines = page.getByRole('region', { name: 'Points history' })
  await expect(lines.getByRole('link', { name: 'Your resource was approved' })).toHaveAttribute('href', `/resources/${RES}`)
  await expect(lines.getByRole('link', { name: /A reaction on your note · Data Structures/ })).toHaveAttribute('href', `/notes/${NOTE}`)
  await expect(lines.getByText('+10')).toBeVisible()
  await expect(lines.getByText('-1', { exact: true })).toBeVisible()

  const show = page.getByRole('checkbox', { name: /Show my achievements and level on my profile/ })
  await expect(show).not.toBeChecked()
  await show.check()
  await expect(show).toBeChecked()
  expect(calls.find((c) => c.op === 'SetAchievementsShown')?.variables).toEqual({ show: true })
})

test('a minor reads that their achievements stay private; with none yet, the page says how to earn them', async ({ page }) => {
  await mockApi(page, { MyAchievements: mine([], { showAchievements: false, canShow: false }), MyPoints: () => ({ myPoints: { __typename: 'PointsEntryConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }) })
  await page.goto('/achievements')
  await expect(page.getByText('Your achievements stay private until you are 18: only you see them.')).toBeVisible()
  await expect(page.getByRole('checkbox')).toHaveCount(0)
  const earned = page.getByRole('region', { name: 'Earned' })
  await expect(earned.getByRole('link', { name: 'Review cards' })).toHaveAttribute('href', '/review')
  await expect(earned.getByRole('link', { name: 'Plan an exam' })).toHaveAttribute('href', '/exams')
  await expect(earned.getByRole('link', { name: 'Your Rhythm' })).toHaveAttribute('href', '/rhythm')
  await expect(page.getByText('No points yet.', { exact: false })).toBeVisible()
})

test('the account leads to Achievements', async ({ page }) => {
  await mockApi(page, {})
  await page.goto('/profile')
  await expect(page.getByRole('link', { name: 'Achievements' })).toHaveAttribute('href', '/achievements')
})
