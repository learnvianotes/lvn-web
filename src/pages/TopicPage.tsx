/* ============================================================
   /:subjectId/:topicId
   Notes → one topic with the topic list in the sidebar.
   Problems → every problem of a category, listed in the sidebar.
   ============================================================ */

import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import { Link, NavLink, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, CheckCircle2, RotateCcw } from 'lucide-react'
import { useCatalog, useProblems, useSubject, useTopic } from '@/content/hooks'
import type { Subject, TopicOutline } from '@/content/types'
import { topicKey, uncompleteTopic, useProgress } from '@/progress/store'
import { useReadCompletion } from '@/progress/useReadCompletion'
import { StudyLayout } from '@/components/StudyLayout'
import { Prose } from '@/components/content/Prose'
import { ProblemCard } from '@/components/problem/ProblemCard'
import { LoadError, Loading, NotFound } from '@/components/Status'

export function TopicPage() {
  const { subjectId = '', topicId = '' } = useParams()
  const catalog = useCatalog()
  const subject = useSubject(subjectId)

  if (catalog.status === 'loading') return <Loading />
  if (catalog.status === 'error') return <LoadError error={catalog.error} retry={catalog.retry} />
  const topic = subject?.topics.find((t) => t.id === topicId)
  if (!subject || !topic) return <NotFound />

  return subject.kind === 'problems'
    ? <CategoryView key={topic.id} subject={subject} category={topic} />
    : <NotesView key={topic.id} subject={subject} topic={topic} />
}

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
  const doc = useTopic(subject.id, topic.id)
  const progress = useProgress()
  const done = Boolean(progress.topics[topicKey(subject.id, topic.id)])
  const index = subject.topics.findIndex((t) => t.id === topic.id)
  const prev = subject.topics[index - 1]
  const next = subject.topics[index + 1]

  const endRef = useRef<HTMLDivElement>(null)
  const text = useMemo(
    () => (doc.data ? new DOMParser().parseFromString(doc.data.html, 'text/html').body.textContent ?? '' : undefined),
    [doc.data],
  )
  useReadCompletion({ subjectId: subject.id, topicId: topic.id, text, done, endRef })

  useEffect(() => { window.scrollTo(0, 0) }, [topic.id])

  const sidebar = (
    <ul className="nav-list">
      {subject.topics.map((t, i) => (
        <Fragment key={t.id}>
          {t.group && t.group !== subject.topics[i - 1]?.group && <li className="nav-group">{t.group}</li>}
          <li>
            <NavLink to={`/${subject.id}/${t.id}`} className="nav-item">
              <span className="nav-item-label">{t.title}</span>
              {progress.topics[topicKey(subject.id, t.id)] && <Check size={14} className="nav-done" aria-label="Completed" />}
            </NavLink>
          </li>
        </Fragment>
      ))}
    </ul>
  )

  return (
    <StudyLayout sidebarTitle={<SidebarTitle subject={subject} back={{ to: '/', label: 'All subjects' }} />} sidebar={sidebar}>
      <article className="topic">
        <header className="topic-head">
          {topic.group && <p className="eyebrow">{topic.group}</p>}
          <h1 className="page-title">{topic.title}</h1>
          {done && (
            <button
              className="done-badge"
              onClick={() => uncompleteTopic(subject.id, topic.id)}
              title="Read to the end — click to mark as unread"
            >
              <CheckCircle2 size={14} aria-hidden /> Completed
            </button>
          )}
        </header>
        {doc.status === 'loading' && <Loading />}
        {doc.status === 'error' && <LoadError error={doc.error} retry={doc.retry} />}
        {doc.data && (
          <>
            <Prose html={doc.data.html} />
            <div ref={endRef} aria-hidden />
            <footer className="topic-foot">
              <div className="pager">
                {prev && <Link className="btn" to={`/${subject.id}/${prev.id}`}><ArrowLeft size={14} aria-hidden /> {prev.title}</Link>}
                {next && <Link className="btn" to={`/${subject.id}/${next.id}`}>{next.title} <ArrowRight size={14} aria-hidden /></Link>}
              </div>
            </footer>
          </>
        )}
      </article>
    </StudyLayout>
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
          <p className="muted">{list.length} problems · {solved} solved</p>
        </header>
        {problems.status === 'loading' && <Loading label="Loading problems…" />}
        {problems.status === 'error' && <LoadError error={problems.error} retry={problems.retry} />}
        {problems.data?.map((p, i) => (
          <ProblemCard key={p.id} problem={p} index={i + 1} status={progress.problems[p.id] ?? 'todo'} />
        ))}
      </div>
    </StudyLayout>
  )
}
