'use client'

import { BookOpen, Search } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import type { SubjectSummary } from './data'

/** Subjects on Home: a search that opens the catalogue, and the first subjects as their own row. */
export function SubjectSpotlight({ subjects }: { subjects: SubjectSummary[] }) {
  const t = useTranslations('subjects')
  const router = useRouter()
  const [query, setQuery] = useState('')
  const shown = subjects.slice(0, 4)
  return (
    <section aria-labelledby="home-subjects" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <p className="text-xs font-semibold text-accent">{t('homeKicker')}</p>
          <h2 id="home-subjects" className="flex items-center gap-2 text-xl font-semibold">
            <BookOpen className="size-5 text-accent" aria-hidden />
            {t('title')}
          </h2>
        </div>
        <Link href="/subjects" className="text-sm font-semibold text-accent hover:underline">
          {t('browseAll')}
        </Link>
      </div>
      <form
        className="flex gap-2"
        onSubmit={(event) => {
          event.preventDefault()
          router.push(query.trim() ? `/subjects?q=${encodeURIComponent(query.trim())}` : '/subjects')
        }}
      >
        <label className="relative min-w-0 flex-1">
          <span className="sr-only">{t('search')}</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted" aria-hidden />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t('searchPlaceholder')} className="h-11 w-full rounded-xl border border-border bg-surface pl-9 pr-3 text-sm" />
        </label>
        <button type="submit" aria-label={t('search')} className="h-11 shrink-0 rounded-xl bg-accent px-4 text-sm font-semibold text-accent-fg">
          {t('searchGo')}
        </button>
      </form>
      {shown.length ? (
        <ul className="grid gap-2 sm:grid-cols-2">
          {shown.map((subject) => (
            <li key={subject.id}>
              <Link href={`/subjects/${subject.slug}`} className="flex items-center gap-2 rounded-xl border border-accent/20 bg-surface px-3 py-2 text-sm font-semibold hover:border-accent/40">
                <BookOpen className="size-4 shrink-0 text-accent" aria-hidden />
                <span className="truncate">{subject.title}</span>
              </Link>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted">{t('unavailable')}</p>
      )}
    </section>
  )
}
