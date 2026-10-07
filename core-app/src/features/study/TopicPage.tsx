/* ============================================================
   /:subjectId/:topicId
   Notes → one topic with the topic list in the sidebar.
   Problems → every problem of a category, listed in the sidebar.
   ============================================================ */

import './study.css'
import { Fragment, useEffect, useRef, useState } from 'react'
import { Link, NavLink, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, RotateCcw } from 'lucide-react'
import { useCatalog, useProblems, useSubject, useTopic } from '@core/features/catalog/hooks'
import { content } from '@core/features/catalog/source'
import type { Subject, TopicOutline } from '@core/features/catalog/types'
import { topicKey, useProgress } from '@core/features/progress/store'
import { StudyLayout } from '@core/features/study/StudyLayout'
import { ContentView } from '@core/features/content/ContentView'
import { ProblemCard } from '@core/features/study/problems/ProblemCard'
import { LoadError, Loading, NotFound } from '@core/shared/ui/Status'

export function TopicPage() {
  const { subjectId = '', topicId = '' } = useParams()
  const catalog = useCatalog()
  const subject = useSubject(subjectId)

  if (catalog.status === 'loading') return <Loading />
  if (catalog.status === 'error') return <LoadError error={catalog.error} retry={catalog.retry} />
  const topic = subject?.topics.find((t) => t.id === topicId)
  if (!subject || !topic) return <NotFound />

  // Notes: the layout and sidebar stay mounted while moving between topics (keeping the sidebar's
  // scroll position); only the article is swapped. Problem categories each have their own list.
  return subject.kind === 'problems'
    ? <CategoryView key={topic.id} subject={subject} category={topic} />
    : <NotesView subject={subject} topic={topic} />
}

/** Loads a topic into the cache (memory + IndexedDB) without rendering it. */
const prefetchTopic = (subjectId: string, topicId: string) => content.topic(subjectId, topicId).catch(() => undefined)

function SidebarTitle({ subject, back }: { subject: Subject; back: { to: string; label: string } }) {
  return (
    <>
      <Link to={back.to} className="back-link"><ArrowLeft size={14} aria-hidden /> {back.label}</Link>
      <span className="ws-subject">{subject.title}</span>
    </>
  )
}

/* ── Notes ───────────────────────────────────────────────── */

function NotesView({ subject, topic }: { subject: Subject; topic: TopicOutline }) {
  const progress = useProgress()

  const sidebar = (
    <ul className="nav-list">
      {subject.topics.map((t, i) => (
        <Fragment key={t.id}>
          {t.group && t.group !== subject.topics[i - 1]?.group && <li className="nav-group">{t.group}</li>}
          <li>
            <NavLink to={`/${subject.id}/${t.id}`} className="nav-item">
              <span className="nav-item-label">{t.title}</span>
              {progress.revisitTopics[topicKey(subject.id, t.id)] && <RotateCcw size={13} className="nav-revisit" aria-label="Revisit" />}
              {progress.topics[topicKey(subject.id, t.id)] && <Check size={14} className="nav-done" aria-label="Completed" />}
            </NavLink>
          </li>
        </Fragment>
      ))}
    </ul>
  )

  return (
    <StudyLayout sidebarTitle={<SidebarTitle subject={subject} back={{ to: '/', label: 'All subjects' }} />} sidebar={sidebar}>
      <NotesArticle key={topic.id} subject={subject} topic={topic} />
    </StudyLayout>
  )
}

