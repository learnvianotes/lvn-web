import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Button } from '@/components/ui/button'
import { iconClass } from '@/features/core-content/components/SubjectCard'
import { Breadcrumbs } from '@/features/core-content/components/Breadcrumbs'
import { groupTopics } from '@/features/core-content/group'
import { getCatalog, getSubject } from '@/features/core-content/source'

type Params = { subjectId: string }

export const dynamicParams = false

export function generateStaticParams(): Params[] {
  return getCatalog().subjects.map((s) => ({ subjectId: s.id }))
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const subject = getSubject((await params).subjectId)
  if (!subject) return {}
  return { title: subject.title, description: subject.description, alternates: { canonical: `/core/${subject.id}` } }
}

export default async function SubjectPage({ params }: { params: Promise<Params> }) {
  const subject = getSubject((await params).subjectId)
  if (!subject) notFound()
  const t = await getTranslations('core')
  const first = subject.topics[0]

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <Breadcrumbs items={[{ href: '/core', label: t('allSubjects') }]} />
      <header className="mt-4 flex items-start gap-4">
        <span className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-accent-soft text-accent">
          <i className={`${iconClass(subject.icon)} text-2xl`} aria-hidden />
        </span>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{subject.title}</h1>
          <p className="mt-1 text-muted">{subject.description}</p>
        </div>
      </header>
      {first && (
        <Button asChild className="mt-6">
          <Link href={`/core/${subject.id}/${first.id}`}>{t('start')} <i className="ti ti-arrow-right" aria-hidden /></Link>
        </Button>
      )}
      <div className="mt-10 space-y-8">
        {groupTopics(subject.topics).map(({ group, topics }) => (
          <section key={group || 'topics'}>
            {group && <h2 className="mb-3 text-sm font-semibold uppercase tracking-wider text-muted">{group}</h2>}
            <ol className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
              {topics.map((topic) => (
                <li key={topic.id}>
                  <Link href={`/core/${subject.id}/${topic.id}`} className="flex items-center gap-3 px-4 py-3.5 hover:bg-surface-2">
                    <span className="font-medium">{topic.title}</span>
                    <span className="ml-auto shrink-0 text-xs text-muted">
                      {topic.problems ? t('problems', { count: topic.problems.length }) : null}
                    </span>
                    <i className="ti ti-chevron-right text-muted" aria-hidden />
                  </Link>
                </li>
              ))}
            </ol>
          </section>
        ))}
      </div>
    </div>
  )
}
