'use client'

import { useTranslations } from 'next-intl'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

/**
 * The one AI result panel: the same heading and placement under the Ask AI button on notes, quick notes,
 * flashcards and quizzes. The button itself is AiButton (aria name “AI tasks”, visible label “Ask AI”).
 */
export function AiResultPanel({ children, empty, className }: { children?: ReactNode; empty?: boolean; className?: string }) {
  const t = useTranslations('ai')
  return (
    <section aria-label={t('results')} className={cn('flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4', className)}>
      <h3 className="text-sm font-bold uppercase tracking-wide text-muted">{t('results')}</h3>
      {children}
      {empty ? <p className="text-sm text-muted">{t('noResults')}</p> : null}
    </section>
  )
}
