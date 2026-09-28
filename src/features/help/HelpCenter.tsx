/* ============================================================
   HelpCenter — panel opened from the header "?" button.

     Help        searchable answers (articles.ts)
     Report      mistake / wrong code / suggestion, sent to the
                 Google Sheet (docs/feedback-google-sheets.md) with
                 context: page, section in view, selected text,
                 optional screenshot, optional reply-to email
     Shortcuts   keyboard shortcuts

   Opening while looking at content (or with text selected) goes
   straight to Report, with that spot attached.
   ============================================================ */

import './help.css'
import { useEffect, useMemo, useRef, useState, useSyncExternalStore, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Camera, ChevronDown, CircleHelp, Keyboard, MessageSquareWarning, Search, Send, WifiOff, X } from 'lucide-react'
import { APP_NAME, FEEDBACK_URL } from '@/config'
import { useUser } from '@/features/auth/auth'
import { captureContext, screenshotVisible, type CapturedContext } from './capture'
import { ARTICLES, SHORTCUTS, type HelpArticle } from './articles'

/* ── open/close store (the header button calls toggleHelp) ── */

type Tab = 'help' | 'report' | 'shortcuts'
let current: { ctx: CapturedContext; tab: Tab } | null = null
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((l) => l())
const subscribe = (l: () => void) => { listeners.add(l); return () => { listeners.delete(l) } }

function openHelp(tab?: Tab) {
  const ctx = captureContext()
  // Something specific in view (a selection, or a problem / section) → they probably want to report it.
  current = { ctx, tab: tab ?? (ctx.selection ? 'report' : 'help') }
  emit()
}
function closeHelp() {
  current = null
  emit()
}

/** Header button: opens the Help center, or closes it if it's already open. */
// eslint-disable-next-line react-refresh/only-export-components
export function toggleHelp() {
  if (current) closeHelp()
  else openHelp()
}

// eslint-disable-next-line react-refresh/only-export-components
export function useHelpOpen() {
  return useSyncExternalStore(subscribe, () => current !== null)
}

export function HelpCenter() {
  const state = useSyncExternalStore(subscribe, () => current)
  if (!state) return null
  return <HelpPanel key={state.ctx.page + state.ctx.section} ctx={state.ctx} initialTab={state.tab} />
}

const TABS: { id: Tab; label: string; icon: typeof CircleHelp }[] = [
  { id: 'help', label: 'Help', icon: CircleHelp },
  { id: 'report', label: 'Report', icon: MessageSquareWarning },
  { id: 'shortcuts', label: 'Shortcuts', icon: Keyboard },
]

function HelpPanel({ ctx, initialTab }: { ctx: CapturedContext; initialTab: Tab }) {
  const [tab, setTab] = useState<Tab>(initialTab)
  const online = useOnline()

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && closeHelp()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <div className="help" role="dialog" aria-modal="false" aria-labelledby="help-title">
      <div className="help-head">
        <h2 id="help-title">Help center</h2>
        <button className="icon-btn sm" onClick={closeHelp} aria-label="Close help center"><X size={16} /></button>
      </div>
      <div className="help-tabs" role="tablist">
        {TABS.map((t) => (
          <button key={t.id} role="tab" aria-selected={tab === t.id} className="help-tab" onClick={() => setTab(t.id)}>
            <t.icon size={14} aria-hidden /> {t.label}
          </button>
        ))}
      </div>
      {!online && <p className="help-offline"><WifiOff size={13} aria-hidden /> You’re offline — reports will need a connection.</p>}
      {tab === 'help' && <HelpArticles onReport={() => setTab('report')} />}
      {tab === 'report' && <ReportForm ctx={ctx} />}
      {tab === 'shortcuts' && <Shortcuts />}
      <p className="help-foot">
        <Link to="/about" onClick={closeHelp}>About {APP_NAME}</Link>
        <span aria-hidden>·</span>
        <Link to="/settings" onClick={closeHelp}>Settings</Link>
        <span aria-hidden>·</span>
        <span>v{import.meta.env.VITE_APP_VERSION}</span>
      </p>
    </div>
  )
}

function useOnline() {
  return useSyncExternalStore(
    (l) => { window.addEventListener('online', l); window.addEventListener('offline', l); return () => { window.removeEventListener('online', l); window.removeEventListener('offline', l) } },
    () => navigator.onLine,
  )
}

