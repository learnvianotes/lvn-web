import { expect, test } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

/**
 * Exams (lvn-backend ADR-0070): each exam's Readiness against the target line and today's revision; adding one with
 * topics found by name; one exam's topics and plan; weak topics with why; the Rhythm ring's exam items and suggestion.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const EXAM = '01920000-0000-7000-8000-0000000e0001'
const TOPIC_A = '01920000-0000-7000-8000-0000000070a1'
const TOPIC_B = '01920000-0000-7000-8000-0000000070b2'
/** A calendar day the exam form will accept: its date input refuses anything before today. */
const futureDay = (days: number) => {
  const d = new Date()
  d.setDate(d.getDate() + days)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}
const topic = (id: string, title: string, over: Record<string, unknown> = {}) => ({ __typename: 'ExamTopic', key: `topic:${id}`, title, recall: null, accuracy: null, mastery: 0, ...over })
const task = (n: number, day: string, titles: string[], over: Record<string, unknown> = {}) => ({ __typename: 'ExamPlanTask', id: `01920000-0000-7000-8000-00000000aa0${n}`, day, done: false, today: false, topics: titles.map((title) => ({ __typename: 'ExamPlanTopic', key: `topic:${title}`, title })), ...over })
const exam = (over: Record<string, unknown> = {}) => ({
  __typename: 'Exam',
  id: EXAM,
  name: 'Operating Systems',
  date: '2026-10-25',
  daysLeft: 12,
  past: false,
  readiness: 34,
  target: 80,
  targetToday: 40,
  topics: [topic(TOPIC_A, 'Paging', { recall: 0.9, accuracy: 0.2, mastery: 0.62 }), topic(TOPIC_B, 'Scheduling')],
  tasks: [task(1, '2026-10-13', ['Paging'], { today: true }), task(2, '2026-10-18', ['Scheduling']), task(3, '2026-10-24', ['Paging'])],
  ...over,
})
const weakTopics = [
  { __typename: 'WeakTopic', key: `topic:${TOPIC_A}`, title: 'Paging', reason: 'LOW_ACCURACY', accuracy: 0.2, examId: EXAM, examName: 'Operating Systems', daysLeft: 12 },
  { __typename: 'WeakTopic', key: `topic:${TOPIC_B}`, title: 'Scheduling', reason: 'NOT_REVISITED', accuracy: null, examId: EXAM, examName: 'Operating Systems', daysLeft: 12 },
]

test('lists exams with Readiness against today’s target, today’s revision, and the weak topics', async ({ page }) => {
  await mockApi(page, { Exams: () => ({ exams: [exam()] }), WeakTopics: () => ({ weakTopics }) }, viewerExtras)
  await page.goto('/exams')
  const card = page.getByRole('article', { name: 'Operating Systems' })
  await expect(card.getByText('Readiness 34%')).toBeVisible()
  await expect(card.getByRole('meter', { name: 'Readiness: 34%, target today 40%' })).toBeVisible()
  await expect(card.getByText('6 points below today’s target')).toBeVisible()
  await expect(card.getByText('Today: Paging')).toBeVisible()
  await expect(card.getByText(/In 12 days/)).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Upcoming' })).toHaveAttribute('aria-selected', 'true')
  await page.getByRole('tab', { name: 'Progress' }).click()
  const weak = page.getByRole('region', { name: 'Weak topics' })
  await expect(weak.getByText('Under 60% right in your last quizzes (20%)')).toBeVisible()
  await expect(weak.getByText('Not revised in 14 days, before Operating Systems')).toBeVisible()
  await expect(page.getByText(/lost|failed|missed/i)).toHaveCount(0)
})

