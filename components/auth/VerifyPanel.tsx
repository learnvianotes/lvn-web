'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { ResendInstitutionalEmailCodeDocument, VerifyEmailDocument, VerifyInstitutionalEmailDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { refreshSession } from '@/lib/auth/session'
import { useSession } from '@/state/session'

/**
 * /verify: with ?token= it confirms the sign-in email from the emailed link; without, it takes the 6-digit code sent
 * to the college or organisation email (ADR-0017).
 */
export function VerifyPanel() {
  const token = useSearchParams().get('token')
  return token ? <EmailLink token={token} /> : <InstitutionalCode />
}

function EmailLink({ token }: { token: string }) {
  const t = useTranslations('auth.verify')
  const client = useApolloClient()
  const status = useSession((s) => s.status)
  const [verify, { data, error }] = useMutation(VerifyEmailDocument)
  const started = useRef(false)
  useEffect(() => {
    if (status === 'unknown' || started.current) return
    started.current = true
    void (async () => {
      try {
        const { data: res } = await verify({ variables: { token } })
        const user = res?.verifyEmail.user
        if (res?.verifyEmail.ok && user) {
          const cacheId = client.cache.identify({ __typename: 'User', id: user.id })
          if (cacheId) {
            client.cache.modify({
              id: cacheId,
              fields: {
                emailVerified: () => user.emailVerified,
                verified: () => user.verified,
                verificationMethod: () => user.verificationMethod,
              },
            })
          }
        }
        if (res?.verifyEmail.ok && useSession.getState().status === 'signed-in') {
          await refreshSession()
          await client.query({ query: ViewerDocument, fetchPolicy: 'network-only' })
        }
      } catch {
        // The mutation result renders the error.
      }
    })()
  }, [client, status, token, verify])
  const result = data?.verifyEmail
  if (!result && !error) return <p role="status" className="text-sm text-muted">{t('checking')}</p>
  if (result?.ok) {
    return (
      <div className="flex flex-col gap-4">
        <Alert tone="success">{t('emailDone')}</Alert>
        {result.user?.verified ? <Alert tone="success">{t('accountVerified')}</Alert> : null}
        <Button asChild><Link href="/profile">{t('continue')}</Link></Button>
      </div>
    )
  }
  return <Alert tone="error">{result?.userErrors[0]?.message ?? error?.message}</Alert>
}

function InstitutionalCode() {
  const t = useTranslations('auth.verify')
  const tn = useTranslations('auth.nav')
  const te = useTranslations('auth.errors')
  const status = useSession((s) => s.status)
  const client = useApolloClient()
  const { data } = useQuery(ViewerDocument, { skip: status !== 'signed-in' })
  const [verify] = useMutation(VerifyInstitutionalEmailDocument)
  const [resend] = useMutation(ResendInstitutionalEmailCodeDocument)
  const [code, setCode] = useState('')
  const [problem, setProblem] = useState<string | null>(null)
  const [note, setNote] = useState<string | null>(null)
  const viewer = data?.viewer

  if (status === 'signed-out') {
    return (
      <div className="flex flex-col gap-4">
        <Alert>{t('signInFirst')}</Alert>
        <Button asChild><Link href="/sign-in?next=/verify">{tn('signInAction')}</Link></Button>
      </div>
    )
  }
  if (!viewer) return <p role="status" className="text-sm text-muted">{t('checking')}</p>
  if (viewer.institutionalEmailStatus === 'CONFIRMED') return <Alert tone="success">{t('codeDone')}</Alert>
  if (viewer.institutionalEmailStatus === 'PENDING_REVIEW') return <Alert>{t('pendingReview')}</Alert>

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setProblem(null)
    setNote(null)
    try {
      const { data: res } = await verify({ variables: { code } })
      if (res?.verifyInstitutionalEmail.ok) await client.refetchQueries({ include: [ViewerDocument] })
      else setProblem(res?.verifyInstitutionalEmail.userErrors[0]?.message ?? te('generic'))
    } catch {
      setProblem(te('generic'))
    }
  }
  const again = async () => {
    setProblem(null)
    const { data: res } = await resend()
    if (res?.resendInstitutionalEmailCode.ok) setNote(t('resent'))
    else setProblem(res?.resendInstitutionalEmailCode.userErrors[0]?.message ?? te('generic'))
  }

  return (
    <form onSubmit={submit} className="flex flex-col gap-4" noValidate>
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t('codeTitle')}</h1>
        <p className="text-sm text-muted">{t('codeLead', { email: viewer.institutionalEmail ?? '' })}</p>
      </header>
      {note ? <Alert tone="success">{note}</Alert> : null}
      <Field label={t('code')} error={problem ?? undefined}>
        <Input value={code} onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))} inputMode="numeric" autoComplete="one-time-code" className="text-center text-2xl tracking-[0.5em]" />
      </Field>
      <Button type="submit" size="lg" disabled={code.length !== 6}>{t('submitCode')}</Button>
      <Button type="button" variant="ghost" onClick={() => void again()}>{t('resend')}</Button>
    </form>
  )
}
