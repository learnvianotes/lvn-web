import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Weekly tasks and the class goal (lvn-backend ADR-0081): the week's tasks with how far each has come and the plan
 * written for it, added from a suggestion or chosen freely, changed and removed; a class's goal as everyone sees it
 * (the total) and as its teacher does (each part, and setting it).
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const TOPIC = '01920000-0000-7000-8000-00000000c511'
const CLASS = '01920000-0000-7000-8000-0000000c1a55'
const task = (id: string, kind: string, target: number, progress: number, extra: Record<string, unknown> = {}) => ({ __typename: 'WeeklyTask', id, kind, target, progress, done: progress >= target, topicId: null, topicTitle: null, plan: null, ...extra })
const rhythm = {
  __typename: 'Rhythm', timeZone: 'Asia/Kolkata', plannedDays: [1, 2, 4, 6], target: 4, countedDays: 1, met: false,
  week: [1, 2, 3, 4, 5, 6, 7].map((i) => ({ __typename: 'RhythmDay', day: `2026-10-${String(11 + i).padStart(2, '0')}`, weekday: i, planned: [1, 2, 4, 6].includes(i), counted: i === 1, status: i === 1 ? 'COUNTED' : i === 3 ? 'TODAY' : i < 3 ? 'REST' : 'AHEAD' })),
  today: { __typename: 'RhythmToday', day: '2026-10-14', learningSeconds: 240, reviews: 3, counted: false, comeback: false, cameBack: false, items: [] },
  weeksThisTerm: 9, weeksAllTime: 23, countedDaysAllTime: 140, pauses: [], pauseDaysLeft: 14, suggestion: null, shareRhythm: false,
}
const week = (tasks: unknown[]) => ({ weeklyTasks: { __typename: 'WeeklyTasks', weekStart: '2026-10-12', max: 3, tasks } })

test('the week’s tasks show their progress and plan; one is added from a suggestion, another removed', async ({ page }) => {
  let tasks = [task('01920000-0000-7000-8000-0000000007a1', 'REVIEWS', 10, 12, { plan: 'After lunch, in the library' }), task('01920000-0000-7000-8000-0000000007a2', 'TOPIC_MINUTES', 60, 15, { topicId: TOPIC, topicTitle: 'Heaps' })]
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm }),
    WeeklyTasks: () => week(tasks),
    TaskSuggestions: () => ({ taskSuggestions: [{ __typename: 'TaskSuggestion', kind: 'QUIZ_ANSWERS', target: 20, topicId: TOPIC, topicTitle: 'Graphs', why: 'Fewer than six in ten of your answers on Graphs were right lately.' }] }),
    AddWeeklyTask: (v) => {
      const input = (v as { input: { kind: string; target: number } }).input
      tasks = [...tasks, task('01920000-0000-7000-8000-0000000007a3', input.kind, input.target, 0, { topicId: TOPIC, topicTitle: 'Graphs' })]
      return { addWeeklyTask: { __typename: 'WeeklyTaskPayload', task: tasks.at(-1), userErrors: [] } }
    },
    RemoveWeeklyTask: (v) => ((tasks = tasks.filter((x) => x.id !== v.id)), { removeWeeklyTask: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  }, viewerExtras)
  await page.goto('/rhythm')
  const box = page.getByRole('region', { name: 'This week’s tasks' })
  await expect(box.getByText('1 of 2 done')).toBeVisible()
  await expect(box.getByRole('progressbar', { name: 'Review 10 flashcards' })).toHaveAttribute('aria-valuenow', '10')
  await expect(box.getByText('Plan: After lunch, in the library')).toBeVisible()
  await expect(box.getByRole('progressbar', { name: 'Spend 60 minutes on Heaps' })).toHaveAttribute('aria-valuenow', '15')

  await box.getByRole('button', { name: 'Add a task' }).click()
  await expect(box.getByText('Fewer than six in ten of your answers on Graphs were right lately.')).toBeVisible()
  await box.getByRole('button', { name: 'Add the task Answer 20 questions on Graphs' }).click()
  await expect(box.getByText('1 of 3 done')).toBeVisible()
  expect(calls.find((c) => c.op === 'AddWeeklyTask')?.variables).toEqual({ input: { kind: 'QUIZ_ANSWERS', target: 20, topicId: TOPIC, plan: null } })
  await expect(box.getByText('That’s 3 tasks for this week.')).toBeVisible()

  await box.getByRole('button', { name: 'Remove the task Spend 60 minutes on Heaps' }).click()
  await expect(box.getByText('1 of 2 done')).toBeVisible()
})

