'use client'

import { useTranslations } from 'next-intl'
import { useState } from 'react'
import type { Doc, Inline } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { InlineText, RichDoc } from './RichText'

/** Cards a reader does something with: reveal an answer, answer a quiz, flip a flashcard. Nothing is sent anywhere. */

export function QuestionCardView({ content }: { content: { prompt: Doc; answer: Doc; hint?: Doc } }) {
  const t = useTranslations('notes.reader')
  const [hint, setHint] = useState(false)
  const [open, setOpen] = useState(false)
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-border bg-surface p-4">
      <RichDoc doc={content.prompt} className="flex flex-col gap-2 font-medium" />
      {content.hint ? (
        hint ? (
          <RichDoc doc={content.hint} className="flex flex-col gap-2 text-sm text-muted" />
        ) : (
          <button type="button" className="self-start text-sm text-accent hover:underline" onClick={() => setHint(true)}>
            {t('showHint')}
          </button>
        )
      ) : null}
      {open ? (
        <div className="rounded-lg bg-accent-soft p-3">
          <RichDoc doc={content.answer} />
        </div>
      ) : (
        <button type="button" className="self-start rounded-full border border-border px-4 py-1.5 text-sm font-medium hover:bg-surface-2" onClick={() => setOpen(true)}>
          {t('showAnswer')}
        </button>
      )}
    </div>
  )
}

export function QuizCardView({ content }: { content: { question: Doc; choices: { id: string; content: Inline }[]; correct: string[]; multiple: boolean; explanation?: Doc } }) {
  const t = useTranslations('notes.reader')
  const [picked, setPicked] = useState<string[]>([])
  const [checked, setChecked] = useState(false)
  const right = checked && picked.length === content.correct.length && picked.every((p) => content.correct.includes(p))
  const toggle = (id: string) => {
    if (checked) return
    setPicked((p) => (content.multiple ? (p.includes(id) ? p.filter((x) => x !== id) : [...p, id]) : [id]))
  }
  return (
    <fieldset className="flex flex-col gap-2 rounded-xl border border-border bg-surface p-4">
      <legend className="sr-only">{t('quiz')}</legend>
      <RichDoc doc={content.question} className="flex flex-col gap-2 font-medium" />
      <ul className="flex flex-col gap-1.5">
        {content.choices.map((c) => {
          const isPicked = picked.includes(c.id)
          const isCorrect = content.correct.includes(c.id)
          return (
            <li key={c.id}>
              <button
                type="button"
                role={content.multiple ? 'checkbox' : 'radio'}
                aria-checked={isPicked}
                className={cn(
                  'w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors',
                  !checked && (isPicked ? 'border-accent bg-accent-soft' : 'border-border hover:bg-surface-2'),
                  checked && isCorrect && 'border-emerald-500 bg-emerald-500/10',
                  checked && isPicked && !isCorrect && 'border-red-500 bg-red-500/10',
                  checked && !isPicked && !isCorrect && 'border-border opacity-70',
                )}
                onClick={() => toggle(c.id)}
              >
                <InlineText content={c.content} />
              </button>
            </li>
          )
        })}
      </ul>
      {checked ? (
        <div role="status" className="flex flex-col gap-2 text-sm">
          <p className={cn('font-semibold', right ? 'text-emerald-700 dark:text-emerald-400' : 'text-red-700 dark:text-red-400')}>{right ? t('correct') : t('notQuite')}</p>
          {content.explanation ? <RichDoc doc={content.explanation} /> : null}
          <button type="button" className="self-start text-accent hover:underline" onClick={() => (setChecked(false), setPicked([]))}>
            {t('tryAgain')}
          </button>
        </div>
      ) : (
        <button type="button" disabled={!picked.length} className="self-start rounded-full bg-accent px-4 py-1.5 text-sm font-semibold text-accent-fg disabled:opacity-50" onClick={() => setChecked(true)}>
          {t('check')}
        </button>
      )}
    </fieldset>
  )
}

export function FlashcardCardView({ content }: { content: { front: Doc; back: Doc } }) {
  const t = useTranslations('notes.reader')
  const [back, setBack] = useState(false)
  return (
    <button
      type="button"
      aria-pressed={back}
      aria-label={back ? t('flashcardBack') : t('flashcardFront')}
      className="flex min-h-32 w-full flex-col items-center justify-center gap-2 rounded-xl border border-border bg-surface p-6 text-center hover:bg-surface-2"
      onClick={() => setBack((b) => !b)}
    >
      <RichDoc doc={back ? content.back : content.front} className="flex flex-col gap-2 text-lg" />
      <span className="text-xs text-muted">{back ? t('tapForFront') : t('tapForBack')}</span>
    </button>
  )
}
