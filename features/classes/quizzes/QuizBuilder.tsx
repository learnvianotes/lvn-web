'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { LoaderCircle, Plus, Sparkles, Trash } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { attempt, textToDoc } from '@/features/groups/shared'
import { AiArtifactDocument, MyNotesDocument, PublishClassQuizDocument, RunAiTaskDocument } from '@/graphql/generated/graphql'
import { docText, inlineText, type Doc, type Inline } from '@/lib/contracts/validation'

/**
 * A quiz for a class (lvn-backend ADR-0064), composed here and published in one go: questions made by AI from one of
 * the teacher's notes (the QUIZ task) and questions written by hand, each editable before it is published.
 */

interface DraftChoice {
  id: string
  text: string
  correct: boolean
}
interface Draft {
  key: string
  question: string
  choices: DraftChoice[]
  explanation: string
}

const MAX_CHOICES = 8
const MAX_QUESTIONS = 50
const POLL_MS = 1500
let keys = 0
const key = () => `q${++keys}`
const blank = (): Draft => ({ key: key(), question: '', choices: [{ id: 'c1', text: '', correct: true }, { id: 'c2', text: '', correct: false }], explanation: '' })
const nextChoiceId = (choices: DraftChoice[]) => {
  let n = choices.length + 1
  while (choices.some((c) => c.id === `c${n}`)) n++
  return `c${n}`
}

/** A quiz card's content as an editable draft (AI-made questions are plain words). */
function fromCard(content: { question: Doc; choices: { id: string; content: Inline }[]; correct: string[]; explanation?: Doc }): Draft {
  return { key: key(), question: docText(content.question), choices: content.choices.map((c) => ({ id: c.id, text: inlineText(c.content), correct: content.correct.includes(c.id) })), explanation: content.explanation ? docText(content.explanation) : '' }
}

/** A draft as quiz card content, or why it is not ready. */
function toCard(d: Draft): { content: object } | { problem: 'noQuestion' | 'fewChoices' | 'noCorrect' } {
  const choices = d.choices.filter((c) => c.text.trim())
  if (!d.question.trim()) return { problem: 'noQuestion' }
  if (choices.length < 2) return { problem: 'fewChoices' }
  const correct = choices.filter((c) => c.correct).map((c) => c.id)
  if (!correct.length) return { problem: 'noCorrect' }
  return {
    content: {
      question: textToDoc(d.question),
      choices: choices.map((c) => ({ id: c.id, content: [{ type: 'text', text: c.text.trim() }] })),
      correct,
      multiple: correct.length > 1,
      ...(d.explanation.trim() ? { explanation: textToDoc(d.explanation) } : {}),
    },
  }
}

