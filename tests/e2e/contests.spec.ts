import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Weekly contests and Quizzes (lvn-backend ADR-0082): the open contest as board A draws it; one attempt with a timer,
 * answers that can change, and the answers explained after with the person's best and, for an adult who asks, a band;
 * the Quizzes page; an admin writing and publishing a contest.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const ID = '01920000-0000-7000-8000-00000000c0a1'
const A = '01920000-0000-7000-8000-00000000c0b1'
const Q = (n: number) => `01920000-0000-7000-8000-00000000c0d${n}`
const base = { __typename: 'Contest', id: ID, title: 'DSA Battle #12', subjectTitle: 'Data Structures', opensAt: new Date(Date.now() - 3_600_000).toISOString(), closesAt: new Date(Date.now() + 86_400_000).toISOString(), minutes: 20, questionCount: 2, state: 'OPEN', participantsMilestone: 1000 }
const choices = [{ __typename: 'ContestChoice', id: 'c2', text: 'O(n)' }, { __typename: 'ContestChoice', id: 'c1', text: 'O(log n)' }]
const attempt = (finished: boolean, mine: Record<string, string | null> = {}) => ({
  __typename: 'ContestAttempt', id: A, startedAt: new Date().toISOString(), deadline: new Date(Date.now() + 19 * 60_000).toISOString(), submittedAt: finished ? new Date().toISOString() : null, finished,
  score: finished ? 1 : null, total: 2, personalBest: finished ? 50 : null, band: finished ? 'TOP_25' : null,
  questions: [1, 2].map((n) => ({ __typename: 'ContestAttemptQuestion', id: Q(n), prompt: `Heap insert ${n}?`, choices, myChoiceId: mine[Q(n)] ?? null, correctChoiceId: finished ? 'c1' : null, explanation: finished ? 'Sift-up walks one path.' : null })),
})
const settings = (show: boolean) => ({ __typename: 'ContestSettings', showBands: show, canShowBands: true })

test('the open contest is joined, answered against the clock, and explained after', async ({ page }) => {
  let state: 'none' | 'started' | 'done' = 'none'
  let compare = false
  const answers: Record<string, string> = {}
  const calls = await mockApi(page, {
    Contests: () => ({ contests: [{ ...base, viewerAttempt: null }] }),
    Contest: () => ({ contest: { ...base, viewerAttempt: state === 'none' ? null : attempt(state === 'done', answers) }, contestSettings: settings(compare) }),
    StartContest: () => ((state = 'started'), { startContest: { __typename: 'ContestPayload', contest: { ...base, viewerAttempt: attempt(false) }, userErrors: [] } }),
    AnswerContestQuestion: (v) => {
      const input = (v as { input: { questionId: string; choiceId: string } }).input
      answers[input.questionId] = input.choiceId
      // The API answers with the attempt's questions and the viewer's choices (as it does).
      return { answerContestQuestion: { __typename: 'ContestPayload', contest: { __typename: 'Contest', id: ID, viewerAttempt: { __typename: 'ContestAttempt', id: A, questions: [1, 2].map((n) => ({ __typename: 'ContestAttemptQuestion', id: Q(n), myChoiceId: answers[Q(n)] ?? null })) } }, userErrors: [] } }
    },
    SubmitContest: () => ((state = 'done'), { submitContest: { __typename: 'ContestPayload', contest: { ...base, viewerAttempt: attempt(true, answers) }, userErrors: [] } }),
    SetContestBands: (v) => ((compare = !!v.show), { setContestBands: { __typename: 'ContestSettingsPayload', settings: settings(compare), userErrors: [] } }),
  }, viewerExtras)
  await page.goto('/contests')
  const hero = page.getByRole('region', { name: 'DSA Battle #12' })
  await expect(hero.getByText('2 questions')).toBeVisible()
  await expect(hero.getByText('1,000+ taking part')).toBeVisible()
  await hero.getByRole('link', { name: 'Join now' }).click()
  await page.getByRole('button', { name: 'Start' }).click()

  const attemptBox = page.getByRole('region', { name: 'Your attempt' })
  await expect(attemptBox.getByRole('timer', { name: 'Time left' })).toHaveText(/^1[89]:\d\d$/)
  await attemptBox.getByRole('radiogroup', { name: 'Heap insert 1?' }).getByRole('radio', { name: 'O(n)' }).click()
  await attemptBox.getByRole('radiogroup', { name: 'Heap insert 1?' }).getByRole('radio', { name: 'O(log n)' }).click()
  await expect(attemptBox.getByText('1 of 2 answered')).toBeVisible()
  await expect.poll(() => calls.filter((c) => c.op === 'AnswerContestQuestion').map((c) => (c.variables as { input: { choiceId: string } }).input.choiceId)).toEqual(['c2', 'c1'])
  await attemptBox.getByRole('button', { name: 'Submit' }).click()

  const results = page.getByRole('region', { name: 'Your result' })
  await expect(results.getByText('1 of 2')).toBeVisible()
  await expect(results.getByText('Your best on Data Structures: 50%')).toBeVisible()
  await expect(page.getByText('Sift-up walks one path.').first()).toBeVisible()
  await expect(page.getByText('Not answered.')).toBeVisible()
  await results.getByRole('checkbox', { name: /Show me how I compare/ }).check()
  await expect.poll(() => calls.find((c) => c.op === 'SetContestBands')?.variables).toEqual({ show: true })
})