test('adds an exam with topics found by name', async ({ page }) => {
  let exams: unknown[] = []
  const calls = await mockApi(page, {
    Exams: () => ({ exams }),
    WeakTopics: () => ({ weakTopics: [] }),
    ExamTopicOptions: (v) => ({
      examTopicOptions: (v as { query: string }).query.toLowerCase().startsWith('pag')
        ? [{ __typename: 'ExamTopicOption', id: TOPIC_A, key: `topic:${TOPIC_A}`, title: 'Paging', subjectTitle: 'Operating Systems' }]
        : [{ __typename: 'ExamTopicOption', id: TOPIC_B, key: `topic:${TOPIC_B}`, title: 'Scheduling', subjectTitle: 'Operating Systems' }],
    }),
    CreateExam: () => {
      exams = [exam()]
      return { createExam: { __typename: 'ExamPayload', exam: exams[0], userErrors: [] } }
    },
  }, viewerExtras)
  await page.goto('/exams')
  await expect(page.getByText(/No exams yet/)).toBeVisible()
  await page.getByRole('button', { name: 'Add an exam' }).click()
  const form = page.getByRole('region', { name: 'Add an exam' })
  await form.getByLabel('Exam').fill('Operating Systems')
  const date = futureDay(30)
  await form.getByLabel('Date').fill(date)
  await expect(form.getByRole('button', { name: 'Add the exam' })).toBeDisabled() // no topics yet
  await form.getByLabel('Find a topic').fill('pag')
  await form.getByRole('button', { name: 'Add Paging' }).click()
  await form.getByLabel('Find a topic').fill('sched')
  await form.getByRole('button', { name: 'Add Scheduling' }).click()
  await form.getByRole('button', { name: 'Remove Paging' }).click()
  await form.getByLabel('Find a topic').fill('pag')
  await form.getByRole('button', { name: 'Add Paging' }).click()
  await form.getByRole('button', { name: 'Add the exam' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'CreateExam')?.variables).toEqual({ input: { name: 'Operating Systems', date, topicIds: [TOPIC_B, TOPIC_A] } })
  await expect(page.getByRole('article', { name: 'Operating Systems' })).toBeVisible()
})

test('says why an exam cannot be added', async ({ page }) => {
  await mockApi(page, {
    Exams: () => ({ exams: [] }),
    WeakTopics: () => ({ weakTopics: [] }),
    ExamTopicOptions: () => ({ examTopicOptions: [{ __typename: 'ExamTopicOption', id: TOPIC_A, key: `topic:${TOPIC_A}`, title: 'Paging', subjectTitle: 'Operating Systems' }] }),
    CreateExam: () => ({ createExam: { __typename: 'ExamPayload', exam: null, userErrors: [{ __typename: 'UserError', message: 'You can plan for 10 exams at a time.', code: 'VALIDATION' }] } }),
  }, viewerExtras)
  await page.goto('/exams')
  await page.getByRole('button', { name: 'Add an exam' }).click()
  await page.getByLabel('Exam', { exact: true }).fill('Eleventh')
  await page.getByLabel('Date', { exact: true }).fill('2026-11-25')
  await page.getByLabel('Find a topic').fill('pag')
  await page.getByRole('button', { name: 'Add Paging' }).click()
  await page.getByRole('button', { name: 'Add the exam' }).click()
  await expect(page.getByText('You can plan for 10 exams at a time.')).toBeVisible()
})

