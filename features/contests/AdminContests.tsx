'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Plus, Trash2 } from 'lucide-react'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { AdminContestsDocument, DeleteContestDocument, PublishContestDocument, SaveContestDocument, ContestSubjectsDocument, type AdminContestFieldsFragment } from '@/graphql/generated/graphql'

type Question = { prompt: string; choices: string[]; correct: number; explanation: string }
type Draft = { id: string | null; title: string; subjectId: string; opensAt: string; closesAt: string; minutes: number; questionCount: number; questions: Question[] }

const IST_MS = 330 * 60_000
/** A datetime-local value (India time) for an instant, and back. */
const toLocal = (d: Date) => new Date(d.getTime() + IST_MS).toISOString().slice(0, 16)
const fromLocal = (v: string) => new Date(Date.parse(`${v}:00Z`) - IST_MS).toISOString()
/** Next Saturday 10:00 to Sunday 22:00, India time (ADR-0082's default window). */
function defaultWindow(now = new Date()) {
  const ist = new Date(now.getTime() + IST_MS)
  const ahead = (6 - ist.getUTCDay() + 7) % 7 || 7
  const saturday = Date.UTC(ist.getUTCFullYear(), ist.getUTCMonth(), ist.getUTCDate() + ahead)
  return { opensAt: toLocal(new Date(saturday + 10 * 3_600_000 - IST_MS)), closesAt: toLocal(new Date(saturday + 46 * 3_600_000 - IST_MS)) }
}
const blankQuestion = (): Question => ({ prompt: '', choices: ['', ''], correct: 0, explanation: '' })
const fresh = (): Draft => ({ id: null, title: '', subjectId: '', ...defaultWindow(), minutes: 20, questionCount: 10, questions: [blankQuestion()] })
const fromRow = (c: AdminContestFieldsFragment): Draft => ({
  id: c.id,
  title: c.title,
  subjectId: c.subjectId ?? '',
  opensAt: toLocal(new Date(c.opensAt)),
  closesAt: toLocal(new Date(c.closesAt)),
  minutes: c.minutes,
  questionCount: c.questionCount,
  questions: c.questions.map((q) => ({ prompt: q.prompt, choices: q.choices.map((x) => x.text), correct: Math.max(0, q.choices.findIndex((x) => x.id === q.correctChoiceId)), explanation: q.explanation })),
})

/**
 * Writing weekly contests (lvn-backend ADR-0082), for platform admins: each contest as a draft (a title, a subject, a
 * window in India time, a length, how many questions an attempt gets, and the pool of questions with their right
 * choices and explanations), published when ready. A published contest stays as it is.
 */
export function AdminContests() {
  const t = useTranslations('adminContests')
  const format = useFormatter()
  const { data, error } = useQuery(AdminContestsDocument, { fetchPolicy: 'cache-and-network' })
  const [editing, setEditing] = useState<Draft | null>(null)
  if (error && !data) return <Alert tone="error">{t('forbidden')}</Alert>
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-end sm:justify-between">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
          <p className="text-sm text-muted">{t('lead')}</p>
        </div>
        {!editing ? (
          <Button type="button" onClick={() => setEditing(fresh())}>
            <Plus aria-hidden className="size-4" />
            {t('new')}
          </Button>
        ) : null}
      </header>
      {editing ? <Editor key={editing.id ?? 'new'} draft={editing} onDone={() => setEditing(null)} /> : null}
      <ul className="flex flex-col gap-2">
        {(data?.adminContests ?? []).map((c) => (
          <li key={c.id} className="flex flex-wrap items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3">
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="font-semibold">{c.title}</span>
              <span className="text-sm break-words text-muted">
                {format.dateTime(new Date(c.opensAt), { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })} – {format.dateTime(new Date(c.closesAt), { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })} · {t('pool', { count: c.questions.length, asked: c.questionCount })} · {t('attempts', { count: c.attempts })}
              </span>
            </span>
            <span className="rounded-full bg-surface-2 px-2.5 py-0.5 text-xs font-semibold">{c.published ? t('published') : t('draft')}</span>
            {!c.published ? (
              <Button type="button" variant="secondary" size="sm" className="h-11" onClick={() => setEditing(fromRow(c))}>
                {t('edit')}
              </Button>
            ) : null}
          </li>
        ))}
      </ul>
      {data && !data.adminContests.length && !editing ? <p className="text-sm text-muted">{t('none')}</p> : null}
    </div>
  )
}

