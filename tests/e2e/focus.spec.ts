import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Focus mode, Rhythm buddies, sharing, the class's Rhythm ring and class performance (lvn-backend ADR-0072).
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const SESSION = '01920000-0000-7000-8000-00000000f001'
const CLASS = '01920000-0000-7000-8000-00000000c1a5'
const TOPIC = '01920000-0000-7000-8000-0000000070a1'
const user = (id: string, displayName: string) => ({ __typename: 'User', id, displayName, handle: displayName.toLowerCase().replace(/\s+/g, '') })
const week = ['COUNTED', 'MISSED', 'REST', 'TODAY', 'AHEAD', 'AHEAD', 'AHEAD'].map((status, i) => ({ __typename: 'RhythmDay', day: `2026-10-${12 + i}`, weekday: i + 1, planned: [1, 2, 4, 6].includes(i + 1), counted: status === 'COUNTED', status }))
const rhythm = (shareRhythm = false) => ({
  __typename: 'Rhythm', timeZone: 'UTC', plannedDays: [1, 2, 4, 6], target: 4, countedDays: 1, met: false, week,
  today: { __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 0, reviews: 0, counted: false, comeback: false, cameBack: false, items: [] },
  weeksThisTerm: 0, weeksAllTime: 0, countedDaysAllTime: 1, pauses: [], pauseDaysLeft: 14, suggestion: null, shareRhythm,
})
const session = (over: Record<string, unknown> = {}) => ({ __typename: 'FocusSession', id: SESSION, topicKey: `topic:${TOPIC}`, plannedMinutes: 25, breakMinutes: 5, meetUrl: 'https://meet.google.com/abc-defg-hij', startedAt: new Date(Date.now() - 60_000).toISOString(), endedAt: null, focusedSeconds: 0, ...over })
const ok = (name: string, userErrors: unknown[] = []) => ({ [name]: { __typename: 'OkPayload', ok: !userErrors.length, userErrors } })
const noBuddies = { __typename: 'RhythmBuddies', buddies: [], invites: [], sent: [] }

test('starts a focus session on a topic with a Meet link, shows the time left, and ends it', async ({ page }) => {
  let open: ReturnType<typeof session> | null = null
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm: rhythm() }),
    RhythmBuddies: () => ({ rhythmBuddies: noBuddies }),
    Recommendations: () => ({ recommendations: [] }),
    FocusSession: () => ({ focusSession: open }),
    ExamTopicOptions: () => ({ examTopicOptions: [{ __typename: 'ExamTopicOption', id: TOPIC, key: `topic:${TOPIC}`, title: 'Paging', subjectTitle: 'Operating Systems' }] }),
    StartFocusSession: () => {
      open = session()
      return { startFocusSession: { __typename: 'FocusSessionPayload', session: open, userErrors: [] } }
    },
    EndFocusSession: () => {
      const ended = session({ endedAt: new Date().toISOString(), focusedSeconds: 660 })
      open = null
      return { endFocusSession: { __typename: 'FocusSessionPayload', session: ended, userErrors: [] } }
    },
  }, viewerExtras)
  await page.goto('/rhythm')
  const focus = page.getByRole('region', { name: 'Focus' })
  await focus.getByLabel('Topic (optional)').fill('pag')
  await focus.getByRole('button', { name: 'Focus on Paging' }).click()
  await expect(focus.getByText('On Paging')).toBeVisible()
  await focus.getByLabel(/Google Meet link/).fill('https://meet.google.com/abc-defg-hij')
  await focus.getByRole('button', { name: 'Start focusing' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'StartFocusSession')?.variables).toEqual({ input: { minutes: 25, breakMinutes: 5, topicKey: `topic:${TOPIC}`, meetUrl: 'https://meet.google.com/abc-defg-hij' } })
  await expect(focus.getByRole('timer')).toHaveText(/^2[34]:\d\d$/)
  await expect(focus.getByRole('link', { name: 'Open the Meet call' })).toHaveAttribute('href', 'https://meet.google.com/abc-defg-hij')
  await focus.getByRole('button', { name: 'End the session' }).click()
  await expect(focus.getByRole('status')).toHaveText('11 minutes counted.')
})

