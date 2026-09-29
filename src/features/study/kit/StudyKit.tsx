/* ============================================================
   StudyKit — revision aids above a topic, built automatically
   from its content (study/extract.ts):
     Quick notes · Side headings · Remember · My notes
   The quick notes can be listened to or copied.
   Starts collapsed on every topic — the notes come first; the
   kit opens only when the learner asks for it.
   ============================================================ */

import './kit.css'
import { useEffect, useMemo, useRef, useState } from 'react'
import { BookmarkCheck, ChevronDown, Copy, Headphones, ListTree, NotebookPen, Sparkles, Lightbulb } from 'lucide-react'
import { get, set } from '@/services/storage'
import { useUser } from '@/features/auth/auth'
import { NOTE_MAX, saveNote, useNote } from '@/features/progress/notes'
import { speak, speechSupported, type Segment } from '@/features/voice/speech'
import type { Content } from '@schema/content'
import { buildStudyKit, recapText, type StudyKit as Kit } from '@/features/study/kit/extract'
import { track } from '@/features/telemetry/track'

type Tab = 'notes' | 'outline' | 'remember' | 'mine'

const TABS: { id: Tab; label: string; icon: typeof Sparkles }[] = [
  { id: 'notes', label: 'Quick notes', icon: Sparkles },
  { id: 'outline', label: 'Side headings', icon: ListTree },
  { id: 'remember', label: 'Remember', icon: Lightbulb },
  { id: 'mine', label: 'My notes', icon: NotebookPen },
]

const CALLOUT_LABEL = { def: 'Definition', note: 'Key point', warn: 'Watch out', good: 'Do', bad: 'Avoid', example: 'Example' } as const

interface Props {
  content: Content
  title: string
  noteKey: string
  subjectId: string
  topicId: string
}

export function StudyKit({ content, title, noteKey, subjectId, topicId }: Props) {
  const kit = useMemo(() => buildStudyKit(content), [content])
  const [open, setOpen] = useState(false)
  const [tab, setTab] = useState<Tab>(() => get<Tab>('kit-tab') ?? 'notes')
  const minutes = Math.max(1, Math.round(kit.words / 230))

  const toggle = () => {
    if (!open) track('kit_open', { s: subjectId, k: topicId, l: tab })
    setOpen(!open)
  }
  const choose = (t: Tab) => {
    set('kit-tab', t)
    setTab(t)
    if (!open) setOpen(true)
    track('kit_open', { s: subjectId, k: topicId, l: t })
  }

  if (!kit.sections.length && !kit.terms.length && !kit.remember.length) return null

  return (
    <section className={`study-kit ${open ? 'is-open' : ''}`} aria-label="Study kit">
      <header className="kit-head">
        <button className="kit-toggle" onClick={toggle} aria-expanded={open}>
          <span className="kit-badge"><Sparkles size={14} aria-hidden /></span>
          <span className="kit-heading">
            <strong>Smart study kit</strong>
            <span className="muted small">Auto-generated · {kit.sections.length} sections · ~{minutes} min read</span>
          </span>
          <ChevronDown size={16} className="kit-chevron" aria-hidden />
        </button>
      </header>
      {open && (
        <>
          <div className="kit-tabs" role="tablist">
            {TABS.map((t) => (
              <button key={t.id} role="tab" aria-selected={tab === t.id} className="kit-tab" onClick={() => choose(t.id)}>
                <t.icon size={14} aria-hidden /> {t.label}
              </button>
            ))}
          </div>
          <div className="kit-body" role="tabpanel">
            {tab === 'notes' && <QuickNotes kit={kit} title={title} />}
            {tab === 'outline' && <Outline kit={kit} />}
            {tab === 'remember' && <Remember kit={kit} />}
            {tab === 'mine' && <MyNotes noteKey={noteKey} />}
          </div>
        </>
      )}
    </section>
  )
}

function scrollToSection(id: string) {
  const el = document.getElementById(id)
  if (!el) return
  // A section inside a hidden tab: switch to that tab first.
  const panel = el.closest<HTMLElement>('.tab-panel')
  if (panel?.hidden) {
    const tabs = panel.parentElement!
    const i = [...tabs.querySelectorAll(':scope > .tab-panel')].indexOf(panel)
    tabs.querySelectorAll<HTMLButtonElement>(':scope > .tab-bar > button')[i]?.click()
  }
  el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  el.classList.add('is-flash')
  window.setTimeout(() => el.classList.remove('is-flash'), 1600)
}

