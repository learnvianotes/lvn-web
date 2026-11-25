'use client'

import { useMutation } from '@apollo/client/react'
import { KeyRound } from 'lucide-react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { RequestSignInCodeDocument, SignInDocument, SignInWithCodeDocument } from '@/graphql/generated/graphql'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { refusalMessage } from '@/lib/limit-error'
import { AgeBlocked } from './AgeBlocked'
import { InviteOnlyNotice } from './InviteOnlyNotice'
import { ProviderButtons } from './ProviderButtons'
import { useFinishSignIn } from './useFinishSignIn'
import { usePasskeySignIn } from './usePasskeySignIn'

type Step = { kind: 'email' } | { kind: 'password' } | { kind: 'code'; email: string }
type Finish = ReturnType<typeof useFinishSignIn>
type Payload = { session?: Parameters<Finish>[0] | null; mfaRequired?: boolean | null; userErrors: { message: string; code: string }[] }

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const RESEND_AFTER = 30

/**
 * Sign in (lvn-backend ADR-0115): Google, a passkey, or the email. The email gets a 6-digit code by default; a password
 * is one quiet link away. Every path ends in the same finish (session stored, admins sent to their code screen).
 */
export function SignInForm() {
  const t = useTranslations('auth.signIn')
  const te = useTranslations('auth.errors')
  const params = useSearchParams()
  const next = params.get('next')
  const inviteFromQuery = params.get('error') === 'invite_only'
  const finish = useFinishSignIn()
  const passkey = usePasskeySignIn(next)
  const [requestCode] = useMutation(RequestSignInCodeDocument)
  const [withCode] = useMutation(SignInWithCodeDocument)
  const [withPassword] = useMutation(SignInDocument)
  const [step, setStep] = useState<Step>({ kind: 'email' })
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [general, setGeneral] = useState<string | null>(null)
  const [fieldError, setFieldError] = useState<string | null>(null)
  const [refused, setRefused] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [hold, setHold] = useState<AgeHold | null>(null)
  const [wait, setWait] = useState(0)

  useEffect(() => {
    if (wait <= 0) return
    const timer = setTimeout(() => setWait((s) => s - 1), 1000)
    return () => clearTimeout(timer)
  }, [wait])

  const reset = () => {
    setGeneral(null)
    setFieldError(null)
    setRefused(null)
    setNotice(null)
  }

  /** The same handling for every way in: an age hold, a session, or the reason it did not work. */
  const settle = async (payload: Payload | undefined) => {
    if (!payload) return setGeneral(te('generic'))
    const ageHold = ageHoldFromProblems(payload.userErrors as never)
    if (ageHold) return setHold(ageHold)
    if (payload.session) return void (await finish(payload.session, next, payload.mfaRequired))
    const blocked = payload.userErrors.find((e) => e.code === 'FORBIDDEN')
    if (blocked) return setRefused(blocked.message)
    setGeneral(payload.userErrors[0]?.message ?? te('generic'))
  }

  const run = async (work: () => Promise<void>) => {
    reset()
    setBusy(true)
    try {
      await work()
    } catch (error) {
      setGeneral(refusalMessage(error) ?? te('generic'))
    } finally {
      setBusy(false)
    }
  }

  const validEmail = () => {
    if (EMAIL.test(email.trim())) return true
    setFieldError(te('email'))
    return false
  }

  const sendCode = (event: React.FormEvent) => {
    event.preventDefault()
    reset()
    if (!validEmail()) return
    void run(async () => {
      const { data } = await requestCode({ variables: { input: { email: email.trim() } } })
      const problem = data?.requestSignInCode.userErrors[0]
      if (problem) return setGeneral(problem.message)
      setStep({ kind: 'code', email: email.trim() })
      setCode('')
      setWait(RESEND_AFTER)
    })
  }

  const resend = () =>
    void run(async () => {
      if (step.kind !== 'code') return
      const { data } = await requestCode({ variables: { input: { email: step.email } } })
      const problem = data?.requestSignInCode.userErrors[0]
      if (problem) return setGeneral(problem.message)
      setNotice(t('resent'))
      setWait(RESEND_AFTER)
    })

  const submitCode = (event: React.FormEvent) => {
    event.preventDefault()
    reset()
    if (step.kind !== 'code') return
    if (!/^\d{6}$/.test(code.replace(/\s+/g, ''))) return setFieldError(te('required'))
    void run(async () => {
      const { data } = await withCode({ variables: { input: { email: step.email, code } } })
      await settle(data?.signInWithCode)
    })
  }

  const submitPassword = (event: React.FormEvent) => {
    event.preventDefault()
    reset()
    if (!validEmail()) return
    if (!password) return setFieldError(te('required'))
    void run(async () => {
      const { data } = await withPassword({ variables: { input: { email: email.trim(), password } } })
      await settle(data?.signIn)
    })
  }

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">{step.kind === 'code' ? t('codeTitle') : t('title')}</h1>
        <p className="text-sm text-muted">{step.kind === 'code' ? t('codeLead', { email: step.email }) : t('lead')}</p>
      </header>
      <InviteOnlyNotice />
      {inviteFromQuery || refused ? <Alert tone="error">{refused ?? te('inviteOnly')}</Alert> : null}
      {general ? <Alert tone="error">{general}</Alert> : null}
      {notice ? <Alert tone="info">{notice}</Alert> : null}

      {step.kind === 'code' ? (
        <form onSubmit={submitCode} noValidate className="flex flex-col gap-4">
          <Field label={t('code')} error={fieldError ?? undefined}>
            <Input
              autoFocus
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={7}
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/[^\d ]/g, ''))}
              className="font-mono text-lg tabular-nums tracking-[0.3em]"
            />
          </Field>
          <Button type="submit" size="lg" disabled={busy}>
            {t('codeSubmit')}
          </Button>
          <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
            <button type="button" className="text-accent hover:underline disabled:text-muted disabled:no-underline" disabled={busy || wait > 0} onClick={resend}>
              {wait > 0 ? t('resendIn', { seconds: wait }) : t('resend')}
            </button>
            <button type="button" className="text-muted hover:text-fg" onClick={() => (reset(), setStep({ kind: 'email' }))}>
              {t('otherEmail')}
            </button>
          </div>
        </form>
      ) : (
        <>
          <ProviderButtons next={next} onAgeHold={setHold} />
          <form onSubmit={step.kind === 'password' ? submitPassword : sendCode} noValidate className="flex flex-col gap-3">
            <Field label={t('email')} error={fieldError && !(step.kind === 'password' && EMAIL.test(email.trim())) ? fieldError : undefined}>
              <Input type="email" autoComplete="email webauthn" inputMode="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            </Field>
            {step.kind === 'password' ? (
              <Field label={t('password')} error={fieldError && EMAIL.test(email.trim()) ? fieldError : undefined}>
                <Input type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </Field>
            ) : null}
            <Button type="submit" size="lg" className="mt-1" disabled={busy}>
              {step.kind === 'password' ? t('submit') : t('emailCode')}
            </Button>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-sm">
              <button type="button" className="font-medium text-accent hover:underline" onClick={() => (reset(), setStep(step.kind === 'password' ? { kind: 'email' } : { kind: 'password' }))}>
                {step.kind === 'password' ? t('useCode') : t('usePassword')}
              </button>
              {step.kind === 'password' ? (
                <Link href="/reset" className="text-muted hover:text-fg">
                  {t('forgot')}
                </Link>
              ) : null}
              {passkey.available ? (
                <button type="button" className="inline-flex items-center gap-1.5 text-muted hover:text-fg disabled:opacity-50" disabled={passkey.busy || busy} onClick={() => void passkey.signIn()}>
                  <KeyRound className="size-4" strokeWidth={1.75} aria-hidden />
                  {passkey.busy ? t('passkeyBusy') : t('passkey')}
                </button>
              ) : null}
            </div>
            {passkey.error ? <Alert tone="error">{passkey.error}</Alert> : null}
          </form>
        </>
      )}

      <p className="text-sm text-muted">
        {t('noAccount')}{' '}
        <Link href={next ? `/sign-up?next=${encodeURIComponent(next)}` : '/sign-up'} className="font-medium text-accent hover:underline">
          {t('signUp')}
        </Link>
      </p>
    </div>
  )
}