test('shows one exam’s topics and plan, and deletes it', async ({ page }) => {
  const calls = await mockApi(page, {
    Exam: () => ({ exam: exam({ tasks: [task(1, '2026-10-12', ['Paging'], { done: true }), task(2, '2026-10-13', ['Scheduling'], { today: true }), task(3, '2099-10-24', ['Paging'])] }) }),
    Exams: () => ({ exams: [] }),
    WeakTopics: () => ({ weakTopics: [] }),
    DeleteExam: () => ({ deleteExam: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  }, viewerExtras)
  await page.goto(`/exams/${EXAM}`)
  await expect(page.getByRole('heading', { name: 'Operating Systems' })).toBeVisible()
  const topics = page.getByRole('region', { name: 'Topics' })
  await expect(topics.getByText('Recall 90% · Accuracy 20%')).toBeVisible()
  await expect(topics.getByText('No flashcards or quizzes yet')).toBeVisible()
  const plan = page.getByRole('region', { name: 'Revision plan' })
  await expect(plan.getByRole('listitem', { name: /Paging, done$/ })).toBeVisible()
  await expect(plan.getByRole('listitem', { name: /Scheduling, today$/ })).toBeVisible()
  await expect(plan.getByRole('listitem', { name: /Paging, to come$/ })).toBeVisible()
  page.once('dialog', (d) => void d.accept())
  await page.getByRole('button', { name: 'Delete the exam' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'DeleteExam')?.variables).toEqual({ input: { id: EXAM } })
  await expect(page).toHaveURL(/\/exams$/)
})

test('Rhythm shows today’s revision and a weak topic in the ring, and suggests a day more before an exam', async ({ page }) => {
  const week = ['COUNTED', 'MISSED', 'REST', 'TODAY', 'AHEAD', 'AHEAD', 'AHEAD'].map((status, i) => ({ __typename: 'RhythmDay', day: `2026-10-${12 + i}`, weekday: i + 1, planned: [1, 2, 4, 6].includes(i + 1), counted: status === 'COUNTED', status }))
  await mockApi(page, {
    Rhythm: () => ({
      rhythm: {
        __typename: 'Rhythm', timeZone: 'UTC', plannedDays: [1, 2, 4, 6], target: 4, countedDays: 1, met: false, week,
        today: {
          __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 0, reviews: 0, counted: false, comeback: false, cameBack: false,
          items: [
            { __typename: 'RhythmItem', kind: 'REVIEWS', done: 0, total: 0, title: null, topicKey: null },
            { __typename: 'RhythmItem', kind: 'PLAN_TASK', done: 0, total: 1, title: 'Operating Systems', topicKey: null },
            { __typename: 'RhythmItem', kind: 'WEAK_TOPIC', done: 0, total: 1, title: 'Paging', topicKey: `topic:${TOPIC_A}` },
          ],
        },
        weeksThisTerm: 0, weeksAllTime: 0, countedDaysAllTime: 1, pauses: [], pauseDaysLeft: 14,
        shareRhythm: false,
        suggestion: { __typename: 'RhythmSuggestion', plannedDays: 5, examId: EXAM, examName: 'Operating Systems', daysLeft: 12 },
      },
    }),
  }, viewerExtras)
  await page.goto('/rhythm')
  const today = page.getByRole('region', { name: 'Today' })
  await expect(today.getByText('Revision for Operating Systems: 0 of 1')).toBeVisible()
  await expect(today.getByRole('link', { name: 'Plan' })).toHaveAttribute('href', '/exams')
  await expect(today.getByText('Weak topic: Paging')).toBeVisible()
  await expect(page.getByRole('note')).toContainText('Operating Systems is in 12 days: try 5 planned days a week until then.')
})

test('a quiz checked in a note read signed in is a result on the note’s topics', async ({ page }) => {
  const quiz = {
    __typename: 'Card',
    id: '01920000-0000-7000-8000-00000000c003',
    type: 'quiz',
    position: 'a2',
    revision: 1,
    content: { question: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Its running time?' }] }] }, choices: [{ id: 'a', content: [{ type: 'text', text: 'O(n)' }] }, { id: 'b', content: [{ type: 'text', text: 'O(log n)' }] }], correct: ['b'], multiple: false },
  }
  const reader = { viewerAccess: 'READER', viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true }, draftRevision: null, publishedAt: new Date().toISOString() }
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ ...reader, topics: [{ __typename: 'Topic', id: TOPIC_A, title: 'Paging', subject: { __typename: 'Subject', id: TOPIC_B, title: 'Operating Systems' } }] }), cards: page1([...cards, quiz]) } }),
    TrackEvents: (v) => ({ trackEvents: { __typename: 'TrackEventsPayload', accepted: (v.input as { events: unknown[] }).events.length, duplicates: 0, rejected: [], userErrors: [] } }),
  })
  await page.clock.install()
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('radio', { name: 'O(n)' }).click()
  await page.getByRole('button', { name: 'Check' }).click()
  await expect(page.getByText('Not quite')).toBeVisible()
  await page.clock.runFor(11_000)
  await expect.poll(() => calls.filter((c) => c.op === 'TrackEvents').flatMap((c) => (c.variables.input as { events: { type: string }[] }).events).find((e) => e.type === 'QUIZ_COMPLETED')).toMatchObject({
    type: 'QUIZ_COMPLETED',
    entityType: 'NOTE_CARD',
    entityId: quiz.id,
    topicKeys: [`topic:${TOPIC_A}`],
    metadata: { answered: 1, correct: 0 },
  })
})