export function QuizBuilder({ classroomId, open, onClose, onPublished }: { classroomId: string; open: boolean; onClose: () => void; onPublished: () => void }) {
  const t = useTranslations('classes.quiz')
  const client = useApolloClient()
  const mine = useQuery(MyNotesDocument, { variables: { first: 50 }, fetchPolicy: 'cache-and-network', skip: !open })
  const [runTask] = useMutation(RunAiTaskDocument)
  const [publish, publishing] = useMutation(PublishClassQuizDocument)
  const [title, setTitle] = useState('')
  const [drafts, setDrafts] = useState<Draft[]>([])
  const [noteId, setNoteId] = useState('')
  const [sourceNoteId, setSourceNoteId] = useState<string | null>(null)
  const [making, setMaking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const notes = mine.data?.myNotes.edges.map((e) => e.node) ?? []

  const update = (k: string, change: (d: Draft) => Draft) => setDrafts((all) => all.map((d) => (d.key === k ? change(d) : d)))
  const reset = () => {
    setTitle('')
    setDrafts([])
    setNoteId('')
    setSourceNoteId(null)
    setError(null)
  }

  // The AI QUIZ task on one of the teacher's notes (ADR-0059): its quiz cards become questions to edit or drop.
  const make = async () => {
    if (!noteId) return
    setError(null)
    setMaking(true)
    try {
      const res = await runTask({ variables: { input: { noteId, task: 'QUIZ' } } })
      const started = res.data?.runAiTask.artifact
      if (!started) return setError(res.data?.runAiTask.userErrors[0]?.message ?? t('makeFailed'))
      for (;;) {
        await new Promise((r) => setTimeout(r, POLL_MS))
        const { data } = await client.query({ query: AiArtifactDocument, variables: { id: started.id }, fetchPolicy: 'network-only' })
        const a = data?.aiArtifact
        if (!a || a.status === 'FAILED') return setError(a?.error ?? t('makeFailed'))
        if (a.status !== 'READY') continue
        const made = (a.cards ?? []).filter((c) => c.type === 'quiz').map((c) => fromCard(c.content as Parameters<typeof fromCard>[0]))
        if (!made.length) return setError(t('makeFailed'))
        setDrafts((all) => [...all, ...made].slice(0, MAX_QUESTIONS))
        setSourceNoteId(noteId)
        if (!title.trim()) setTitle(notes.find((n) => n.id === noteId)?.title ?? '')
        return
      }
    } catch {
      setError(t('makeFailed'))
    } finally {
      setMaking(false)
    }
  }

  const submit = async () => {
    setError(null)
    if (!title.trim()) return setError(t('needTitle'))
    if (!drafts.length) return setError(t('needQuestion'))
    const cards = drafts.map(toCard)
    const bad = cards.findIndex((c) => 'problem' in c)
    if (bad >= 0) return setError(t(`problem.${(cards[bad] as { problem: string }).problem}`, { n: bad + 1 }))
    const problem = await attempt(() => publish({ variables: { input: { classroomId, title: title.trim(), questions: cards.map((c) => (c as { content: object }).content), ...(sourceNoteId ? { sourceNoteId } : {}) } } }), t('publishFailed'))
    if (problem) return setError(problem)
    reset()
    onPublished()
  }

  return (
    <Dialog open={open} onClose={onClose} title={t('newTitle')} wide persistent>
      <div className="flex flex-col gap-5">
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-semibold">{t('titleLabel')}</span>
          <input value={title} maxLength={120} onChange={(e) => setTitle(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3 text-sm" />
        </label>

        <div className="flex flex-col gap-2 rounded-2xl border border-border bg-surface-2 p-4">
          <div className="flex flex-wrap items-end gap-2">
            <label className="flex min-w-0 flex-1 flex-col gap-1.5">
              <span className="text-sm font-semibold">{t('fromNote')}</span>
              <select value={noteId} onChange={(e) => setNoteId(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3 text-sm">
                <option value="">{t('chooseNote')}</option>
                {notes.map((n) => (
                  <option key={n.id} value={n.id}>
                    {n.title || t('untitled')}
                  </option>
                ))}
              </select>
            </label>
            <Button variant="secondary" className="gap-1.5" disabled={!noteId || making} onClick={() => void make()}>
              {making ? <LoaderCircle className="size-4 animate-spin" aria-hidden /> : <Sparkles className="size-4 text-accent" aria-hidden />}
              {making ? t('making') : t('make')}
            </Button>
          </div>
          <p className="text-xs text-muted">{t('fromNoteHint')}</p>
        </div>

        <ol className="flex flex-col gap-4">
          {drafts.map((d, i) => (
            <li key={d.key} aria-label={t('questionN', { n: i + 1 })} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">{t('questionN', { n: i + 1 })}</span>
                <span className="flex-1" />
                <Button variant="ghost" size="icon" aria-label={t('removeQuestion', { n: i + 1 })} title={t('removeQuestion', { n: i + 1 })} onClick={() => setDrafts((all) => all.filter((x) => x.key !== d.key))}>
                  <Trash className="size-4" aria-hidden />
                </Button>
              </div>
              <textarea aria-label={t('questionText', { n: i + 1 })} value={d.question} rows={2} onChange={(e) => update(d.key, (x) => ({ ...x, question: e.target.value }))} className="rounded-xl border border-border bg-bg p-3 text-sm" />
              <fieldset className="flex flex-col gap-2">
                <legend className="mb-1 text-xs font-semibold text-muted">{t('choicesHint')}</legend>
                {d.choices.map((c, j) => (
                  <div key={c.id} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={c.correct}
                      aria-label={t('correctChoice', { n: j + 1 })}
                      onChange={() => update(d.key, (x) => ({ ...x, choices: x.choices.map((y) => (y.id === c.id ? { ...y, correct: !y.correct } : y)) }))}
                      className="size-4 shrink-0 accent-[var(--accent)]"
                    />
                    <input
                      aria-label={t('choiceText', { n: j + 1 })}
                      value={c.text}
                      onChange={(e) => update(d.key, (x) => ({ ...x, choices: x.choices.map((y) => (y.id === c.id ? { ...y, text: e.target.value } : y)) }))}
                      className="h-10 min-w-0 flex-1 rounded-lg border border-border bg-bg px-3 text-sm"
                    />
                    <Button variant="ghost" size="icon" aria-label={t('removeChoice', { n: j + 1 })} disabled={d.choices.length <= 2} onClick={() => update(d.key, (x) => ({ ...x, choices: x.choices.filter((y) => y.id !== c.id) }))}>
                      <Trash className="size-3.5" aria-hidden />
                    </Button>
                  </div>
                ))}
                {d.choices.length < MAX_CHOICES ? (
                  <Button variant="ghost" size="sm" className="self-start gap-1.5" onClick={() => update(d.key, (x) => ({ ...x, choices: [...x.choices, { id: nextChoiceId(x.choices), text: '', correct: false }] }))}>
                    <Plus className="size-3.5" aria-hidden />
                    {t('addChoice')}
                  </Button>
                ) : null}
              </fieldset>
              <textarea aria-label={t('explanation', { n: i + 1 })} placeholder={t('explanationHint')} value={d.explanation} rows={2} onChange={(e) => update(d.key, (x) => ({ ...x, explanation: e.target.value }))} className="rounded-xl border border-border bg-bg p-3 text-sm" />
            </li>
          ))}
        </ol>
        {drafts.length < MAX_QUESTIONS ? (
          <Button variant="secondary" className="self-start gap-1.5" onClick={() => setDrafts((all) => [...all, blank()])}>
            <Plus className="size-4" aria-hidden />
            {t('addQuestion')}
          </Button>
        ) : null}

        {error ? (
          <p role="alert" className="text-sm text-bad">
            {error}
          </p>
        ) : null}
        <div className="flex justify-end gap-2">
          <Button variant="secondary" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button disabled={publishing.loading || making} onClick={() => void submit()}>
            {t('publish', { n: drafts.length })}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
