'use client'

import { Search } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useMemo, useState } from 'react'
import type { SubjectSummary } from './data'
import { SubjectGrid } from './SubjectGrid'

/** Search and a topic filter over the subject catalogue. */
export function SubjectBrowser({ subjects, initialQuery = '' }: { subjects: SubjectSummary[]; initialQuery?: string }) {
  const t = useTranslations('subjects')
  const [query, setQuery] = useState(initialQuery)
  const [topic, setTopic] = useState('all')
  const topics = useMemo(() => subjects.flatMap((subject) => subject.topics.map((item) => ({ id: item.id, title: item.title, subjectId: subject.id }))), [subjects])
  const q = query.trim().toLowerCase()
  const shown = subjects.filter((subject) => {
    const topicHit = topic === 'all' || subject.topics.some((item) => item.id === topic)
    if (!topicHit) return false
    if (!q) return true
    const haystack = `${subject.title} ${subject.topics.map((item) => `${item.title} ${item.children.map((child) => child.title).join(' ')}`).join(' ')}`.toLowerCase()
    return haystack.includes(q)
  })
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 sm:flex-row">
        <label className="relative min-w-0 flex-1">
          <span className="sr-only">{t('search')}</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t('searchPlaceholder')} className="h-11 w-full rounded-xl border border-border bg-surface pl-9 pr-3 text-sm outline-none focus-visible:ring-2 focus-visible:ring-sky-600" />
        </label>
        <label className="sm:w-64">
          <span className="sr-only">{t('filter')}</span>
          <select value={topic} onChange={(event) => setTopic(event.target.value)} className="h-11 w-full rounded-xl border border-border bg-surface px-3 text-sm">
            <option value="all">{t('filterAll')}</option>
            {topics.map((item) => (
              <option key={item.id} value={item.id}>{item.title}</option>
            ))}
          </select>
        </label>
      </div>
      {shown.length ? <SubjectGrid subjects={shown} /> : <p className="text-sm text-muted">{t('noneMatch')}</p>}
    </div>
  )
}
