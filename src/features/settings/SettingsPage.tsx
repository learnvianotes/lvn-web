/* ============================================================
   /settings — the essentials in one place.
     Appearance      theme (everyone)
     Study           daily goal, read-aloud voice & speed, focus sound
     Home            default sort, reset my subject order
     Account         profile, verification, sync, sign out
     Your data       export as JSON, delete account
   Everything but Appearance needs an account.
   ============================================================ */

import './settings.css'
import { useState, type ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  ArrowLeft, Bell, BellOff, CloudOff, Download, LogOut, MailWarning, Monitor, Moon, Play, RefreshCw, Sun, Trash2,
} from 'lucide-react'
import type { SubjectSort } from '@schema/firestore'
import { APP_NAME } from '@/config'
import {
  authErrorMessage, deleteCurrentUser, refreshUser, resendVerification, signOutUser, useAuth, type AppUser,
} from '@/features/auth/auth'
import { SignInBanner } from '@/features/auth/SignInBanner'
import { DAILY_GOALS, getPrefs, resetSubjectOrder, setDailyGoal, setSort, usePrefs } from '@/features/progress/prefs'
import { getProgress } from '@/features/progress/store'
import { getActivity } from '@/features/progress/activity'
import { getNotes } from '@/features/progress/notes'
import { deleteMyData, syncNow, useSyncStatus } from '@/features/progress/sync'
import { SORTS } from '@/features/home/subjectOrder'
import { toggleSound, useFocus } from '@/features/focus/focus'
import { RATES, setRate, setVoice, speak, speechSupported, useSpeech, useVoices } from '@/features/voice/speech'
import { setThemeMode, useThemeMode, type ThemeMode } from '@/shared/lib/theme'
import { Loading } from '@/shared/ui/Status'

export function SettingsPage() {
  const auth = useAuth()
  const user = auth.status === 'signed-in' ? auth.user : null

  return (
    <div className="page settings">
      <div className="settings-head">
        <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> All subjects</Link>
        <h1 className="page-title">Settings</h1>
      </div>

      <Appearance />
      {auth.status === 'loading' ? (
        <Loading />
      ) : user ? (
        <>
          <Study />
          <HomeSettings />
          <Account user={user} />
          <DataSettings user={user} />
        </>
      ) : (
        <SignInBanner />
      )}
      <p className="settings-foot muted small">
        {APP_NAME} v{import.meta.env.VITE_APP_VERSION} · <Link to="/about">About</Link> · <Link to="/privacy">Privacy</Link> ·{' '}
        <Link to="/terms">Terms</Link> · <Link to="/grievance">Grievance</Link>
      </p>
    </div>
  )
}

/* ── building blocks ─────────────────────────────────────── */

function Group({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="settings-group" aria-label={title}>
      <h2>{title}</h2>
      <div className="settings-card">{children}</div>
    </section>
  )
}

function Row({ label, hint, children }: { label: string; hint?: string; children: ReactNode }) {
  return (
    <div className="settings-row">
      <div className="settings-label">
        <span>{label}</span>
        {hint && <span className="muted small">{hint}</span>}
      </div>
      <div className="settings-control">{children}</div>
    </div>
  )
}

function Segmented<T extends string | number>({ value, options, onChange, label }: {
  value: T
  options: { value: T; label: ReactNode }[]
  onChange: (v: T) => void
  label: string
}) {
  return (
    <div className="seg" role="radiogroup" aria-label={label}>
      {options.map((o) => (
        <button key={String(o.value)} role="radio" aria-checked={value === o.value} className="seg-item" onClick={() => onChange(o.value)}>
          {o.label}
        </button>
      ))}
    </div>
  )
}

/* ── sections ────────────────────────────────────────────── */

function Appearance() {
  const mode = useThemeMode()
  return (
    <Group title="Appearance">
      <Row label="Theme" hint="System follows your device’s light / dark setting.">
        <Segmented<ThemeMode>
          label="Theme"
          value={mode}
          onChange={setThemeMode}
          options={[
            { value: 'light', label: <><Sun size={14} aria-hidden /> Light</> },
            { value: 'dark', label: <><Moon size={14} aria-hidden /> Dark</> },
            { value: 'system', label: <><Monitor size={14} aria-hidden /> System</> },
          ]}
        />
      </Row>
    </Group>
  )
}

function Study() {
  const prefs = usePrefs()
  const focus = useFocus()
  const speech = useSpeech()
  const voices = useVoices()
  return (
    <Group title="Study">
      <Row label="Daily goal" hint="Minutes of study that fill today’s ring on the home page.">
        <select className="settings-select" value={prefs.dailyGoal} onChange={(e) => setDailyGoal(Number(e.target.value))} aria-label="Daily goal">
          {DAILY_GOALS.map((m) => <option key={m} value={m}>{m} min</option>)}
        </select>
      </Row>
      {speechSupported && (
        <>
          <Row label="Read-aloud speed">
            <select className="settings-select" value={speech.rate} onChange={(e) => setRate(Number(e.target.value))} aria-label="Read-aloud speed">
              {RATES.map((r) => <option key={r} value={r}>{r}×</option>)}
            </select>
          </Row>
          <Row label="Read-aloud voice" hint="Voices come from your device.">
            <div className="settings-inline">
              <select className="settings-select" value={speech.voiceURI} onChange={(e) => setVoice(e.target.value)} aria-label="Read-aloud voice">
                <option value="">Automatic</option>
                {voices.map((v) => <option key={v.voiceURI} value={v.voiceURI}>{v.name} ({v.lang})</option>)}
              </select>
              <button className="btn btn-sm" onClick={() => speak('Voice preview', [{ text: 'This is how topics will sound when read aloud.' }])}>
                <Play size={13} aria-hidden /> Test
              </button>
            </div>
          </Row>
        </>
      )}
      <Row label="Focus timer sound" hint="A short chime when a session ends.">
        <button className={`btn btn-sm ${focus.sound ? 'is-on' : ''}`} onClick={toggleSound} aria-pressed={focus.sound}>
          {focus.sound ? <><Bell size={14} aria-hidden /> On</> : <><BellOff size={14} aria-hidden /> Off</>}
        </button>
      </Row>
    </Group>
  )
}

