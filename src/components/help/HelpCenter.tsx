/* ============================================================
   HelpCenter — floating feedback window opened from the header.
   Sends the message plus captured context (page, section in view,
   selected text, screenshot) to the Google Sheet (see
   docs/feedback-google-sheets.md).
   ============================================================ */

import { useEffect, useRef, useState, useSyncExternalStore, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { Camera, X } from 'lucide-react'
import { APP_NAME, FEEDBACK_URL } from '@/config'
import { captureContext, screenshotVisible, type CapturedContext } from './capture'

/* ── open/close store (the header button calls toggleHelp) ── */
let current: CapturedContext | null = null
const listeners = new Set<() => void>()
const emit = () => listeners.forEach((l) => l())

function openHelp() {
  current = captureContext()
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
  return useSyncExternalStore((l) => { listeners.add(l); return () => listeners.delete(l) }, () => current !== null)
}

const TYPES = ['Mistake in content', 'Wrong code', 'Suggestion', 'Other'] as const
type Status = 'idle' | 'sending' | 'sent' | 'error'
type Shot = { state: 'none' } | { state: 'capturing' } | { state: 'ready'; url: string } | { state: 'failed' }

export function HelpCenter() {
  const ctx = useSyncExternalStore((l) => { listeners.add(l); return () => listeners.delete(l) }, () => current)
  if (!ctx) return null
  return <HelpDialog key={ctx.page + ctx.section} ctx={ctx} />
}

function HelpDialog({ ctx }: { ctx: CapturedContext }) {
  const [type, setType] = useState<(typeof TYPES)[number]>(TYPES[0])
  const [message, setMessage] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [shot, setShot] = useState<Shot>(ctx.target ? { state: 'capturing' } : { state: 'none' })
  const textRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    textRef.current?.focus({ preventScroll: true })
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && closeHelp()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

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
    try {
      // Apps Script doesn't send CORS headers; "no-cors" still delivers the POST.
      await fetch(FEEDBACK_URL, {
        method: 'POST',
        mode: 'no-cors',
        body: new URLSearchParams({
          type,
          message: message.trim().slice(0, 2000),
          page: ctx.page,
          pageTitle: ctx.pageTitle,
          section: ctx.section,
          selection: ctx.selection,
          device: `${ctx.device} · ${ctx.theme}`,
          screenshot: shot.state === 'ready' ? shot.url : '',
        }),
      })
      setStatus('sent')
    } catch {
      setStatus('error')
    }
  }

  return (
    <div className="help" role="dialog" aria-modal="false" aria-labelledby="help-title">
      <div className="help-head">
        <h2 id="help-title">Help center</h2>
        <button className="icon-btn sm" onClick={closeHelp} aria-label="Close help center"><X size={16} /></button>
      </div>

      {status === 'sent' ? (
        <div className="help-body">
          <p className="help-thanks">Thanks! Your feedback was sent.</p>
          <button className="btn btn-sm" onClick={closeHelp}>Close</button>
        </div>
      ) : (
        <form className="help-body" onSubmit={submit}>
          <label className="help-label" htmlFor="help-message">Found a mistake or have a suggestion?</label>
          <select value={type} onChange={(e) => setType(e.target.value as (typeof TYPES)[number])} aria-label="Feedback type">
            {TYPES.map((t) => <option key={t}>{t}</option>)}
          </select>
          <textarea
            id="help-message"
            ref={textRef}
            rows={4}
            maxLength={2000}
            placeholder="What's wrong, or what could be better?"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            required
          />
          <input type="text" name="website" tabIndex={-1} autoComplete="off" className="honeypot" aria-hidden />

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
            <button className="btn btn-primary btn-sm" type="submit" disabled={status === 'sending' || shot.state === 'capturing' || !FEEDBACK_URL}>
              {status === 'sending' ? 'Sending…' : 'Send feedback'}
            </button>
            {!FEEDBACK_URL && <span className="muted">Feedback isn’t connected yet.</span>}
            {status === 'error' && <span className="help-error">Couldn’t send — check your connection.</span>}
          </div>
          <p className="help-foot"><Link to="/about" onClick={closeHelp}>About {APP_NAME}</Link></p>
        </form>
      )}
    </div>
  )
}
