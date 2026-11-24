import { BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import type { SubjectSummary } from './data'

const count = (s: SubjectSummary) => s.topics.reduce((n, t) => n + 1 + t.children.length, 0)

/** Subjects as cards, each with how many topics it has, leading to its page (owner, 2026-10-14: no /core). */
export function SubjectGrid({ subjects, headingLevel = 'h2' }: { subjects: SubjectSummary[]; headingLevel?: 'h2' | 'h3' }) {
  const t = useTranslations('subjects')
  const Heading = headingLevel
  return (
    <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {subjects.map((s) => (
        <li key={s.id}>
          <Link href={`/subjects/${s.slug}`} className="group flex h-full items-start gap-3 rounded-2xl border border-border bg-surface p-4 transition hover:border-accent/40 hover:shadow-lg hover:shadow-accent/10">
            <span aria-hidden className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent">
              <BookOpen className="size-5" />
            </span>
            <span className="flex min-w-0 flex-col gap-0.5">
              <Heading className="font-semibold group-hover:text-accent">{s.title}</Heading>
              <span className="text-sm text-muted">{t('topicCount', { count: count(s) })}</span>
            </span>
          </Link>
        </li>
      ))}
    </ul>
  )
}