test('Quizzes gathers the contest, class quizzes waiting and ways to practise; the sidebar leads there', async ({ page }, info) => {
  const CLASS = '01920000-0000-7000-8000-0000000c1a55'
  await mockApi(page, {
    Contests: () => ({ contests: [{ ...base, viewerAttempt: null }] }),
    QuizzesHub: () => ({ myClassrooms: [{ __typename: 'Classroom', id: CLASS, name: 'Physics 9A', quizzes: [{ __typename: 'ClassQuiz', id: Q(9), title: 'Waves', questionCount: 5, publishedAt: new Date().toISOString(), myAttempts: [] }] }] }),
  }, viewerExtras)
  // On a phone the sidebar is the menu (shell.spec covers it); here it is opened by its address.
  if (info.project.name === 'phone') await page.goto('/quizzes')
  else {
    await page.goto('/home')
    await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Quizzes' }).click()
  }
  await expect(page.getByRole('heading', { name: 'Quizzes', level: 1 })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Join now' })).toHaveAttribute('href', `/contests/${ID}`)
  await expect(page.getByRole('link', { name: /Waves/ })).toHaveAttribute('href', `/classes/${CLASS}/quizzes/${Q(9)}`)
  await expect(page.getByRole('link', { name: /Review flashcards/ })).toHaveAttribute('href', '/review')
})

test('an admin writes a contest and publishes it', async ({ page }) => {
  const saved = { __typename: 'AdminContest', id: ID, title: 'Graphs', subjectId: null, subjectTitle: null, opensAt: base.opensAt, closesAt: base.closesAt, minutes: 20, questionCount: 10, published: false, attempts: 0, questions: [] }
  const calls = await mockApi(page, {
    AdminContests: () => ({ adminContests: [] }),
    ContestSubjects: () => ({ subjects: [{ __typename: 'Subject', id: '01920000-0000-7000-8000-0000000005b1', title: 'Data Structures' }] }),
    SaveContest: () => ({ saveContest: { __typename: 'AdminContestPayload', contest: saved, userErrors: [] } }),
    PublishContest: () => ({ publishContest: { __typename: 'AdminContestPayload', contest: { ...saved, published: true }, userErrors: [] } }),
  }, viewerExtras)
  await page.goto('/admin/contests')
  await page.getByRole('button', { name: 'New contest' }).click()
  await page.getByLabel('Title').fill('Graphs')
  await page.getByLabel('Subject').selectOption({ label: 'Data Structures' })
  await page.getByLabel('Question', { exact: true }).fill('BFS uses a…')
  await page.getByLabel('Choice 1', { exact: true }).fill('Stack')
  await page.getByLabel('Choice 2', { exact: true }).fill('Queue')
  await page.getByLabel('Choice 2 is right').check()
  await page.getByLabel('Why (shown after the attempt)').fill('Breadth first visits by levels: first in, first out.')
  await page.getByRole('button', { name: 'Publish' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'PublishContest')?.variables).toEqual({ id: ID })
  const input = (calls.find((c) => c.op === 'SaveContest')?.variables as { input: Record<string, unknown> }).input
  expect(input).toMatchObject({ id: null, title: 'Graphs', subjectId: '01920000-0000-7000-8000-0000000005b1', minutes: 20, questionCount: 10, questions: [{ prompt: 'BFS uses a…', choices: ['Stack', 'Queue'], correct: 1, explanation: 'Breadth first visits by levels: first in, first out.' }] })
  // The default window: Saturday 10:00 to Sunday 22:00, India time.
  expect(new Date(input.opensAt as string).getUTCHours()).toBe(4)
  expect(new Date(input.opensAt as string).getUTCMinutes()).toBe(30)
})
