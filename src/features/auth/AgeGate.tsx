/* ============================================================
   AgeGate — over every page while a signed-in account hasn't
   confirmed it is 18+ (an account made with Google from the
   log-in page, or one made before the age check existed).

     ask             date of birth → "Is this right?" (asked for
                     every answer, so no answer stands out)
     blocked         this device refused someone in the last day
     confirm-delete  under 18 on an old session: sign in again so
                     the account can be deleted, or leave
   ============================================================ */

import './auth.css'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { APP_NAME } from '@/config'
import {
  authErrorMessage, confirmAdultAge, deleteRefusedAccount, dismissAgeNotice, leaveRefusedAccount, refuseUnderage,
  signOutUser, useAgeNotice, useAuth, type AppUser,
} from './auth'
import { isAdult, isValidBirthDate, type BirthDate } from './age'
import { BirthDateField, formatBirthDate } from './BirthDateField'

export function AgeGate() {
  const auth = useAuth()
  const notice = useAgeNotice()
  if (notice) return <Refused notice={notice} />
  if (auth.status !== 'age-check') return null
  if (auth.step === 'blocked') return <Blocked />
  if (auth.step === 'confirm-delete') return <ConfirmDelete user={auth.user} />
  return <AskAge email={auth.user.email} />
}

/**
 * A modal <dialog>: the page behind it is inert. Escape is refused, and if the browser closes it
 * anyway (a second Escape, Android back), it opens again until the gate is done.
 */
function Modal({ labelledBy, children }: { labelledBy: string; children: React.ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null)
  const leaving = useRef(false)
  useEffect(() => {
    const d = ref.current
    leaving.current = false
    if (d && !d.open) d.showModal()
    return () => {
      leaving.current = true
      d?.close()
    }
  }, [])
  const reopen = () => {
    const d = ref.current
    if (!leaving.current && d?.isConnected && !d.open) d.showModal()
  }
  return (
    <dialog ref={ref} className="age-gate" aria-labelledby={labelledBy} onCancel={(e) => e.preventDefault()} onClose={reopen}>
      {children}
    </dialog>
  )
}

function useAction() {
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const run = async (fn: () => Promise<void>) => {
    setBusy(true)
    setError('')
    try {
      await fn()
    } catch (e) {
      setError(authErrorMessage(e))
    } finally {
      setBusy(false)
    }
  }
  return { error, setError, busy, run }
}

function AskAge({ email }: { email: string }) {
  const [dob, setDob] = useState<Partial<BirthDate>>({})
  const [checking, setChecking] = useState(false)
  const { error, setError, busy, run } = useAction()

  const submit = (e: FormEvent) => {
    e.preventDefault()
    if (!isValidBirthDate(dob)) return setError('Enter your date of birth.')
    setError('')
    setChecking(true)
  }

  if (checking && isValidBirthDate(dob)) {
    return (
      <Modal labelledBy="age-gate-title">
        <div className="auth-form">
          <div className="auth-head">
            <h2 id="age-gate-title">Is this right?</h2>
            <p className="muted">Your date of birth:</p>
          </div>
          <p className="age-gate-date">{formatBirthDate(dob)}</p>
          {error && <p className="auth-error" role="alert">{error}</p>}
          <button className="btn btn-primary auth-submit" disabled={busy} autoFocus
            onClick={() => void run(isAdult(dob) ? confirmAdultAge : refuseUnderage)}>
            {busy && <span className="spinner sm" aria-hidden />} Yes, that’s right
          </button>
          <button className="btn auth-submit" disabled={busy} onClick={() => setChecking(false)}>Change it</button>
        </div>
      </Modal>
    )
  }

  return (
    <Modal labelledBy="age-gate-title">
      <form className="auth-form" onSubmit={submit} noValidate>
        <div className="auth-head">
          <h2 id="age-gate-title">Before you continue</h2>
          <p className="muted">Signed in as {email}. Please tell us your date of birth.</p>
        </div>
        <BirthDateField value={dob} onChange={(d) => { setDob(d); setError('') }} invalid={Boolean(error)} />
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="btn btn-primary auth-submit" type="submit">Continue</button>
        <button className="btn auth-submit" type="button" disabled={busy} onClick={() => void run(signOutUser)}>Sign out</button>
        <p className="auth-fine muted small">
          By continuing you agree to the <a href="/terms" target="_blank" rel="noopener">Terms of Use</a> and confirm
          you’ve read the <a href="/privacy" target="_blank" rel="noopener">Privacy Policy</a>.
        </p>
      </form>
    </Modal>
  )
}

function Blocked() {
  const { busy, run } = useAction()
  return (
    <Modal labelledBy="age-blocked-title">
      <div className="auth-form">
        <div className="auth-head">
          <h2 id="age-blocked-title">You can’t continue on this device right now</h2>
        </div>
        <p>
          {APP_NAME} accounts are only for adults, and this device was used to tell us someone is under 18 in the last
          day. Please try again later.
        </p>
        <p className="muted">You can still read every note and try every problem without an account.</p>
        <button className="btn btn-primary auth-submit" disabled={busy} autoFocus onClick={() => void run(signOutUser)}>Sign out</button>
      </div>
    </Modal>
  )
}

function ConfirmDelete({ user }: { user: AppUser }) {
  const [password, setPassword] = useState('')
  const { error, busy, run } = useAction()
  const withPassword = user.provider === 'password'
  return (
    <Modal labelledBy="age-delete-title">
      <form className="auth-form" noValidate onSubmit={(e) => { e.preventDefault(); void run(() => deleteRefusedAccount(password)) }}>
        <div className="auth-head">
          <h2 id="age-delete-title">One more step</h2>
        </div>
        <p>
          {APP_NAME} accounts are only for adults. We’ve deleted the study data saved in this account; to delete the
          account itself, confirm it’s you.
        </p>
        {withPassword && (
          <label className="field">
            <span>Password for {user.email}</span>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" autoFocus />
          </label>
        )}
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="btn btn-primary auth-submit" type="submit" disabled={busy || (withPassword && !password)}>
          {busy && <span className="spinner sm" aria-hidden />} {withPassword ? 'Delete my account' : 'Confirm and delete my account'}
        </button>
        <button className="btn auth-submit" type="button" disabled={busy} onClick={() => void run(leaveRefusedAccount)}>Sign out instead</button>
        <p className="auth-fine muted small">If you sign out, the account is deleted the next time it signs in here.</p>
      </form>
    </Modal>
  )
}

function Refused({ notice }: { notice: 'deleted' | 'signed-out' }) {
  return (
    <Modal labelledBy="age-refused-title">
      <div className="auth-form">
        <div className="auth-head">
          <h2 id="age-refused-title">{notice === 'deleted' ? 'Your account has been deleted' : 'You’ve been signed out'}</h2>
        </div>
        <p>
          {APP_NAME} accounts are only for adults,{' '}
          {notice === 'deleted'
            ? 'so we’ve deleted this account and everything saved in it.'
            : 'so we’ve deleted the study data saved in this account. The account itself is deleted the next time it signs in here.'}
        </p>
        <p className="muted">You can still read every note and try every problem without an account.</p>
        <button className="btn btn-primary auth-submit" onClick={dismissAgeNotice} autoFocus>OK</button>
      </div>
    </Modal>
  )
}