function QuickNotes({ kit, title }: { kit: Kit; title: string }) {
  const [copied, setCopied] = useState(false)
  const listen = () => {
    const segs: Segment[] = [{ text: `Here's a quick recap of ${title}.` }]
    if (kit.lead) segs.push({ text: kit.lead })
    for (const s of kit.sections) {
      if (!s.points.length) continue
      const anchor = document.getElementById(s.id)
      const el = anchor?.matches('.tab-panel') ? anchor : anchor?.parentElement
      segs.push({ text: `${s.title}.`, el })
      s.points.forEach((p) => segs.push({ text: p, el }))
    }
    if (kit.terms.length) segs.push({ text: `Key terms to remember: ${kit.terms.slice(0, 10).join(', ')}.` })
    speak(`Recap · ${title}`, segs)
  }
  const copy = () => {
    void navigator.clipboard?.writeText(recapText(title, kit)).then(() => {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    })
  }
  return (
    <>
      <div className="kit-actions">
        {speechSupported && <button className="btn btn-sm" onClick={listen}><Headphones size={14} aria-hidden /> Explain it to me</button>}
        <button className="btn btn-sm" onClick={copy}><Copy size={14} aria-hidden /> {copied ? 'Copied' : 'Copy notes'}</button>
      </div>
      {kit.lead && <p className="kit-lead">{kit.lead}</p>}
      {!kit.sections.some((s) => s.points.length) && <p className="muted small">This topic is short — see the Remember tab for its key points.</p>}
      <div className="kit-notes">
        {kit.sections.filter((s) => s.points.length).map((s) => (
          <div key={s.id} className="kit-note">
            <button className="kit-note-title" onClick={() => scrollToSection(s.id)}>{s.title}</button>
            <ul>{s.points.map((p) => <li key={p}>{p}</li>)}</ul>
          </div>
        ))}
      </div>
    </>
  )
}

function Outline({ kit }: { kit: Kit }) {
  const [active, setActive] = useState<string>()
  useEffect(() => {
    const els = kit.sections.map((s) => document.getElementById(s.id)).filter(Boolean) as HTMLElement[]
    const obs = new IntersectionObserver(
      (entries) => {
        const top = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0]
        if (top) setActive(top.target.id)
      },
      { rootMargin: '-80px 0px -60% 0px' },
    )
    els.forEach((el) => obs.observe(el))
    return () => obs.disconnect()
  }, [kit])
  return (
    <ol className="kit-outline">
      {kit.sections.map((s, i) => (
        <li key={s.id}>
          <button className={active === s.id ? 'is-active' : ''} onClick={() => scrollToSection(s.id)}>
            <span className="kit-outline-num">{i + 1}</span>{s.title}
          </button>
        </li>
      ))}
    </ol>
  )
}

function Remember({ kit }: { kit: Kit }) {
  return (
    <>
      {kit.terms.length > 0 && (
        <>
          <p className="kit-label">Key terms</p>
          <div className="kit-terms">{kit.terms.map((t) => <span key={t} className="kit-term">{t}</span>)}</div>
        </>
      )}
      {kit.remember.length > 0 && (
        <>
          <p className="kit-label">Must remember</p>
          <ul className="kit-remember">
            {kit.remember.map((r, i) => (
              <li key={i} className={`kit-callout kit-callout--${r.kind}`}>
                <span className="kit-callout-label"><BookmarkCheck size={12} aria-hidden /> {r.label || CALLOUT_LABEL[r.kind]}</span>
                {r.text}
              </li>
            ))}
          </ul>
        </>
      )}
      {!kit.terms.length && !kit.remember.length && <p className="muted small">No highlighted terms in this topic.</p>}
    </>
  )
}

function MyNotes({ noteKey }: { noteKey: string }) {
  const note = useNote(noteKey)
  const user = useUser()
  const [text, setText] = useState(note?.text ?? '')
  const [saved, setSaved] = useState(true)
  const timer = useRef(0)

  // Pick up changes synced from another device while not typing.
  useEffect(() => { if (saved) setText(note?.text ?? '') }, [note, saved])
  useEffect(() => () => window.clearTimeout(timer.current), [])

  const onChange = (v: string) => {
    setText(v)
    setSaved(false)
    window.clearTimeout(timer.current)
    timer.current = window.setTimeout(() => { saveNote(noteKey, v); setSaved(true) }, 600)
    if (!text) track('note_save', { i: noteKey })
  }

  return (
    <div className="kit-mine">
      <textarea
        value={text}
        onChange={(e) => onChange(e.target.value)}
        onBlur={() => { if (!saved) { window.clearTimeout(timer.current); saveNote(noteKey, text); setSaved(true) } }}
        placeholder="Jot down what you want to remember — formulas, gotchas, interview answers…"
        maxLength={NOTE_MAX}
        rows={6}
        aria-label="My notes for this topic"
      />
      <p className="muted small">
        {saved ? (user ? 'Saved · synced to your account' : 'Saved on this device · sign in to sync') : 'Saving…'}
        <span className="kit-count">{text.length}/{NOTE_MAX}</span>
      </p>
    </div>
  )
}