test('a class goal: classmates see the total, its teacher each part and the target', async ({ page }) => {
  const goal = (parts: unknown) => ({ __typename: 'ClassGoal', target: 4, progress: 3, sharePerStudent: 3, automatic: false, reached: false, parts })
  const ring = (g: unknown) => ({ classroom: { __typename: 'Classroom', id: CLASS, rhythmRing: { __typename: 'ClassroomRhythm', students: 2, metCount: 0, countedDays: 3, targetDays: 8, people: [], goal: g } } })
  const classroom = (teacher: boolean) => ({
    __typename: 'Classroom', id: CLASS, name: 'Physics 9A', description: null, memberCount: 3, viewerRole: teacher ? 'TEACHER' : 'STUDENT', teacher: { __typename: 'User', id: '01920000-0000-7000-8000-0000000000cc', displayName: 'Ms Rao', handle: 'rao' }, createdAt: '2026-10-01T10:00:00.000Z',
    joinCode: teacher ? 'K7PQ2MXA' : null, viewerRequestId: null, viewerInviteId: null,
    viewerCan: { __typename: 'ClassroomActions', requestJoin: false, acceptInvite: false, review: teacher, post: teacher, publishQuiz: teacher, manage: teacher, leave: !teacher },
  })
  const posts = () => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } })

  await mockApi(page, { Classroom: () => ({ classroom: classroom(false) }), ClassroomPosts: posts, ClassroomRhythmRing: () => ring(goal(null)) }, viewerExtras)
  await page.goto(`/classes/${CLASS}`)
  await page.getByRole('tab', { name: 'Rhythm' }).click()
  const box = page.getByRole('region', { name: 'Class goal this week' })
  await expect(box.getByText('3 of 4 counted days, together')).toBeVisible()
  await expect(box.getByText('Each student counts up to 3 days, so no one carries it alone.')).toBeVisible()
  await expect(box.getByText(/Each student’s part/)).toHaveCount(0)
  await expect(box.getByRole('button')).toHaveCount(0)

  await page.unrouteAll()
  const calls = await mockApi(page, {
    Classroom: () => ({ classroom: classroom(true) }),
    ClassroomPosts: posts,
    ClassroomRhythmRing: () => ring(goal([{ __typename: 'ClassGoalPart', countedDays: 2, user: { __typename: 'User', id: '01920000-0000-7000-8000-0000000000dd', displayName: 'Kiran Das' } }, { __typename: 'ClassGoalPart', countedDays: 1, user: { __typename: 'User', id: '01920000-0000-7000-8000-0000000000de', displayName: 'Meena Shah' } }])),
    SetClassGoal: () => ({ setClassGoal: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  }, viewerExtras)
  await page.reload()
  await page.getByRole('tab', { name: 'Rhythm' }).click()
  await box.getByText(/Each student’s part/).click()
  await expect(box.getByText('Kiran Das')).toBeVisible()
  await expect(box.getByText('1 day')).toBeVisible()
  await box.getByLabel('Target in counted days').fill('6')
  await box.getByRole('button', { name: 'Update the goal' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'SetClassGoal')?.variables).toEqual({ input: { classroomId: CLASS, on: true, target: 6 } })
})