const noteHit = (id: string, title: string) => ({ __typename: 'NoteSearchHit', snippet: '', note: { __typename: 'Note', id, title, kind: 'NOTE', visibility: 'PUBLIC', viewerAccess: 'READER', publishedAt: new Date().toISOString(), owner: { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Meera Iyer' } } })
const searchResults = (notes: unknown[]) => ({ search: { __typename: 'SearchResults', notes, notesCursor: null, people: [], topics: [], groups: [], classrooms: [], resources: [] } })

test('tabs: the Study Plan’s checklist leads to each topic and Continue plan to the next; Progress; Notes on the exam’s topics', async ({ page }) => {
  const calls = await mockApi(page, { Exams: () => ({ exams: [exam()] }), WeakTopics: () => ({ weakTopics }), Search: () => searchResults([noteHit(NOTE_ID, 'Paging in ten minutes')]) }, viewerExtras)
  await page.goto('/exams')
  const tabs = page.getByRole('tablist', { name: 'Your exams' })
  await expect(tabs.getByRole('tab')).toHaveText(['Upcoming', 'Study Plan', 'Progress', 'Notes'])
  // Study Plan: today's session, not done yet; its topic and Continue plan lead to its notes.
  await tabs.getByRole('tab', { name: 'Study Plan' }).click()
  const today = page.getByRole('list', { name: 'Today’s sessions' }).getByRole('listitem')
  await expect(today).toHaveCount(1)
  await expect(today.getByRole('img', { name: 'to do' })).toBeVisible()
  await expect(today.getByRole('link', { name: 'Paging' })).toHaveAttribute('href', '/search?topic=Paging&topicTitle=Paging')
  await expect(page.getByRole('link', { name: 'Continue plan' })).toHaveAttribute('href', '/search?topic=Paging&topicTitle=Paging')
  await expect(page.getByRole('link', { name: 'The whole plan for Operating Systems' })).toHaveAttribute('href', `/exams/${EXAM}`)
  // Progress: Readiness and each topic, then the weak topics.
  await tabs.getByRole('tab', { name: 'Progress' }).click()
  const progress = page.getByRole('region', { name: 'Operating Systems' })
  await expect(progress.getByRole('meter', { name: 'Readiness: 34%, target today 40%' })).toBeVisible()
  await expect(progress.getByText('Recall 90% · Accuracy 20%')).toBeVisible()
  await expect(page.getByRole('region', { name: 'Weak topics' })).toBeVisible()
  // Notes: on the exam's topics, from everywhere the person may read.
  await tabs.getByRole('tab', { name: 'Notes' }).click()
  await expect(page.getByRole('link', { name: /Paging in ten minutes/ })).toHaveAttribute('href', `/notes/${NOTE_ID}`)
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: '', first: 20, scopes: ['NOTES'], filters: { kinds: null, sources: null, topicId: null, topicIds: [TOPIC_A, TOPIC_B] } })
})

test('a day’s revision done shows no Continue plan; with no exam coming up, each tab leads to adding one', async ({ page }) => {
  let exams = [exam({ tasks: [task(1, '2026-10-13', ['Paging'], { today: true, done: true })] })]
  await mockApi(page, { Exams: () => ({ exams }), WeakTopics: () => ({ weakTopics: [] }), Search: () => searchResults([]) }, viewerExtras)
  await page.goto('/exams')
  await page.getByRole('tab', { name: 'Study Plan' }).click()
  await expect(page.getByText('Today’s revision is done')).toBeVisible()
  await expect(page.getByRole('list', { name: 'Today’s sessions' }).getByRole('img', { name: 'done' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Continue plan' })).toHaveCount(0)
  await page.getByRole('tab', { name: 'Notes' }).click()
  await expect(page.getByText('No notes on these topics yet.')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Search notes' })).toHaveAttribute('href', '/search')
  exams = []
  await page.reload()
  await page.getByRole('tab', { name: 'Progress' }).click()
  await expect(page.getByText('No exam coming up. Add one and its plan, progress and notes appear here.')).toBeVisible()
  await page.getByRole('button', { name: 'Add an exam' }).click()
  await expect(page.getByRole('tab', { name: 'Upcoming' })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByRole('region', { name: 'Add an exam' })).toBeVisible()
})
