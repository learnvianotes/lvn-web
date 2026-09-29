/* ============================================================
   /:subjectId/:topicId
   Notes → one topic with the topic list in the sidebar.
   Problems → every problem of a category, listed in the sidebar.
   ============================================================ */

import './study.css'
import { Fragment, useEffect, useMemo, useRef, useState } from 'react'
import { Link, NavLink, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, Check, CheckCircle2, RotateCcw } from 'lucide-react'
import { useCatalog, useProblems, useSubject, useTopic } from '@/features/catalog/hooks'
import type { Subject, TopicOutline } from '@/features/catalog/types'
import { toggleTopicRevisit, topicKey, uncompleteTopic, useProgress } from '@/features/progress/store'
import { useStudyTime } from '@/features/progress/useStudyTime'
import { useReadCompletion } from '@/features/progress/useReadCompletion'
import { StudyLayout } from '@/features/study/StudyLayout'
import { ContentView } from '@/features/content/ContentView'
import { plainText } from '@/features/content/query'
import { ProblemCard } from '@/features/study/problems/ProblemCard'
import { LoadError, Loading, NotFound } from '@/shared/ui/Status'
import { StudyKit } from '@/features/study/kit/StudyKit'
import { ListenButton } from '@/features/voice/ListenButton'
import { segmentsFrom } from '@/features/voice/speech'
import { useUser } from '@/features/auth/auth'
import { UnlockHint } from '@/features/auth/UnlockHint'

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
  const user = useUser()
  const key = topicKey(subject.id, topic.id)
  const done = Boolean(progress.topics[key])
  const revisit = Boolean(progress.revisitTopics[key])
  const index = subject.topics.findIndex((t) => t.id === topic.id)
  const prev = subject.topics[index - 1]
  const next = subject.topics[index + 1]

  const endRef = useRef<HTMLDivElement>(null)
  const text = useMemo(
    () => (doc.data ? plainText(doc.data.content) : undefined),
    [doc.data],
  )
  // Tracking (completion, time, history) is for signed-in learners only.
  useReadCompletion({ subjectId: subject.id, topicId: topic.id, text, done: done || !user, endRef })
  useStudyTime({ subjectId: subject.id, topicId: topic.id, title: topic.title, subjectTitle: subject.title, enabled: Boolean(user) })
  const articleRef = useRef<HTMLElement>(null)

  useEffect(() => { window.scrollTo(0, 0) }, [topic.id])

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
      <article className="topic" ref={articleRef}>
        <header className="topic-head">
          {topic.group && <p className="eyebrow">{topic.group}</p>}
          <h1 className="page-title">{topic.title}</h1>
          {user ? (
          <div className="topic-tools">
            {done && (
              <button
                className="done-badge"
                onClick={() => uncompleteTopic(subject.id, topic.id)}
                title="Read to the end — click to mark as unread"
              >
                <CheckCircle2 size={14} aria-hidden /> Completed
              </button>
            )}
            {doc.data && (
              <ListenButton
                title={topic.title}
                segments={() => {
                  const body = articleRef.current?.querySelector<HTMLElement>('.prose')
                  return [{ text: `${topic.title}.`, el: articleRef.current?.querySelector('h1') }, ...(body ? segmentsFrom(body) : [])]
                }}
              />
            )}
            <button
              className={`btn btn-sm revisit-btn ${revisit ? 'is-on' : ''}`}
              onClick={() => toggleTopicRevisit(subject.id, topic.id)}
              aria-pressed={revisit}
              title="Add to your review queue"
            >
              <RotateCcw size={13} aria-hidden /> {revisit ? 'Marked to revisit' : 'Revisit later'}
            </button>
          </div>
          ) : (
            <UnlockHint />
          )}
        </header>
        {doc.status === 'loading' && <Loading />}
        {doc.status === 'error' && <LoadError error={doc.error} retry={doc.retry} />}
        {doc.data && (
          <>
            {user && <StudyKit content={doc.data.content} title={topic.title} noteKey={key} subjectId={subject.id} topicId={topic.id} />}
            <ContentView content={doc.data.content} anchors />
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
  const user = useUser()
  useStudyTime({ subjectId: subject.id, topicId: category.id, title: category.title, subjectTitle: subject.title, enabled: Boolean(user) })

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
          <p className="muted">{list.length} problems{user ? ` · ${solved} solved` : ''}</p>
          {!user && <UnlockHint />}
        </header>
        {problems.status === 'loading' && <Loading label="Loading problems…" />}
        {problems.status === 'error' && <LoadError error={problems.error} retry={problems.retry} />}
        {problems.data?.map((p, i) => (
          <ProblemCard key={p.id} problem={p} index={i + 1} status={progress.problems[p.id] ?? 'todo'} signedIn={Boolean(user)} />
        ))}
      </div>
    </StudyLayout>
  )
}
