/* ============================================================
   AgeGate — over every page while a signed-in account hasn't
   confirmed it is 18+ (an account made with Google from the
   log-in page, or one made before the age check existed).
   An adult date of birth lets them in; under 18, the account
   and its data are deleted (auth.ts → refuseUnderage).
   ============================================================ */

import './auth.css'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { APP_NAME } from '@/config'
import {
  authErrorMessage, confirmAdultAge, dismissAgeNotice, refuseUnderage, signOutUser, useAgeNotice, useAuth,
} from './auth'
import { isAdult, isValidBirthDate, type BirthDate } from './age'
import { BirthDateField } from './BirthDateField'

export function AgeGate() {
  const auth = useAuth()
  const notice = useAgeNotice()
  if (notice === 'refused') return <Refused />
  if (auth.status !== 'age-check') return null
  return <AskAge email={auth.user.email} />
}

/** A modal <dialog>: the page behind it is inert and Escape doesn't close it. */
function Modal({ labelledBy, children }: { labelledBy: string; children: React.ReactNode }) {
  const ref = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const d = ref.current
    if (d && !d.open) d.showModal()
    return () => d?.close()
  }, [])
  return (
    <dialog ref={ref} className="age-gate" aria-labelledby={labelledBy} onCancel={(e) => e.preventDefault()}>
      {children}
    </dialog>
  )
}

function AskAge({ email }: { email: string }) {
  const [dob, setDob] = useState<Partial<BirthDate>>({})
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    if (!isValidBirthDate(dob)) return setError('Enter your date of birth.')
    setBusy(true)
    setError('')
    try {
      if (isAdult(dob)) await confirmAdultAge()
      else await refuseUnderage()
    } catch (err) {
      setError(authErrorMessage(err))
      setBusy(false)
    }
  }

  return (
    <Modal labelledBy="age-gate-title">
      <form className="auth-form" onSubmit={submit} noValidate>
        <div className="auth-head">
          <h2 id="age-gate-title">Before you continue</h2>
          <p className="muted">Signed in as {email}. Please tell us your date of birth.</p>
        </div>
        <BirthDateField value={dob} onChange={setDob} invalid={Boolean(error)} />
        {error && <p className="auth-error" role="alert">{error}</p>}
        <button className="btn btn-primary auth-submit" type="submit" disabled={busy}>
          {busy && <span className="spinner sm" aria-hidden />} Continue
        </button>
        <button className="btn auth-submit" type="button" disabled={busy} onClick={() => void signOutUser()}>Sign out</button>
        <p className="auth-fine muted small">
          By continuing you agree to the <a href="/terms" target="_blank" rel="noopener">Terms of Use</a> and confirm
          you’ve read the <a href="/privacy" target="_blank" rel="noopener">Privacy Policy</a>.
        </p>
      </form>
    </Modal>
  )
}

function Refused() {
  return (
    <Modal labelledBy="age-refused-title">
      <div className="auth-form">
        <div className="auth-head">
          <h2 id="age-refused-title">Sorry, this account can’t be used</h2>
        </div>
        <p>
          {APP_NAME} accounts are only for adults, so we’ve signed you out and are deleting this account and anything
          saved in it.
        </p>
        <p className="muted">You can still read every note and try every problem without an account.</p>
        <button className="btn btn-primary auth-submit" onClick={dismissAgeNotice} autoFocus>OK</button>
      </div>
    </Modal>
  )
}
