/* ============================================================
   /login · /signup · /forgot-password
   Social providers first, then email + password.
   ============================================================ */

import './auth.css'
import { useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Eye, EyeOff, Flame, Github, Headphones, History, Linkedin, MailCheck, Timer } from 'lucide-react'
import { APP_NAME, AUTH_PROVIDERS } from '@/config'
import {
  authErrorMessage, isValidEmail, passwordIssues, passwordStrength, safeNext, sendPasswordReset, signInWithEmail,
  signInWithProvider, signUpWithEmail, useAuth, type ProviderId,
} from '@/features/auth/auth'

export type AuthMode = 'login' | 'signup' | 'reset'

const TITLES: Record<AuthMode, string> = {
  login: 'Welcome back',
  signup: 'Create your account',
  reset: 'Reset your password',
}

function GoogleIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 48 48" aria-hidden>
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z" />
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z" />
      <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z" />
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z" />
    </svg>
  )
}

const ALL_PROVIDERS: { id: ProviderId; label: string; icon: React.ReactNode }[] = [
  { id: 'google', label: 'Google', icon: <GoogleIcon /> },
  { id: 'github', label: 'GitHub', icon: <Github size={16} aria-hidden /> },
  { id: 'linkedin', label: 'LinkedIn', icon: <Linkedin size={16} aria-hidden /> },
]
const PROVIDERS = AUTH_PROVIDERS.map((id) => ALL_PROVIDERS.find((p) => p.id === id)!).filter(Boolean)

