import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { getShelf, getSubject } from '@/features/subjects/data'
import { Shelf } from '@/features/subjects/Shelf'

export const revalidate = 3600

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params
  const subject = await getSubject(slug).catch(() => null)
  const t = await getTranslations('subjects')
  return subject ? { title: subject.title, description: t('subjectLead', { subject: subject.title }), alternates: { canonical: `/subjects/${slug}` } } : {}
}

/** A subject: its topics, each with its own page, and the public notes and resources on it. */
export default async function SubjectPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params
  const subject = await getSubject(slug).catch(() => null)
  if (!subject) notFound()
  const t = await getTranslations('subjects')
  const shelf = await getShelf({ subjectId: subject.id }).catch(() => ({ notes: [], resources: [] }))
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-10">
      <nav aria-label={t('breadcrumb')} className="text-sm text-muted">
        <Link href="/subjects" className="hover:text-accent">
          {t('title')}
        </Link>{' '}
        › <span className="text-fg">{subject.title}</span>
      </nav>
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight">{subject.title}</h1>
        <p className="max-w-2xl text-muted">{t('subjectLead', { subject: subject.title })}</p>
      </header>
      <section aria-labelledby="subject-topics" className="flex flex-col gap-3">
        <h2 id="subject-topics" className="text-lg font-bold">
          {t('topics')}
        </h2>
        <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {subject.topics.map((topic) => (
            <li key={topic.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
              <Link href={`/subjects/${subject.slug}/${topic.slug}`} className="font-semibold hover:text-accent">
                {topic.title}
              </Link>
              {topic.children.length ? (
                <ul className="flex flex-wrap gap-1.5">
                  {topic.children.map((c) => (
                    <li key={c.id}>
                      <Link href={`/subjects/${subject.slug}/${c.slug}`} className="inline-block rounded-full bg-accent-soft px-2.5 py-0.5 text-xs font-medium text-accent hover:underline">
                        {c.title}
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : null}
            </li>
          ))}
        </ul>
      </section>
      <Shelf notes={shelf.notes} resources={shelf.resources} topicTitle={subject.title} />
    </div>
  )
}