function Editor({ draft, onDone }: { draft: Draft; onDone: () => void }) {
  const t = useTranslations('adminContests')
  const [d, setD] = useState(draft)
  const [problem, setProblem] = useState<string | null>(null)
  const subjects = useQuery(ContestSubjectsDocument).data?.subjects ?? []
  const refetchQueries = [AdminContestsDocument]
  const [save, saving] = useMutation(SaveContestDocument, { refetchQueries })
  const [publish, publishing] = useMutation(PublishContestDocument, { refetchQueries })
  const [remove] = useMutation(DeleteContestDocument, { refetchQueries })
  const setQ = (i: number, q: Partial<Question>) => setD((x) => ({ ...x, questions: x.questions.map((old, j) => (j === i ? { ...old, ...q } : old)) }))
  const persist = async (): Promise<string | null> => {
    const res = await save({
      variables: { input: { id: d.id, title: d.title, subjectId: d.subjectId || null, opensAt: fromLocal(d.opensAt), closesAt: fromLocal(d.closesAt), minutes: d.minutes, questionCount: d.questionCount, questions: d.questions } },
    }).catch(() => null)
    const why = res?.data?.saveContest.userErrors[0]?.message ?? (res ? null : t('failed'))
    setProblem(why)
    if (!why && res?.data?.saveContest.contest) setD((x) => ({ ...x, id: res.data!.saveContest.contest!.id }))
    return why ? null : (res?.data?.saveContest.contest?.id ?? null)
  }
  return (
    <form
      className="flex min-w-0 flex-col gap-4 rounded-3xl border border-border bg-surface p-4 sm:p-5"
      onSubmit={async (e) => {
        e.preventDefault()
        if (await persist()) onDone()
      }}
    >
      <div className="grid gap-3 sm:grid-cols-2 sm:[&>*]:min-w-0">
        <label className="flex min-w-0 flex-col gap-1 text-sm sm:col-span-2">
          {t('contestTitle')}
          <input value={d.title} maxLength={120} onChange={(e) => setD({ ...d, title: e.target.value })} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3" />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          {t('subject')}
          <select value={d.subjectId} onChange={(e) => setD({ ...d, subjectId: e.target.value })} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3">
            <option value="">{t('anySubject')}</option>
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
        </label>
        <div className="flex gap-3">
          <label className="flex flex-1 flex-col gap-1 text-sm">
            {t('minutes')}
            <input type="number" min={5} max={60} value={d.minutes} onChange={(e) => setD({ ...d, minutes: Number(e.target.value) })} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3" />
          </label>
          <label className="flex flex-1 flex-col gap-1 text-sm">
            {t('asked')}
            <input type="number" min={3} max={30} value={d.questionCount} onChange={(e) => setD({ ...d, questionCount: Number(e.target.value) })} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3" />
          </label>
        </div>
        <label className="flex flex-col gap-1 text-sm">
          {t('opens')}
          <input type="datetime-local" value={d.opensAt} onChange={(e) => setD({ ...d, opensAt: e.target.value })} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3" />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          {t('closes')}
          <input type="datetime-local" value={d.closesAt} onChange={(e) => setD({ ...d, closesAt: e.target.value })} className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3" />
        </label>
      </div>
      <p className="text-xs text-muted">{t('indiaTime')}</p>

      <ol className="flex flex-col gap-4">
        {d.questions.map((q, i) => (
          <li key={i} className="flex flex-col gap-2 rounded-2xl bg-surface-2 p-4">
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-semibold">{t('question', { n: i + 1 })}</span>
              {d.questions.length > 1 ? (
                <button type="button" aria-label={t('removeQuestion', { n: i + 1 })} className="rounded-lg p-1.5 text-muted hover:text-fg" onClick={() => setD({ ...d, questions: d.questions.filter((_, j) => j !== i) })}>
                  <Trash2 className="size-4" />
                </button>
              ) : null}
            </div>
            <label className="flex flex-col gap-1 text-sm">
              {t('prompt')}
              <textarea value={q.prompt} maxLength={500} rows={2} onChange={(e) => setQ(i, { prompt: e.target.value })} className="rounded-xl border border-border bg-bg px-3 py-2" />
            </label>
            <fieldset className="flex flex-col gap-2">
              <legend className="mb-1 text-sm">{t('choices')}</legend>
              {q.choices.map((choice, c) => (
                <div key={c} className="flex items-center gap-2">
                  <input type="radio" name={`correct-${i}`} aria-label={t('markRight', { n: c + 1 })} checked={q.correct === c} onChange={() => setQ(i, { correct: c })} className="size-4" />
                  <input aria-label={t('choice', { n: c + 1 })} value={choice} maxLength={200} onChange={(e) => setQ(i, { choices: q.choices.map((x, k) => (k === c ? e.target.value : x)) })} className="h-11 min-w-0 flex-1 rounded-xl border border-border bg-bg px-3 text-sm" />
                </div>
              ))}
              {q.choices.length < 6 ? (
                <button type="button" className="self-start text-sm font-medium text-accent hover:underline" onClick={() => setQ(i, { choices: [...q.choices, ''] })}>
                  {t('addChoice')}
                </button>
              ) : null}
            </fieldset>
            <label className="flex flex-col gap-1 text-sm">
              {t('explanation')}
              <textarea value={q.explanation} maxLength={1000} rows={2} onChange={(e) => setQ(i, { explanation: e.target.value })} className="rounded-xl border border-border bg-bg px-3 py-2" />
            </label>
          </li>
        ))}
      </ol>
      <Button type="button" variant="secondary" size="sm" className="self-start" onClick={() => setD({ ...d, questions: [...d.questions, blankQuestion()] })}>
        {t('addQuestion')}
      </Button>
      {problem ? <Alert tone="error">{problem}</Alert> : null}
      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
        <Button type="submit" disabled={saving.loading}>
          {t('saveDraft')}
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={saving.loading || publishing.loading}
          onClick={async () => {
            const id = await persist()
            if (!id) return
            const res = await publish({ variables: { id } }).catch(() => null)
            const why = res?.data?.publishContest.userErrors[0]?.message ?? (res ? null : t('failed'))
            setProblem(why)
            if (!why) onDone()
          }}
        >
          {t('publish')}
        </Button>
        {d.id ? (
          <Button type="button" variant="ghost" onClick={async () => (await remove({ variables: { id: d.id! } }).catch(() => null), onDone())}>
            {t('delete')}
          </Button>
        ) : null}
        <Button type="button" variant="ghost" onClick={onDone}>
          {t('cancel')}
        </Button>
      </div>
    </form>
  )
}