/* ── Help: searchable articles ───────────────────────────── */

function matches(a: HelpArticle, terms: string[]) {
  const hay = `${a.title} ${a.body} ${a.keywords ?? ''} ${a.topic}`.toLowerCase()
  return terms.every((t) => hay.includes(t))
}

function HelpArticles({ onReport }: { onReport: () => void }) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  useEffect(() => { inputRef.current?.focus({ preventScroll: true }) }, [])

  const terms = query.toLowerCase().split(/\s+/).filter(Boolean)
  const list = terms.length ? ARTICLES.filter((a) => matches(a, terms)) : ARTICLES
  const groups = useMemo(() => {
    const m = new Map<string, HelpArticle[]>()
    for (const a of list) m.set(a.topic, [...(m.get(a.topic) ?? []), a])
    return [...m.entries()]
  }, [list])

  return (
    <div className="help-body">
      <label className="help-search">
        <Search size={15} aria-hidden />
        <input ref={inputRef} type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search help…" aria-label="Search help" />
      </label>
      {groups.map(([topic, items]) => (
        <div key={topic} className="help-group">
          <p className="help-group-title">{topic}</p>
          {items.map((a) => (
            <div key={a.id} className={`help-article ${open === a.id || terms.length ? 'is-open' : ''}`}>
              <button className="help-article-q" aria-expanded={open === a.id || terms.length > 0} onClick={() => setOpen(open === a.id ? null : a.id)}>
                {a.title}
                <ChevronDown size={15} aria-hidden />
              </button>
              {(open === a.id || terms.length > 0) && <ArticleBody body={a.body} />}
            </div>
          ))}
        </div>
      ))}
      {!list.length && <p className="muted small">No answers for “{query}”.</p>}
      <div className="help-cta">
        <p>Didn’t find it, or spotted a mistake?</p>
        <button className="btn btn-sm btn-primary" onClick={onReport}><MessageSquareWarning size={14} aria-hidden /> Report it</button>
      </div>
    </div>
  )
}

function ArticleBody({ body }: { body: string }) {
  return (
    <div className="help-article-a">
      {body.split('\n\n').map((block, i) => {
        const lines = block.split('\n')
        if (lines.every((l) => l.startsWith('- '))) return <ul key={i}>{lines.map((l) => <li key={l}>{l.slice(2)}</li>)}</ul>
        const bullets = lines.filter((l) => l.startsWith('- '))
        const text = lines.filter((l) => !l.startsWith('- ')).join(' ')
        return (
          <div key={i}>
            <p>{text}</p>
            {bullets.length > 0 && <ul>{bullets.map((l) => <li key={l}>{l.slice(2)}</li>)}</ul>}
          </div>
        )
      })}
    </div>
  )
}

/* ── Report ──────────────────────────────────────────────── */

const TYPES = ['Mistake in content', 'Wrong code', 'Bug in the app', 'Sign-in problem', 'Suggestion', 'Other'] as const
type Status = 'idle' | 'sending' | 'sent' | 'error'
type Shot = { state: 'none' } | { state: 'capturing' } | { state: 'ready'; url: string } | { state: 'failed' }

