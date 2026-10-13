import { expect, test } from '@playwright/test'
import { mockApi, USER } from './support/notes-api'

/**
 * Classroom quizzes (lvn-backend ADR-0064) against a mocked API: a teacher makes questions from a note with AI, edits
 * them, adds one by hand and publishes; a student takes the quiz without seeing the answers, is scored, reads the
 * answers and explanations, and practises again. A dropped submission is sent again as the same attempt.
 */

const CLASS = '01920000-0000-7000-8000-0000000c0001'
const QUIZ = '01920000-0000-7000-8000-0000000c0a01'
const NOTE = '01920000-0000-7000-8000-00000000a001'
const ART = '01920000-0000-7000-8000-0000000a1001'
const [Q1, Q2] = ['01920000-0000-7000-8000-0000000c0b01', '01920000-0000-7000-8000-0000000c0b02']
const TEACHER = '01920000-0000-7000-8000-00000000bbbb'
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const inline = (s: string) => [{ type: 'text', text: s }]
const can = (over: Record<string, boolean> = {}) => ({ __typename: 'ClassroomActions', requestJoin: false, acceptInvite: false, review: false, post: false, publishQuiz: false, manage: false, leave: false, ...over })
const classroom = (staff: boolean) => ({
  __typename: 'Classroom', id: CLASS, name: 'Biology 10A', description: null, memberCount: 31, createdAt: '2026-10-01T10:00:00.000Z', viewerRequestId: null, viewerInviteId: null,
  viewerRole: staff ? 'TEACHER' : 'STUDENT', joinCode: staff ? 'K7PQ2MXA' : null, teacher: { __typename: 'User', id: staff ? USER : TEACHER, displayName: staff ? 'Asha Rao' : 'Meera Iyer' },
  viewerCan: staff ? can({ review: true, post: true, publishQuiz: true, manage: true }) : can({ leave: true }),
})
const quizCard = (question: string, choices: string[], correct: string[], explanation?: string) => ({ __typename: 'AiCard', type: 'quiz', content: { question: doc(question), choices: choices.map((c, i) => ({ id: `c${i + 1}`, content: inline(c) })), correct, multiple: correct.length > 1, ...(explanation ? { explanation: doc(explanation) } : {}) } })
type Attempt = { id: string; score: number; total: number; answers: { questionId: string; choiceIds: string[]; correct: boolean }[] }
const quiz = (attempts: Attempt[], over: Record<string, unknown> = {}) => {
  const shown = attempts.length > 0
  return {
    __typename: 'ClassQuiz', id: QUIZ, classroomId: CLASS, title: 'Respiration', publishedAt: '2026-10-13T09:00:00.000Z', questionCount: 2, submittedCount: null, viewerCanDelete: false,
    author: { __typename: 'User', id: TEACHER, displayName: 'Meera Iyer' },
    myAttempts: attempts.map((a) => ({ __typename: 'QuizAttempt', submittedAt: '2026-10-13T10:00:00.000Z', ...a, answers: a.answers.map((x) => ({ __typename: 'QuizAnswer', ...x })) })),
    questions: [
      { __typename: 'ClassQuizQuestion', id: Q1, position: 0, question: doc('What makes most of the ATP?'), choices: [{ __typename: 'ClassQuizChoice', id: 'c1', content: inline('Mitochondria') }, { __typename: 'ClassQuizChoice', id: 'c2', content: inline('Ribosomes') }], multiple: false, correct: shown ? ['c1'] : null, explanation: shown ? doc('Respiration happens there.') : null },
      { __typename: 'ClassQuizQuestion', id: Q2, position: 1, question: doc('Which are products?'), choices: [{ __typename: 'ClassQuizChoice', id: 'a', content: inline('Water') }, { __typename: 'ClassQuizChoice', id: 'b', content: inline('Oxygen') }, { __typename: 'ClassQuizChoice', id: 'c', content: inline('Carbon dioxide') }], multiple: true, correct: shown ? ['a', 'c'] : null, explanation: null },
    ],
    ...over,
  }
}
const list = (q: unknown[]) => ({ classroom: { __typename: 'Classroom', id: CLASS, quizzes: q } })

