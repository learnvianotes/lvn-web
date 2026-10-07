import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Breadcrumbs } from '@/features/core-content/components/Breadcrumbs'
import { ContentHtml } from '@/features/core-content/components/ContentHtml'
import { PrevNext } from '@/features/core-content/components/PrevNext'
import { ProblemArticle } from '@/features/core-content/components/ProblemArticle'
import { TopicSidebar } from '@/features/core-content/components/TopicSidebar'
import { renderContent } from '@/features/core-content/render'
import { allItems, getProblemSet, getSubject, getTopic, neighbours } from '@/features/core-content/source'

type Params = { subjectId: string; itemId: string }

export const dynamicParams = false

export function generateStaticParams(): Params[] {
  return allItems()
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { subjectId, itemId } = await params
  const subject = getSubject(subjectId)
  const outline = subject?.topics.find((t) => t.id === itemId)
  if (!subject || !outline) return {}
  const description = outline.headings.length
    ? `${outline.title}: ${outline.headings.slice(0, 6).join(', ')}.`
    : `${outline.title} — ${subject.description}`
  return {
    title: `${outline.title} · ${subject.title}`,
    description,
    alternates: { canonical: `/core/${subject.id}/${outline.id}` },
    openGraph: { type: 'article', title: `${outline.title} · ${subject.title}`, description },
  }
}

export default async function ItemPage({ params }: { params: Promise<Params> }) {
  const { subjectId, itemId } = await params
  const subject = getSubject(subjectId)
  const outline = subject?.topics.find((t) => t.id === itemId)
  if (!subject || !outline) notFound()
  const t = await getTranslations('core')
  const { prev, next } = neighbours(subject, itemId)

  let body: React.ReactNode
  let headings: { id: string; text: string }[] = []
  if (subject.kind === 'problems') {
    const set = getProblemSet(itemId)
    if (!set) notFound()
    headings = set.problems.map((p) => ({ id: p.id, text: p.title }))
    body = set.problems.map((p, i) => <ProblemArticle key={p.id} problem={p} index={i + 1} />)
  } else {
    const topic = getTopic(subjectId, itemId)
    if (!topic) notFound()
    const rendered = renderContent(topic.html)
    headings = rendered.headings
    body = <ContentHtml html={rendered.html} />
  }

  return (
    <div className="mx-auto grid max-w-7xl gap-8 px-4 py-8 lg:grid-cols-[16rem_minmax(0,1fr)] xl:grid-cols-[16rem_minmax(0,1fr)_14rem]">
      <TopicSidebar subject={subject} currentId={itemId} label={t('contents')} />
      <article className="min-w-0">
        <Breadcrumbs items={[{ href: '/core', label: t('allSubjects') }, { href: `/core/${subject.id}`, label: subject.title }]} />
        <h1 className="mt-4 text-3xl font-bold tracking-tight text-balance">{outline.title}</h1>
        {headings.length > 1 && (
          <details className="mt-4 rounded-xl border border-border bg-surface xl:hidden">
            <summary className="cursor-pointer px-4 py-3 text-sm font-medium">{t('onThisPage')}</summary>
            <OnThisPage headings={headings} />
          </details>
        )}
        <div className="mt-6">{body}</div>
        <PrevNext subject={subject} prev={prev} next={next} labels={{ previous: t('previous'), next: t('next') }} />
      </article>
      {headings.length > 1 && (
        <aside className="hidden xl:block" aria-label={t('onThisPage')}>
          <div className="sticky top-20 max-h-[calc(100dvh-6rem)] overflow-y-auto">
            <p className="px-3 text-xs font-semibold uppercase tracking-wider text-muted">{t('onThisPage')}</p>
            <OnThisPage headings={headings} />
          </div>
        </aside>
      )}
    </div>
  )
}

function OnThisPage({ headings }: { headings: { id: string; text: string }[] }) {
  return (
    <ol className="space-y-0.5 p-2 text-sm">
      {headings.map((h) => (
        <li key={h.id}>
          <a href={`#${h.id}`} className="block rounded-lg px-3 py-1.5 text-muted hover:bg-surface-2 hover:text-fg">{h.text}</a>
        </li>
      ))}
    </ol>
  )
}
