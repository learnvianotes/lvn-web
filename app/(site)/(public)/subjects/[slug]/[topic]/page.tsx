import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { getShelf, getSubject, loadSubject, type SubjectSummary } from '@/features/subjects/data'
import { SubjectsDown } from '@/features/subjects/SubjectsDown'
import { Shelf } from '@/features/subjects/Shelf'
import { templated } from '@/lib/page-title'

export const revalidate = 3600

/** A topic of the subject by its slug, with its parent when it is a subtopic. */
function find(subject: SubjectSummary, slug: string) {
  for (const t of subject.topics) {
    if (t.slug === slug) return { topic: t, parent: null }
    const child = t.children.find((c) => c.slug === slug)
    if (child) return { topic: { ...child, children: [] }, parent: t }
  }
  return null
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string; topic: string }> }): Promise<Metadata> {
  const { slug, topic } = await params
  const subject = await getSubject(slug).catch(() => null)
  const found = subject ? find(subject, topic) : null
  const t = await getTranslations('subjects')
  return found && subject ? { title: templated(`${found.topic.title} · ${subject.title}`), description: t('topicLead', { topic: found.topic.title }), alternates: { canonical: `/subjects/${slug}/${topic}` } } : {}
}

/** A topic: its subtopics, and the public notes and resources on it. */
export default async function TopicPage({ params }: { params: Promise<{ slug: string; topic: string }> }) {
  const { slug, topic: topicSlug } = await params
  const loaded = await loadSubject(slug)
  if (loaded.status === 'down') return <SubjectsDown />
  if (loaded.status === 'missing') notFound()
  const subject = loaded.subject
  const found = find(subject, topicSlug)
  if (!found) notFound()
  const { topic, parent } = found
  const t = await getTranslations('subjects')
  const shelf = await getShelf({ topicId: topic.id }).catch(() => ({ notes: [], resources: [] }))
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-10">
      <nav aria-label={t('breadcrumb')} className="flex flex-wrap gap-1 text-sm text-muted">
        <Link href="/subjects" className="hover:text-accent">
          {t('title')}
        </Link>
        <span aria-hidden>›</span>
        <Link href={`/subjects/${subject.slug}`} className="hover:text-accent">
          {subject.title}
        </Link>
        {parent ? (
          <>
            <span aria-hidden>›</span>
            <Link href={`/subjects/${subject.slug}/${parent.slug}`} className="hover:text-accent">
              {parent.title}
            </Link>
          </>
        ) : null}
        <span aria-hidden>›</span>
        <span className="text-fg">{topic.title}</span>
      </nav>
      <header className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight">{topic.title}</h1>
        <p className="max-w-2xl text-muted">{t('topicLead', { topic: topic.title })}</p>
      </header>
      {topic.children.length ? (
        <section aria-labelledby="topic-children" className="flex flex-col gap-2">
          <h2 id="topic-children" className="text-lg font-bold">
            {t('subtopics')}
          </h2>
          <ul className="flex flex-wrap gap-2">
            {topic.children.map((c) => (
              <li key={c.id}>
                <Link href={`/subjects/${subject.slug}/${c.slug}`} className="inline-block rounded-full bg-accent-soft px-3 py-1 text-sm font-medium text-accent hover:underline">
                  {c.title}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <Shelf notes={shelf.notes} resources={shelf.resources} topicTitle={topic.title} />
    </div>
  )
}