function HomeSettings() {
  const prefs = usePrefs()
  return (
    <Group title="Home">
      <Row label="Sort subjects by">
        <select className="settings-select" value={prefs.sort} onChange={(e) => setSort(e.target.value as SubjectSort)} aria-label="Sort subjects by">
          {SORTS.filter((s) => s.id !== 'custom' || prefs.subjectOrder.length).map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
      </Row>
      <Row label="My subject order" hint={prefs.subjectOrder.length ? 'You’ve arranged the subjects yourself.' : 'Use “Rearrange” on the home page to set your own order.'}>
        <button className="btn btn-sm" disabled={!prefs.subjectOrder.length} onClick={resetSubjectOrder}>Reset to default</button>
      </Row>
    </Group>
  )
}

const PROVIDER_LABEL: Record<string, string> = {
  password: 'Email & password', 'google.com': 'Google', 'github.com': 'GitHub', 'oidc.linkedin': 'LinkedIn',
}
const SYNC_LABEL = { off: 'Not synced', syncing: 'Syncing…', synced: 'All changes synced', error: 'Sync paused — will retry' } as const

function Account({ user }: { user: AppUser }) {
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
    <Group title="Account">
      <div className="settings-profile">
        {user.photoURL
          ? <img className="avatar" src={user.photoURL} alt="" width={44} height={44} referrerPolicy="no-referrer" />
          : <span className="avatar avatar--initial" style={{ width: 44, height: 44, fontSize: 17 }} aria-hidden>{user.name.charAt(0).toUpperCase()}</span>}
        <div>
          <strong>{user.name}</strong>
          <span className="muted small">{user.email} · {PROVIDER_LABEL[user.provider] ?? user.provider}</span>
        </div>
      </div>
      {user.provider === 'password' && !user.emailVerified && (
        <Row label="Email not verified" hint="Verify to secure your account and allow password resets.">
          <div className="settings-inline">
            <button className="btn btn-sm" disabled={busy} onClick={() => void act(async () => { await resendVerification(); setMsg('Verification email sent.') })}>
              <MailWarning size={14} aria-hidden /> Resend email
            </button>
            <button className="btn btn-sm" disabled={busy} onClick={() => void act(refreshUser)}>I’ve verified</button>
          </div>
        </Row>
      )}
      <Row label="Sync" hint={SYNC_LABEL[sync]}>
        <button className="btn btn-sm" disabled={sync === 'syncing'} onClick={() => void syncNow()}>
          {sync === 'error' ? <CloudOff size={14} aria-hidden /> : <RefreshCw size={14} aria-hidden className={sync === 'syncing' ? 'spin' : ''} />} Sync now
        </button>
      </Row>
      <Row label="Sign out" hint="Your study data is removed from this device and stays in your account.">
        <button className="btn btn-sm" disabled={busy} onClick={() => void act(async () => { await signOutUser(); navigate('/') })}>
          <LogOut size={14} aria-hidden /> Sign out
        </button>
      </Row>
      {msg && <p className="settings-msg" role="status">{msg}</p>}
    </Group>
  )
}

function exportData(user: AppUser) {
  const data = {
    exportedAt: new Date().toISOString(),
    account: { name: user.name, email: user.email, provider: user.provider },
    progress: getProgress(),
    activity: getActivity(),
    notes: getNotes(),
    preferences: getPrefs(),
  }
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `learnvianotes-${new Date().toISOString().slice(0, 10)}.json`
  a.click()
  setTimeout(() => URL.revokeObjectURL(a.href), 1000)
}

function DataSettings({ user }: { user: AppUser }) {
  const navigate = useNavigate()
  const [confirm, setConfirm] = useState('')
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState('')

  return (
    <Group title="Your data">
      <Row label="Export my data" hint="Progress, study history, notes and preferences as a JSON file.">
        <button className="btn btn-sm" onClick={() => exportData(user)}><Download size={14} aria-hidden /> Download</button>
      </Row>
      <Row label="Delete account" hint="Permanently deletes your account, streak, history and notes.">
        {!open && <button className="btn btn-sm is-danger" onClick={() => setOpen(true)}><Trash2 size={14} aria-hidden /> Delete…</button>}
      </Row>
      {open && (
        <div className="settings-danger">
          <p>This can’t be undone. Type <strong>DELETE</strong> to confirm.</p>
          <div className="settings-inline">
            <input className="settings-input" value={confirm} onChange={(e) => setConfirm(e.target.value)} aria-label="Type DELETE to confirm" />
            <button className="btn btn-sm" onClick={() => { setOpen(false); setConfirm('') }}>Cancel</button>
            <button
              className="btn btn-sm btn-danger"
              disabled={confirm !== 'DELETE' || busy}
              onClick={async () => {
                setBusy(true)
                setMsg('')
                try {
                  await deleteMyData()
                  await deleteCurrentUser()
                  navigate('/')
                } catch (e) {
                  setMsg(authErrorMessage(e))
                } finally {
                  setBusy(false)
                }
              }}
            >
              {busy ? 'Deleting…' : 'Delete forever'}
            </button>
          </div>
          {msg && <p className="settings-msg" role="alert">{msg}</p>}
        </div>
      )}
    </Group>
  )
}