export function AuthPage({ mode }: { mode: AuthMode }) {
  const auth = useAuth()
  const [params] = useSearchParams()
  const next = safeNext(params.get('next'))
  const navigate = useNavigate()
  const [email, setEmail] = useState(params.get('email') ?? '')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [resetSent, setResetSent] = useState(false)
  const [touched, setTouched] = useState(false)

  useEffect(() => {
    document.title = `${TITLES[mode]} · ${APP_NAME}`
    setError('')
    setTouched(false)
    return () => { document.title = APP_NAME }
  }, [mode])

  if (auth.status === 'signed-in' && mode !== 'reset') return <Navigate to={next} replace />

  const unavailable = auth.status === 'unavailable'
  const issues = passwordIssues(password)
  const strength = passwordStrength(password)
  const emailOk = isValidEmail(email)

  const run = async (key: string, action: () => Promise<void>) => {
    setBusy(key)
    setError('')
    try {
      await action()
    } catch (e) {
      setError(authErrorMessage(e))
    } finally {
      setBusy(null)
    }
  }

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    setTouched(true)
    if (!emailOk) return setError('Enter a valid email address.')
    if (mode === 'reset') {
      return void run('email', async () => {
        await sendPasswordReset(email)
        setResetSent(true)
      })
    }
    if (mode === 'signup' && issues.length) return setError(`Password needs ${issues.join(', ')}.`)
    if (!password) return setError('Enter your password.')
    void run('email', async () => {
      if (mode === 'signup') await signUpWithEmail(name, email, password)
      else await signInWithEmail(email, password)
      navigate(next, { replace: true })
    })
  }

  const withNext = (path: string) => `${path}${next !== '/' ? `?next=${encodeURIComponent(next)}` : ''}`

  return (
    <div className="auth-page">
      <aside className="auth-aside" aria-hidden>
        <Link to="/" className="auth-brand" tabIndex={-1}>
          <img src="/icons/icon-192.png" alt="" width={36} height={36} />
          <span>{APP_NAME}</span>
        </Link>
        <h2 className="auth-aside-title">Study a little every day.<br /><span>We’ll keep count.</span></h2>
        <ul className="auth-perks">
          <li><Flame size={16} /> <span><strong>Streak & calendar</strong> — see every day you studied</span></li>
          <li><History size={16} /> <span><strong>History</strong> — topics, time spent and revisits</span></li>
          <li><Headphones size={16} /> <span><strong>Read-aloud & study kit</strong> — listen, quick notes, key terms</span></li>
          <li><Timer size={16} /> <span><strong>Focus timer</strong> — sessions that count toward your streak</span></li>
        </ul>
        <p className="auth-aside-foot">Free forever · Notes stay free to read without an account</p>
      </aside>

      <div className="auth-card">
        <div className="auth-top">
          <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> Back</Link>
          {mode !== 'reset' && (
            <div className="auth-switcher" role="tablist" aria-label="Sign in or create an account">
              <Link role="tab" aria-selected={mode === 'login'} to={withNext('/login')} replace>Log in</Link>
              <Link role="tab" aria-selected={mode === 'signup'} to={withNext('/signup')} replace>Create account</Link>
            </div>
          )}
        </div>
        <div className="auth-head">
          <h1>{TITLES[mode]}</h1>
          <p className="muted">
            {mode === 'login' && 'Pick up your streak where you left it.'}
            {mode === 'signup' && 'Takes 20 seconds. Your progress syncs everywhere.'}
            {mode === 'reset' && 'We’ll email you a link to choose a new password.'}
          </p>
        </div>

        {unavailable && <p className="auth-error" role="alert">Sign-in isn’t available right now. You can keep studying without an account.</p>}

        {mode === 'reset' && resetSent ? (
          <div className="auth-success" role="status">
            <MailCheck size={20} aria-hidden />
            <p>If an account exists for <strong>{email.trim()}</strong>, a reset link is on its way. Check your inbox (and spam folder).</p>
            <Link className="btn btn-sm" to={withNext('/login')}>Back to log in</Link>
          </div>
        ) : (
          <>
            {mode !== 'reset' && PROVIDERS.length > 0 && (
              <>
                <div className="auth-providers">
                  {PROVIDERS.map((p) => (
                    <button
                      key={p.id}
                      className="btn auth-provider"
                      disabled={unavailable || busy !== null}
                      onClick={() => void run(p.id, async () => {
                        await signInWithProvider(p.id)
                        navigate(next, { replace: true })
                      })}
                    >
                      {busy === p.id ? <span className="spinner sm" aria-hidden /> : p.icon}
                      <span>Continue with {p.label}</span>
                    </button>
                  ))}
                </div>
                <div className="auth-divider"><span>or with email</span></div>
              </>
            )}

            <form className="auth-form" onSubmit={onSubmit} noValidate>
              {mode === 'signup' && (
                <label className="field">
                  <span>Name</span>
                  <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" maxLength={60} placeholder="Your name" />
                </label>
              )}
              <label className="field">
                <span>Email</span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoComplete="email"
                  inputMode="email"
                  required
                  maxLength={254}
                  aria-invalid={touched && !emailOk}
                  placeholder="you@example.com"
                />
              </label>
              {mode !== 'reset' && (
                <label className="field">
                  <span className="field-row">
                    Password
                    {mode === 'login' && <Link to={`/forgot-password?email=${encodeURIComponent(email)}`} className="field-link">Forgot password?</Link>}
                  </span>
                  <span className="field-password">
                    <input
                      type={showPw ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      autoComplete={mode === 'signup' ? 'new-password' : 'current-password'}
                      required
                      maxLength={128}
                      aria-invalid={touched && mode === 'signup' && issues.length > 0}
                    />
                    <button type="button" className="icon-btn sm" onClick={() => setShowPw((v) => !v)} aria-label={showPw ? 'Hide password' : 'Show password'}>
                      {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </span>
                  {mode === 'signup' && password && (
                    <span className="strength" data-level={strength}>
                      <span className="strength-bar" aria-hidden><span /><span /><span /><span /></span>
                      <span className="muted small">{issues.length ? `Needs ${issues.join(', ')}` : ['Weak', 'Weak', 'Fair', 'Good', 'Strong'][strength]}</span>
                    </span>
                  )}
                </label>
              )}
              {error && <p className="auth-error" role="alert">{error}</p>}
              <button className="btn btn-primary auth-submit" type="submit" disabled={unavailable || busy !== null}>
                {busy === 'email' && <span className="spinner sm" aria-hidden />}
                {mode === 'login' ? 'Log in' : mode === 'signup' ? 'Create account' : 'Send reset link'}
              </button>
            </form>
          </>
        )}

        {mode === 'reset' && <p className="auth-switch">Remembered it? <Link to={withNext('/login')}>Log in</Link></p>}
        {mode === 'signup' && (
          <p className="auth-fine muted small">
            Only your name, email and study data are stored — never sold. Delete your account anytime.
          </p>
        )}
      </div>
    </div>
  )
}
