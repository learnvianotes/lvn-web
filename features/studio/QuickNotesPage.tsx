'use client'

import { PenLine } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { AiButton } from '@/features/ai/AiPanel'
import { AiResultPanel } from '@/features/ai/AiAction'
import { useStudioAsk } from './useStudioAsk'

/** A scratchpad: one page of rough words, not the full notebook. */
export function QuickNotesPage() {
  const t = useTranslations('studio.quick')
  const [text, setText] = useState('')
  const ai = useStudioAsk(t('noteTitle'), text)
  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-4">
      <header className="flex flex-wrap items-start justify-between gap-3 rounded-3xl border border-teal-700/25 bg-teal-50 px-4 py-4 text-teal-950 dark:bg-teal-950/40 dark:text-teal-50">
        <div className="flex min-w-0 flex-col gap-1">
          <p className="text-xs font-bold uppercase tracking-wider text-teal-800 dark:text-teal-200">{t('kicker')}</p>
          <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight sm:text-3xl">
            <PenLine className="size-7 shrink-0" aria-hidden />
            {t('title')}
          </h1>
          <p className="max-w-md text-sm text-teal-900/80 dark:text-teal-100/80">{t('lead')}</p>
        </div>
        <AiButton onClick={() => void ai.ask()} />
      </header>
      <label className="block">
        <span className="sr-only">{t('label')}</span>
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder={t('placeholder')}
          className="min-h-[52dvh] w-full resize-y rounded-2xl border border-teal-800/20 bg-white px-4 py-4 text-base leading-8 text-slate-900 shadow-inner outline-none focus-visible:border-accent dark:bg-slate-950 dark:text-slate-100"
          style={{ backgroundImage: 'repeating-linear-gradient(transparent, transparent 31px, rgb(20 184 166 / 0.28) 32px)' }}
        />
      </label>
      <AiResultPanel empty={!ai.busy && !ai.result && !ai.error}>
        {ai.busy ? <p className="text-sm text-muted">{t('working')}</p> : null}
        {ai.error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{ai.error}</p> : null}
        {ai.result ? <p className="whitespace-pre-wrap text-sm leading-6">{ai.result}</p> : null}
      </AiResultPanel>
    </div>
  )
}