/** One topic's content — remounted per topic, so tracking and loading start fresh. */
function NotesArticle({ subject, topic }: { subject: Subject; topic: TopicOutline }) {
  const doc = useTopic(subject.id, topic.id)
  const index = subject.topics.findIndex((t) => t.id === topic.id)
  const prev = subject.topics[index - 1]
  const next = subject.topics[index + 1]

  const articleRef = useRef<HTMLElement>(null)

  useEffect(() => { window.scrollTo(0, 0) }, [topic.id])

  // Once this topic is in, warm the cache for the neighbours so Next / Previous open instantly.
  const loaded = doc.status === 'ready'
  useEffect(() => {
    if (!loaded) return
    const id = window.setTimeout(() => {
      for (const t of [next, prev]) if (t) void prefetchTopic(subject.id, t.id)
    }, 600)
    return () => window.clearTimeout(id)
  }, [loaded, subject.id, next, prev])

  return (
    <article className="topic" ref={articleRef}>
      <header className="topic-head">
        {topic.group && <p className="eyebrow">{topic.group}</p>}
        <h1 className="page-title">{topic.title}</h1>
      </header>
      {doc.status === 'loading' && <Loading />}
      {doc.status === 'error' && <LoadError error={doc.error} retry={doc.retry} />}
      {doc.data && (
        <>
          <ContentView content={doc.data.content} anchors />
          <footer className="topic-foot">
            <div className="pager">
              {prev && <Link className="btn" to={`/${subject.id}/${prev.id}`}><ArrowLeft size={14} aria-hidden /> {prev.title}</Link>}
              {next && <Link className="btn" to={`/${subject.id}/${next.id}`}>{next.title} <ArrowRight size={14} aria-hidden /></Link>}
            </div>
          </footer>
        </>
      )}
    </article>
  )
}

/* ── Problem category ────────────────────────────────────── */

function CategoryView({ subject, category }: { subject: Subject; category: TopicOutline }) {
  const problems = useProblems(subject.id, category.id)
  const progress = useProgress()
  const location = useLocation()
  const [activeId, setActiveId] = useState<string>()
  const list = category.problems ?? []
  const solved = list.filter((p) => progress.problems[p.id] === 'solved').length

  // Jump to #lc-… once the cards exist.
  useEffect(() => {
    if (problems.status !== 'ready') return
    const id = location.hash.slice(1)
    const el = id ? document.getElementById(id) : null
    if (el) el.scrollIntoView({ block: 'start' })
    else window.scrollTo(0, 0)
  }, [problems.status, location.hash])

  // Highlight the problem currently at the top of the viewport.
  useEffect(() => {
    if (problems.status !== 'ready') return
    let frame = 0
    const onScroll = () => {
      cancelAnimationFrame(frame)
      frame = requestAnimationFrame(() => {
        const cards = [...document.querySelectorAll<HTMLElement>('.problem-card')]
        const current = cards.filter((c) => c.getBoundingClientRect().top <= 140).pop() ?? cards[0]
        setActiveId(current?.id)
      })
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => { cancelAnimationFrame(frame); window.removeEventListener('scroll', onScroll) }
  }, [problems.status])

  const sidebar = (
    <ul className="nav-list">
      <li className="nav-group">{category.title} · {solved}/{list.length}</li>
      {list.map((p, i) => {
        const status = progress.problems[p.id]
        return (
          <li key={p.id}>
            <a href={`#${p.id}`} className={`nav-item ${activeId === p.id ? 'active' : ''}`} aria-current={activeId === p.id ? 'true' : undefined}>
              <span className="nav-num">{i + 1}</span>
              <span className="nav-item-label">{p.title}</span>
              {status === 'solved' && <Check size={14} className="nav-done" aria-label="Solved" />}
              {status === 'revisit' && <RotateCcw size={13} className="nav-revisit" aria-label="Revisit" />}
              <span className={`dot dot--${p.difficulty.toLowerCase()}`} title={p.difficulty} />
            </a>
          </li>
        )
      })}
    </ul>
  )

  return (
    <StudyLayout
      sidebarTitle={<SidebarTitle subject={subject} back={{ to: `/${subject.id}`, label: subject.title }} />}
      sidebar={sidebar}
    >
      <div className="topic">
        <header className="topic-head">
          <p className="eyebrow">{subject.title}</p>
          <h1 className="page-title">{category.title}</h1>
          <p className="muted">{list.length} problems</p>
        </header>
        {problems.status === 'loading' && <Loading label="Loading problems…" />}
        {problems.status === 'error' && <LoadError error={problems.error} retry={problems.retry} />}
        {problems.data?.map((p, i) => (
          <ProblemCard key={p.id} problem={p} index={i + 1} status={progress.problems[p.id] ?? 'todo'} signedIn={false} />
        ))}
      </div>
    </StudyLayout>
  )
}