function ReportForm({ ctx }: { ctx: CapturedContext }) {
  const user = useUser()
  const [type, setType] = useState<(typeof TYPES)[number]>(TYPES[0])
  const [message, setMessage] = useState('')
  const [contact, setContact] = useState(user?.email ?? '')
  const [allowContact, setAllowContact] = useState(Boolean(user))
  const [status, setStatus] = useState<Status>('idle')
  const [shot, setShot] = useState<Shot>(ctx.target ? { state: 'capturing' } : { state: 'none' })
  const textRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => { textRef.current?.focus({ preventScroll: true }) }, [])
  useEffect(() => {
    if (!ctx.target) return
    let alive = true
    screenshotVisible(ctx.target).then(
      (url) => alive && setShot({ state: 'ready', url }),
      () => alive && setShot({ state: 'failed' }),
    )
    return () => { alive = false }
  }, [ctx.target])

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (new FormData(e.currentTarget).get('website')) return // honeypot
    if (!message.trim() || !FEEDBACK_URL) return
    setStatus('sending')
    const replyTo = allowContact && /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(contact.trim()) ? contact.trim() : ''
    try {
      // Apps Script doesn't send CORS headers; "no-cors" still delivers the POST.
      await fetch(FEEDBACK_URL, {
        method: 'POST',
        mode: 'no-cors',
        body: new URLSearchParams({
          type,
          message: (message.trim().slice(0, 1900) + (replyTo ? `\n\n— Reply to: ${replyTo}` : '')),
          page: ctx.page,
          pageTitle: ctx.pageTitle,
          section: ctx.section,
          selection: ctx.selection,
          device: `${ctx.device} · ${ctx.theme} · v${import.meta.env.VITE_APP_VERSION}${user ? ' · signed in' : ''}`,
          screenshot: shot.state === 'ready' ? shot.url : '',
        }),
      })
      setStatus('sent')
    } catch {
      setStatus('error')
    }
  }

  if (status === 'sent') {
    return (
      <div className="help-body help-sent">
        <div className="help-sent-icon" aria-hidden><Send size={20} /></div>
        <p className="help-thanks">Thanks! Your report was sent.</p>
        <p className="muted small">{allowContact && contact ? 'We’ll reply by email if we need more details.' : 'We read every report.'}</p>
        <button className="btn btn-sm" onClick={closeHelp}>Close</button>
      </div>
    )
  }

  return (
    <form className="help-body" onSubmit={submit}>
      <div className="help-types" role="radiogroup" aria-label="What’s it about?">
        {TYPES.map((t) => (
          <button key={t} type="button" role="radio" aria-checked={type === t} className="help-type" onClick={() => setType(t)}>{t}</button>
        ))}
      </div>
      <textarea
        id="help-message"
        ref={textRef}
        rows={4}
        maxLength={1900}
        placeholder={type === 'Suggestion' ? 'What would make this better?' : 'What’s wrong? The more specific, the faster we can fix it.'}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        required
        aria-label="Message"
      />
      <input type="text" name="website" tabIndex={-1} autoComplete="off" className="honeypot" aria-hidden />

      <label className="help-check">
        <input type="checkbox" checked={allowContact} onChange={(e) => setAllowContact(e.target.checked)} />
        You can email me about this
      </label>
      {allowContact && (
        <input className="help-input" type="email" value={contact} onChange={(e) => setContact(e.target.value)} placeholder="you@example.com" autoComplete="email" maxLength={254} aria-label="Your email" />
      )}

      <div className="help-attached">
        <p className="help-label">Attached automatically</p>
        <dl>
          <dt>Page</dt><dd>{ctx.section || ctx.pageTitle}</dd>
          {ctx.selection && <><dt>Selected</dt><dd className="help-quote">“{ctx.selection}”</dd></>}
        </dl>
        {shot.state === 'capturing' && <p className="muted"><Camera size={14} aria-hidden /> Taking a screenshot…</p>}
        {shot.state === 'failed' && <p className="muted">Screenshot unavailable.</p>}
        {shot.state === 'ready' && (
          <figure className="help-shot">
            <img src={shot.url} alt="Screenshot of the section you were viewing" />
            <button type="button" className="btn btn-sm" onClick={() => setShot({ state: 'none' })}>Remove screenshot</button>
          </figure>
        )}
      </div>

      <div className="help-actions">
        <button className="btn btn-primary btn-sm" type="submit" disabled={status === 'sending' || shot.state === 'capturing' || !FEEDBACK_URL || !message.trim()}>
          <Send size={14} aria-hidden /> {status === 'sending' ? 'Sending…' : 'Send report'}
        </button>
        {!FEEDBACK_URL && <span className="muted">Reports aren’t connected yet.</span>}
        {status === 'error' && <span className="help-error">Couldn’t send — check your connection.</span>}
      </div>
    </form>
  )
}

/* ── Shortcuts ───────────────────────────────────────────── */

function Shortcuts() {
  return (
    <div className="help-body">
      <ul className="help-shortcuts">
        {SHORTCUTS.map((s) => (
          <li key={s.action}>
            <span>{s.action}</span>
            <span className="help-keys">{s.keys.map((k) => <kbd key={k}>{k}</kbd>)}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
