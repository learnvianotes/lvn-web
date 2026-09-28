/* ============================================================
   AccountMenu — header button: "Sign in" when signed out, the
   learner's avatar with a small menu when signed in.
   ============================================================ */

import './auth.css'
import { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { CloudOff, History, LogOut, MailWarning, RefreshCw, Settings } from 'lucide-react'
import { authErrorMessage, refreshUser, resendVerification, signOutUser, useAuth, type AppUser } from '@/features/auth/auth'
import { useSyncStatus } from '@/features/progress/sync'

function Avatar({ user, size = 28 }: { user: AppUser; size?: number }) {
  const [broken, setBroken] = useState(false)
  if (user.photoURL && !broken) {
    return <img className="avatar" src={user.photoURL} alt="" width={size} height={size} referrerPolicy="no-referrer" onError={() => setBroken(true)} />
  }
  return <span className="avatar avatar--initial" style={{ width: size, height: size }} aria-hidden>{user.name.charAt(0).toUpperCase()}</span>
}

const SYNC_LABEL = { off: 'Not synced', syncing: 'Syncing…', synced: 'Synced', error: 'Sync paused — will retry' } as const

export function AccountMenu() {
  const auth = useAuth()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const root = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const onDown = (e: MouseEvent) => { if (!root.current?.contains(e.target as Node)) setOpen(false) }
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onDown)
    window.addEventListener('keydown', onKey)
    return () => { document.removeEventListener('mousedown', onDown); window.removeEventListener('keydown', onKey) }
  }, [open])
  useEffect(() => setOpen(false), [location.pathname])

  // Signed out: no header button — the sign-in banner lives in the progress panel.
  if (auth.status !== 'signed-in') return null

  return (
    <div className="account" ref={root}>
      <button className="account-btn" onClick={() => setOpen((o) => !o)} aria-haspopup="menu" aria-expanded={open} aria-label="Account">
        <Avatar user={auth.user} />
      </button>
      {open && <AccountPopover user={auth.user} close={() => setOpen(false)} />}
    </div>
  )
}

function AccountPopover({ user, close }: { user: AppUser; close: () => void }) {
  const sync = useSyncStatus()
  const navigate = useNavigate()
  const [msg, setMsg] = useState('')
  const [busy, setBusy] = useState(false)

  const act = async (fn: () => Promise<void>) => {
    setBusy(true)
    setMsg('')
    try { await fn() } catch (e) { setMsg(authErrorMessage(e)) } finally { setBusy(false) }
  }

  return (
    <div className="account-menu" role="menu">
      <div className="account-id">
        <Avatar user={user} size={36} />
        <div>
          <strong>{user.name}</strong>
          <span className="muted small">{user.email}</span>
        </div>
      </div>
      <p className={`account-sync is-${sync}`}>
        {sync === 'error' ? <CloudOff size={13} aria-hidden /> : <RefreshCw size={13} aria-hidden className={sync === 'syncing' ? 'spin' : ''} />}
        {SYNC_LABEL[sync]}
      </p>

      {user.provider === 'password' && !user.emailVerified && (
        <div className="account-verify">
          <MailWarning size={14} aria-hidden />
          <span>Please verify your email.</span>
          <button className="linkish" disabled={busy} onClick={() => void act(async () => { await resendVerification(); setMsg('Verification email sent.') })}>Resend</button>
          <button className="linkish" disabled={busy} onClick={() => void act(refreshUser)}>I’ve verified</button>
        </div>
      )}

      <Link to="/history" className="account-item" role="menuitem" onClick={close}><History size={15} aria-hidden /> Study history</Link>
      <Link to="/settings" className="account-item" role="menuitem" onClick={close}><Settings size={15} aria-hidden /> Settings</Link>
      <button className="account-item" role="menuitem" disabled={busy} onClick={() => void act(async () => { await signOutUser(); close(); navigate('/') })}>
        <LogOut size={15} aria-hidden /> Sign out
      </button>

      {msg && <p className="account-msg" role="status">{msg}</p>}
    </div>
  )
}
