'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation } from '@apollo/client/react'
import { usePathname, useRouter } from 'next/navigation'
import { useFormatter, useTranslations } from 'next-intl'
import { useEffect, useRef, useState, type ClipboardEvent, type FormEvent } from 'react'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { MfaStatusDocument, StartMfaChallengeDocument, VerifyMfaChallengeDocument } from '@/graphql/generated/graphql'
import { safeNext } from '@/lib/auth/destination'
import { ADMIN_VERIFY_PATH, classifyMfaProblem, isAdminMfaRole, noteMfaVerified, retryAfterSeconds, type MfaProblemKind } from '@/lib/auth/mfa'
import { signedIn } from '@/lib/auth/session'
import { useViewerRole } from '@/features/admin/useViewerRole'

/** After a code is sent, wait before offering another, unless the API asks for longer. */
const RESEND_AFTER_SEND_SECONDS = 30

type Problem = { message: string; code?: string | null; retryAfter?: number | null }

function thrownRetry(error: unknown): number | null {
  if (!CombinedGraphQLErrors.is(error)) return null
  const hit = error.errors.find((item) => item.extensions?.code === 'RATE_LIMITED')
  return retryAfterSeconds(typeof hit?.extensions?.retryAfter === 'number' ? hit.extensions.retryAfter : null)
}

/**
 * The "Check your email" step. It sends a 6-digit code as soon as it opens, then checks what was typed or pasted.
 * A successful check stores the new access token (the API rotates the refresh cookie with it).
 */
export function AdminMfaPanel({ onVerified }: { onVerified: () => void }) {
  const t = useTranslations('adminMfa')
  const format = useFormatter()
  const [start, startState] = useMutation(StartMfaChallengeDocument)
  const [verify, verifyState] = useMutation(VerifyMfaChallengeDocument)
  const [challenge, setChallenge] = useState<{ id: string; expiresAt: string } | null>(null)
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [wait, setWait] = useState(0)
  const started = useRef(false)

  useEffect(() => {
    if (wait <= 0) return
    const id = window.setTimeout(() => setWait((current) => Math.max(0, current - 1)), 1000)
    return () => window.clearTimeout(id)
  }, [wait])

  const hold = (seconds: number) => setWait((current) => Math.max(current, seconds))

  const showProblem = (problem: Problem) => {
    const kind: MfaProblemKind = classifyMfaProblem(problem.message, problem.code)
    const seconds = retryAfterSeconds(problem.retryAfter)
    if (kind === 'rate') {
      const pause = seconds ?? 60
      hold(pause)
      setError(t('rate', { seconds: pause }))
      return
    }
    if (kind === 'locked' || kind === 'expired' || kind === 'used') setChallenge(null)
    setError(kind === 'other' ? problem.message || t('failed') : t(kind))
  }

  const send = async () => {
    setError(null)
    try {
      const { data } = await start({ variables: { factor: 'EMAIL_OTP' } })
      const payload = data?.startMfaChallenge
      const problem = payload?.userErrors[0]
      if (problem) {
        showProblem(problem)
        return
      }
      if (!payload?.challengeId || !payload.expiresAt) {
        setError(t('sendFailed'))
        return
      }
      setChallenge({ id: payload.challengeId, expiresAt: payload.expiresAt })
      setCode('')
      hold(RESEND_AFTER_SEND_SECONDS)
    } catch (err) {
      const seconds = thrownRetry(err)
      if (seconds) {
        hold(seconds)
        setError(t('rate', { seconds }))
        return
      }
      setError(t('sendFailed'))
    }
  }

  useEffect(() => {
    if (started.current) return
    started.current = true
    void send()
    // One code when the screen opens. Resend is the only later send.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault()
    if (!challenge || code.length !== 6 || verifyState.loading) return
    setError(null)
    try {
      const { data } = await verify({ variables: { challengeId: challenge.id, code } })
      const payload = data?.verifyMfaChallenge
      const problem = payload?.userErrors[0]
      if (problem || !payload?.session) {
        if (problem) showProblem(problem)
        else setError(t('failed'))
        return
      }
      signedIn(payload.session.accessToken, payload.session.accessTokenExpiresAt)
      noteMfaVerified(payload.session.user.globalRole)
      onVerified()
    } catch (err) {
      const seconds = thrownRetry(err)
      if (seconds) {
        hold(seconds)
        setError(t('rate', { seconds }))
        return
      }
      setError(t('failed'))
    }
  }

  const onPaste = (event: ClipboardEvent<HTMLInputElement>) => {
    const digits = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
    if (!digits) return
    event.preventDefault()
    setCode(digits)
  }

  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
  const expires = challenge ? format.dateTime(new Date(challenge.expiresAt), { hour: 'numeric', minute: '2-digit', day: 'numeric', month: 'short', timeZone }) : null

  return (
    <form onSubmit={onSubmit} noValidate className="mx-auto flex w-full max-w-md flex-col gap-4 rounded-2xl border border-border bg-surface p-6" aria-labelledby="admin-mfa-title">
      <header className="flex flex-col gap-1">
        <h1 id="admin-mfa-title" className="text-2xl font-semibold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {expires ? <p className="text-sm text-muted">{t('expires', { time: expires })}</p> : <p role="status" className="text-sm text-muted">{t('sending')}</p>}
      <Field label={t('code')} error={error ?? undefined}>
        <Input
          inputMode="numeric"
          autoComplete="one-time-code"
          autoFocus
          maxLength={6}
          pattern="[0-9]*"
          value={code}
          onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))}
          onPaste={onPaste}
        />
      </Field>
      <Button type="submit" disabled={code.length !== 6 || !challenge || verifyState.loading}>{verifyState.loading ? t('verifying') : t('verify')}</Button>
      <Button type="button" variant="secondary" disabled={wait > 0 || startState.loading} onClick={() => void send()}>
        {wait > 0 ? t('resendWait', { seconds: wait }) : t('resend')}
      </Button>
    </form>
  )
}

/** Shown in place of admin pages until the code is accepted. Afterwards, the verify route returns to where they were. */
export function AdminMfaGate() {
  const pathname = usePathname()
  const router = useRouter()
  const client = useApolloClient()
  return (
    <AdminMfaPanel
      onVerified={() => {
        const current = client.readQuery({ query: MfaStatusDocument })
        if (current) {
          client.writeQuery({
            query: MfaStatusDocument,
            data: { mfaStatus: { ...current.mfaStatus, satisfied: true, verifiedAt: new Date().toISOString() } },
          })
        }
        void client.refetchQueries({ include: [MfaStatusDocument] })
        if (pathname !== ADMIN_VERIFY_PATH) return
        const next = safeNext(new URLSearchParams(window.location.search).get('next'))
        router.replace(next ?? '/admin')
      }}
    />
  )
}

/**
 * The verify route's page. The layout shows the code screen itself while a code is still required, so this only
 * runs once that is finished — or when the visitor is not an admin, who is sent away without the form.
 */
export function AdminVerifyPage() {
  const t = useTranslations('adminMfa')
  const { role, ready } = useViewerRole()
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    if (!ready || pathname !== ADMIN_VERIFY_PATH) return
    const next = safeNext(new URLSearchParams(window.location.search).get('next'))
    router.replace(isAdminMfaRole(role) ? (next ?? '/admin') : (next ?? '/home'))
  }, [ready, role, router, pathname])

  return <p role="status" className="text-sm text-muted">{t('checking')}</p>
}