test('asks a buddy, answers an invite, and sees a buddy studying now with their Meet link', async ({ page }) => {
  let list = {
    ...noBuddies,
    buddies: [{ __typename: 'RhythmBuddy', id: '01920000-0000-7000-8000-0000000b0001', user: user('01920000-0000-7000-8000-0000000000aa', 'Ravi Kumar'), studyingNow: true, studyingSince: new Date().toISOString(), topicTitle: 'Paging', meetUrl: 'https://meet.google.com/abc-defg-hij', countedDays: 2, target: 4, met: false }],
    invites: [{ __typename: 'RhythmBuddyInvite', id: '01920000-0000-7000-8000-0000000b0002', at: new Date().toISOString(), user: user('01920000-0000-7000-8000-0000000000bb', 'Meena Shah') }],
  }
  let refuse = true
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm: rhythm() }),
    RhythmBuddies: () => ({ rhythmBuddies: list }),
    Recommendations: () => ({ recommendations: [] }),
    FocusSession: () => ({ focusSession: null }),
    AnswerRhythmBuddy: () => {
      list = { ...list, invites: [] }
      return ok('answerRhythmBuddy')
    },
    InviteRhythmBuddy: () => {
      if (refuse) {
        refuse = false
        return ok('inviteRhythmBuddy', [{ __typename: 'UserError', message: 'Follow someone, or connect with them, before asking them to be your buddy.', code: 'VALIDATION' }])
      }
      return ok('inviteRhythmBuddy')
    },
  }, viewerExtras)
  await page.goto('/rhythm')
  const box = page.getByRole('region', { name: 'Rhythm buddies' })
  await expect(box.getByText('Studying now')).toBeVisible()
  await expect(box.getByText('On Paging · 2 of 4 days this week')).toBeVisible()
  await expect(box.getByRole('link', { name: 'Join' })).toHaveAttribute('href', 'https://meet.google.com/abc-defg-hij')
  await expect(box.getByText('Meena Shah asked you to be Rhythm buddies.')).toBeVisible()
  await box.getByRole('button', { name: 'Accept' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'AnswerRhythmBuddy')?.variables).toEqual({ input: { id: '01920000-0000-7000-8000-0000000b0002', accept: true } })
  await box.getByLabel('Ask someone by their handle').fill('stranger')
  await box.getByRole('button', { name: 'Ask', exact: true }).click()
  await expect(box.getByText('Follow someone, or connect with them, before asking them to be your buddy.')).toBeVisible()
})

test('turns on sharing Rhythm with classes', async ({ page }) => {
  let shared = false
  const calls = await mockApi(page, {
    Rhythm: () => ({ rhythm: rhythm(shared) }),
    RhythmBuddies: () => ({ rhythmBuddies: noBuddies }),
    Recommendations: () => ({ recommendations: [] }),
    FocusSession: () => ({ focusSession: null }),
    SetRhythmSharing: (v) => {
      shared = (v as { input: { share: boolean } }).input.share
      return ok('setRhythmSharing')
    },
  }, viewerExtras)
  await page.goto('/rhythm')
  const box = page.getByLabel(/Show my name and days on my classes/)
  await expect(box).not.toBeChecked()
  await box.check()
  await expect.poll(() => calls.find((c) => c.op === 'SetRhythmSharing')?.variables).toEqual({ input: { share: true } })
  await expect(box).toBeChecked()
})

test('a class shows its Rhythm this week, and staff see performance and hard topics', async ({ page }) => {
  const classroom = {
    __typename: 'Classroom', id: CLASS, name: 'Physics 9A', description: null, memberCount: 3, viewerRole: 'TEACHER', teacher: user('01920000-0000-7000-8000-0000000000cc', 'Ms Rao'), createdAt: '2026-10-01T10:00:00.000Z',
    joinCode: 'K7PQ2MXA', viewerRequestId: null, viewerInviteId: null,
    viewerCan: { __typename: 'ClassroomActions', requestJoin: false, acceptInvite: false, review: true, post: true, publishQuiz: true, manage: true, leave: false },
  }
  await mockApi(page, {
    Classroom: () => ({ classroom }),
    ClassroomPosts: () => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    ClassroomRhythmRing: () => ({ classroom: { __typename: 'Classroom', id: CLASS, rhythmRing: { __typename: 'ClassroomRhythm', students: 2, metCount: 1, countedDays: 5, targetDays: 8, people: [{ __typename: 'ClassroomRhythmPerson', name: 'Kiran', countedDays: 4, target: 4, met: true, user: { __typename: 'User', id: '01920000-0000-7000-8000-0000000000dd' } }] } } }),
    ClassroomPerformance: () => ({
      classroom: {
        __typename: 'Classroom', id: CLASS,
        performance: {
          __typename: 'ClassPerformance', quizzes: 2,
          students: [{ __typename: 'ClassStudentPerformance', name: 'Kiran Das', submitted: 2, average: 0.75, user: { __typename: 'User', id: '01920000-0000-7000-8000-0000000000dd' }, scores: [] }],
          topics: [{ __typename: 'ClassTopicPerformance', key: `topic:${TOPIC}`, title: 'Paging', accuracy: 0.25, answers: 8, hard: true }],
        },
      },
    }),
  }, viewerExtras)
  await page.goto(`/classes/${CLASS}`)
  await page.getByRole('tab', { name: 'Rhythm' }).click()
  const ring = page.getByRole('region', { name: 'Rhythm this week' })
  await expect(ring.getByText('1 of 2 students met their week · 5 of 8 days counted')).toBeVisible()
  await expect(ring.getByText('Kiran')).toBeVisible()
  await page.getByRole('tab', { name: 'Performance' }).click()
  const perf = page.getByRole('region', { name: 'Class performance' })
  await expect(perf.getByRole('cell', { name: 'Kiran Das' })).toBeVisible()
  await expect(perf.getByRole('cell', { name: '75%' })).toBeVisible()
  await expect(perf.getByText('25% right of 8 answers')).toBeVisible()
  await expect(perf.getByText('Hard', { exact: true })).toBeVisible()
})
