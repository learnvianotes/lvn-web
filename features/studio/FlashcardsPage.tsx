'use client'

import { Layers, RotateCcw } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { AiButton } from '@/features/ai/AiPanel'
import { AiResultPanel } from '@/features/ai/AiAction'
import { cn } from '@/lib/cn'
import { useStudioAsk } from './useStudioAsk'

const STARTER = [
  { front: 'What does a flashcard ask you to do?', back: 'Recall the answer before you turn it over.' },
  { front: 'When do you flip the card?', back: 'After you have tried to remember, not before.' },
  { front: 'Where do cards from a note live?', back: 'On the note’s Flashcards tab, and in Review.' },
]

/** A deck you study one card at a time, separate from the notebook. */
export function FlashcardsPage() {
  const t = useTranslations('studio.cards')
  const [at, setAt] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const card = STARTER[at] ?? STARTER[0]!
  const ai = useStudioAsk(t('noteTitle'), STARTER.map((item) => `${item.front} — ${item.back}`).join('\n'))
  const go = (next: number) => {
    setAt((next + STARTER.length) % STARTER.length)
    setFlipped(false)
  }
  return (
    <div className="mx-auto flex w-full max-w-lg flex-col gap-4">
      <header className="flex flex-wrap items-start justify-between gap-3 rounded-3xl border border-emerald-700/25 bg-emerald-50 px-4 py-4 text-emerald-950 dark:bg-emerald-950/40 dark:text-emerald-50">
        <div className="flex min-w-0 flex-col gap-1">
          <p className="text-xs font-semibold">{t('kicker')}</p>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight sm:text-3xl">
            <Layers className="size-7 shrink-0" aria-hidden />
            {t('title')}
          </h1>
          <p className="text-sm text-emerald-900/80 dark:text-emerald-100/80">{t('lead')}</p>
        </div>
        <AiButton onClick={() => void ai.ask()} />
      </header>
      <p className="text-center text-xs font-semibold text-emerald-800 dark:text-emerald-200">{t('progress', { n: at + 1, total: STARTER.length })}</p>
      <button
        type="button"
        onClick={() => setFlipped((value) => !value)}
        className={cn('flex min-h-56 flex-col items-center justify-center rounded-3xl border-2 px-6 py-8 text-center shadow-lg transition', flipped ? 'border-emerald-700 bg-emerald-800 text-white' : 'border-emerald-600/40 bg-white text-slate-900 dark:bg-slate-950 dark:text-slate-50')}
        aria-pressed={flipped}
      >
        <span className="text-xs font-semibold opacity-70">{flipped ? t('back') : t('front')}</span>
        <span className="mt-3 text-xl font-semibold leading-snug sm:text-2xl">{flipped ? card.back : card.front}</span>
      </button>
      <div className="flex flex-wrap items-center justify-center gap-2">
        <Button type="button" variant="secondary" onClick={() => go(at - 1)}>
          {t('previous')}
        </Button>
        <Button type="button" variant="secondary" className="gap-1.5" onClick={() => setFlipped((value) => !value)}>
          <RotateCcw className="size-4" aria-hidden />
          {t('flip')}
        </Button>
        <Button type="button" onClick={() => go(at + 1)}>
          {t('next')}
        </Button>
      </div>
      <AiResultPanel empty={!ai.busy && !ai.result && !ai.error}>
        {ai.busy ? <p className="text-sm text-muted">{t('working')}</p> : null}
        {ai.error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{ai.error}</p> : null}
        {ai.result ? <p className="whitespace-pre-wrap text-sm leading-6">{ai.result}</p> : null}
      </AiResultPanel>
    </div>
  )
}
