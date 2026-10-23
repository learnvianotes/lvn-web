import { BookMarked, Clock, GitFork, NotebookPen, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { NightSky } from '@/components/brand/NightSky'
import { cardPlainText } from '@/lib/contracts/validation'
import { env } from '@/lib/env'
import { accentOf, readingMinutes } from '@/features/notes/look'
import { CardView } from '@/features/notes/render/CardView'
import { QuizTopicsProvider } from '@/features/notes/render/interactive'
import type { PublicNote } from './data'
import { publicNotePath } from './paths'
import { PublicMedia } from './PublicMedia'
import { PublicReadAloud } from './PublicReadAloud'
import { PublicDiscussion } from '@/features/discussion/PublicDiscussion'
import { PublicSaveNoteButton } from '@/features/saved/SaveNoteButton'
import { CreditsLine } from '@/features/workspaces/Credits'
import { StudyAidsView } from '@/features/ai/StudyAids'

/** A public note as anyone sees it (P2d): rendered on the server, cached, readable without an account. */
export async function PublicNoteView({ note }: { note: PublicNote }) {
  const t = await getTranslations('publicNote')
  const words = note.cards.map((c) => ({ id: c.id, text: cardPlainText(c.type, c.content) }))
  const minutes = readingMinutes(words.map((w) => w.text).join(' '))
  const accent = accentOf(note.id)
  const published = note.publishedAt ? new Date(note.publishedAt) : null
  const url = `${env.NEXT_PUBLIC_SITE_URL}${publicNotePath(note)}`
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: note.title,
    author: { '@type': 'Person', name: note.owner.displayName },
    ...(published ? { datePublished: published.toISOString() } : {}),
    url,
    publisher: { '@type': 'Organization', name: 'LearnViaNotes' },
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8 sm:py-12">
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, '\\u003c') }} />
      <header className="flex animate-rise flex-col gap-4">
        {note.topics.length ? (
          <ul className="flex flex-wrap gap-1.5 text-xs" aria-label={t('topics')}>
            {note.topics.map((topic) => (
              <li key={topic.id} className="inline-flex items-center gap-1 rounded-full border border-border bg-surface px-2.5 py-1 text-muted">
                <BookMarked className="size-3.5" aria-hidden />
                {topic.title} · {topic.subject.title}
              </li>
            ))}
          </ul>
        ) : null}
        <h1 className="text-3xl font-extrabold leading-tight tracking-tight sm:text-[2.75rem]">{note.title || t('untitled')}</h1>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
          <span className="flex items-center gap-2">
            <span className="grid size-9 place-items-center rounded-full text-sm font-bold text-white shadow-sm" style={{ background: `linear-gradient(135deg, ${accent.from}, ${accent.to})` }} aria-hidden>
              {note.owner.displayName.charAt(0).toUpperCase()}
            </span>
            <span>
              <span className="font-medium text-fg">{note.owner.displayName}</span> <span>@{note.owner.handle}</span>
            </span>
          </span>
          {published ? <time dateTime={published.toISOString()}>· {published.toLocaleDateString('en', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' })}</time> : null}
          {minutes ? (
            <span className="inline-flex items-center gap-1">
              · <Clock className="size-3.5" aria-hidden /> {t('readingTime', { n: minutes })}
            </span>
          ) : null}
        </div>
        {note.forkedFrom ? (
          <p className="inline-flex items-center gap-1 text-xs text-muted">
            <GitFork className="size-3.5" aria-hidden />
            {note.forkedFrom.title ? t('copiedFrom', { title: note.forkedFrom.title, name: note.forkedFrom.author.displayName }) : t('copiedFromAuthor', { name: note.forkedFrom.author.displayName })}
          </p>
        ) : null}
        {note.contributors?.length ? <CreditsLine credits={note.contributors} /> : null}
        <div className="flex w-fit flex-wrap items-center gap-2">
          <PublicReadAloud cards={words} />
          <PublicSaveNoteButton noteId={note.id} />
        </div>
      </header>

      <PublicMedia noteId={note.id} hasMedia={note.cards.some((c) => c.hasMedia)}>
        <QuizTopicsProvider topicKeys={note.topics.map((topic) => `topic:${topic.id}`)}>
          <article className="flex flex-col gap-5 rounded-3xl border border-border bg-surface px-5 py-7 text-[1.0625rem] leading-relaxed shadow-sm sm:px-10">
            {note.cards.map((c) => (
              <CardView key={c.id} id={c.id} type={c.type} content={c.content} />
            ))}
            {!note.cards.length ? <p className="text-muted">{t('empty')}</p> : null}
          </article>
        </QuizTopicsProvider>
      </PublicMedia>
      {/* Study aids made when it was published (lvn-backend ADR-0061); saving their cards happens in the app. */}
      <StudyAidsView aids={note.aiInsights ?? []} keepHref={`/notes/${note.id}`} />
      <PublicDiscussion noteId={note.id} />

      <NightSky as="section" className="rounded-3xl px-6 py-7 sm:px-8">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex flex-col gap-1">
            <p className="flex items-center gap-1.5 text-sm font-medium text-inverse-muted">
              <Sparkles className="size-4" aria-hidden />
              {t('ctaKicker')}
            </p>
            <p className="text-xl font-bold">{t('ctaTitle')}</p>
            <p className="text-sm text-inverse-muted">{t('ctaLead')}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Link href="/sign-up" className="inline-flex items-center gap-2 rounded-full bg-inverse-ink px-4 py-2 text-sm font-semibold text-inverse hover:opacity-90">
              <NotebookPen className="size-4" aria-hidden />
              {t('ctaStart')}
            </Link>
            <Link href={`/notes/${note.id}`} className="inline-flex items-center rounded-full px-4 py-2 text-sm font-semibold ring-1 ring-inverse-ink/40 hover:bg-white/10">
              {t('ctaOpen')}
            </Link>
          </div>
        </div>
      </NightSky>
      <p className="text-center text-xs text-muted">
        {t('reportLead')}{' '}
        <Link href={`/notes/${note.id}`} className="underline hover:text-fg">
          {t('reportLink')}
        </Link>
      </p>
    </div>
  )
}