test('a teacher makes questions from a note with AI, edits them, adds one by hand and publishes the quiz', async ({ page }) => {
  let published = false
  const calls = await mockApi(page, {
    Classroom: () => ({ classroom: classroom(true) }),
    ClassroomPosts: () => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    ClassroomQuizzes: () => list(published ? [{ ...quiz([]), submittedCount: 0, viewerCanDelete: true }] : []),
    MyNotes: () => ({ myNotes: { __typename: 'NoteConnection', edges: [{ __typename: 'NoteEdge', node: { __typename: 'Note', id: NOTE, title: 'Respiration notes', visibility: 'PRIVATE', kind: 'NOTE', updatedAt: '2026-10-12T10:00:00.000Z', publishedAt: null, folder: null, tags: [], topics: [], cardCount: 3, owner: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' } } }], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    RunAiTask: () => ({ runAiTask: { __typename: 'AiArtifactPayload', artifact: { __typename: 'AiArtifact', id: ART, task: 'QUIZ', status: 'QUEUED', language: 'ENGLISH', markdown: null, title: null, cards: null, changes: null, error: null, fromPublishedVersion: false, truncated: false, keptAt: null, createdAt: '2026-10-13T10:00:00.000Z' }, userErrors: [] } }),
    AiArtifact: () => ({ aiArtifact: { __typename: 'AiArtifact', id: ART, task: 'QUIZ', status: 'READY', language: 'ENGLISH', markdown: null, title: 'Quiz — Respiration notes', changes: null, error: null, fromPublishedVersion: false, truncated: false, keptAt: null, createdAt: '2026-10-13T10:00:00.000Z', cards: [quizCard('What makes ATP?', ['Mitochondria', 'Ribosomes'], ['c1'], 'Respiration.'), quizCard('Where is glycolysis?', ['Matrix', 'Cytoplasm'], ['c2'])] } }),
    PublishClassQuiz: () => ((published = true), { publishClassQuiz: { __typename: 'ClassQuizPayload', quiz: { ...quiz([]), submittedCount: 0, viewerCanDelete: true }, userErrors: [] } }),
  })
  await page.goto(`/classes/${CLASS}`)
  await page.getByRole('tab', { name: 'Quizzes' }).click()
  await expect(page.getByText('No quizzes yet. Publish one and every member is told.')).toBeVisible()
  await page.getByRole('button', { name: 'New quiz' }).click()
  const builder = page.getByRole('dialog', { name: 'New quiz' })
  await builder.getByLabel('Make questions from a note').selectOption(NOTE)
  await builder.getByRole('button', { name: 'Make questions' }).click()
  // The AI's questions arrive as drafts, and the title from the note.
  await expect(builder.getByLabel('Words of question 1')).toHaveValue('What makes ATP?')
  await expect(builder.getByLabel('Title')).toHaveValue('Respiration notes')
  await builder.getByLabel('Words of question 1').fill('What makes most of a cell’s ATP?')
  await builder.getByRole('button', { name: 'Remove question 2' }).click()
  // One by hand, with two correct choices.
  await builder.getByRole('button', { name: 'Add a question' }).click()
  await builder.getByRole('button', { name: /^Publish/ }).click()
  await expect(builder.getByText('Question 2 has no words.')).toBeVisible()
  const second = builder.getByRole('listitem', { name: 'Question 2' })
  await second.getByLabel('Words of question 2').fill('Which are products of respiration?')
  await second.getByLabel('Choice 1', { exact: true }).fill('Water')
  await second.getByLabel('Choice 2', { exact: true }).fill('Oxygen')
  await second.getByRole('button', { name: 'Add a choice' }).click()
  await second.getByLabel('Choice 3', { exact: true }).fill('Carbon dioxide')
  await second.getByLabel('Choice 3 is correct').check()
  await builder.getByRole('button', { name: 'Publish 2 questions' }).click()
  await expect(page.getByText('Quiz published. Everyone in the class has been told.')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Respiration' })).toBeVisible()
  await expect(page.getByText('No student has submitted yet')).toBeVisible()

  const input = calls.find((c) => c.op === 'PublishClassQuiz')!.variables.input as { classroomId: string; title: string; sourceNoteId: string; questions: { question: unknown; choices: { id: string }[]; correct: string[]; multiple: boolean; explanation?: unknown }[] }
  expect(input).toMatchObject({ classroomId: CLASS, title: 'Respiration notes', sourceNoteId: NOTE })
  expect(input.questions).toEqual([
    { question: doc('What makes most of a cell’s ATP?'), choices: [{ id: 'c1', content: inline('Mitochondria') }, { id: 'c2', content: inline('Ribosomes') }], correct: ['c1'], multiple: false, explanation: doc('Respiration.') },
    { question: doc('Which are products of respiration?'), choices: [{ id: 'c1', content: inline('Water') }, { id: 'c2', content: inline('Oxygen') }, { id: 'c3', content: inline('Carbon dioxide') }], correct: ['c1', 'c3'], multiple: true },
  ])
  expect(calls.find((c) => c.op === 'RunAiTask')?.variables).toEqual({ input: { noteId: NOTE, task: 'QUIZ' } })
})

test('a student takes a quiz without its answers, is scored, reads them, and practises again; a dropped submission is the same attempt', async ({ page }) => {
  let attempts: Attempt[] = []
  const calls = await mockApi(page, {
    Classroom: () => ({ classroom: classroom(false) }),
    ClassroomPosts: () => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    ClassroomQuizzes: () => list([quiz(attempts)]),
    ClassQuiz: () => ({ classQuiz: quiz(attempts) }),
    SubmitQuizAttempt: (v) => {
      const answers = (v.input as { answers: { questionId: string; choiceIds: string[] }[] }).answers
      const right = (id: string, chosen: string[]) => (id === Q1 ? chosen.join() === 'c1' : [...chosen].sort().join() === 'a,c')
      const attempt = { id: `att${attempts.length + 1}`, score: answers.filter((a) => right(a.questionId, a.choiceIds)).length, total: 2, answers: answers.map((a) => ({ ...a, correct: right(a.questionId, a.choiceIds) })) }
      attempts = [attempt, ...attempts]
      return { submitQuizAttempt: { __typename: 'QuizAttemptPayload', attempt: { __typename: 'QuizAttempt', id: attempt.id, score: attempt.score, total: attempt.total }, quiz: quiz(attempts), userErrors: [] } }
    },
  })
  // The first submission is lost on the way; sending again must carry the same id.
  let dropped = false
  await page.route('**/graphql', async (route) => {
    const body = route.request().postDataJSON() as { operationName?: string }
    if (body.operationName === 'SubmitQuizAttempt' && !dropped) {
      dropped = true
      calls.push({ op: 'SubmitQuizAttempt (dropped)', variables: (route.request().postDataJSON() as { variables: Record<string, unknown> }).variables })
      return route.abort()
    }
    return route.fallback()
  })

  await page.goto(`/classes/${CLASS}`)
  await page.getByRole('tab', { name: 'Quizzes' }).click()
  await expect(page.getByText('Not taken yet')).toBeVisible()
  await expect(page.getByRole('button', { name: 'New quiz' })).toHaveCount(0)
  await page.getByRole('link', { name: 'Take the quiz' }).click()
  await expect(page).toHaveURL(new RegExp(`/classes/${CLASS}/quizzes/${QUIZ}$`))
  await expect(page.getByRole('heading', { name: 'Respiration' })).toBeVisible()
  await page.getByRole('radio', { name: 'Mitochondria' }).click()
  await page.getByRole('checkbox', { name: 'Water' }).click()
  await expect(page.getByText('Pick every correct answer.')).toBeVisible()
  await page.getByRole('button', { name: 'Submit answers' }).click()
  await expect(page.getByText('Your answers were not sent. Check the connection and submit again.')).toBeVisible()
  await page.getByRole('button', { name: 'Submit answers' }).click()

  await expect(page.getByText('You got 1 of 2')).toBeVisible()
  const sent = calls.filter((c) => c.op.startsWith('SubmitQuizAttempt'))
  expect(sent).toHaveLength(2)
  const [lost, kept] = sent.map((c) => c.variables.input as { clientOpId: string; answers: unknown })
  expect(kept!.clientOpId).toBe(lost!.clientOpId)
  expect(kept!.answers).toEqual([{ questionId: Q1, choiceIds: ['c1'] }, { questionId: Q2, choiceIds: ['a'] }])
  // The answers and the explanation, once submitted.
  const first = page.getByRole('listitem', { name: 'Question 1' })
  await expect(first.getByText('Right')).toBeVisible()
  await expect(first.getByText('Respiration happens there.')).toBeVisible()
  await expect(page.getByRole('listitem', { name: 'Question 2' }).getByText('Wrong')).toBeVisible()

  // Practice: a new submission, a new id; the first attempt stays the score.
  await page.getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByText('Practice: your first attempt stays your score.')).toBeVisible()
  await page.getByRole('radio', { name: 'Mitochondria' }).click()
  await page.getByRole('checkbox', { name: 'Water' }).click()
  await page.getByRole('checkbox', { name: 'Carbon dioxide' }).click()
  await page.getByRole('button', { name: 'Submit answers' }).click()
  await expect(page.getByText('You got 2 of 2')).toBeVisible()
  await expect(page.getByText('Your score is your first attempt: 1 of 2')).toBeVisible()
  const third = calls.filter((c) => c.op === 'SubmitQuizAttempt').at(-1)!.variables.input as { clientOpId: string }
  expect(third.clientOpId).not.toBe(lost!.clientOpId)
})
