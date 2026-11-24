'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation } from '@apollo/client/react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { RequestPasswordResetDocument, ResetPasswordDocument } from '@/graphql/generated/graphql'
import { applyProblems } from './forms'

/** /reset: ask for a link by email; with ?token= from that link, choose the new password. */
export function ResetPanel() {
  const token = useSearchParams().get('token')
  return token ? <NewPassword token={token} /> : <RequestLink />
}

function RequestLink() {
  const t = useTranslations('auth.reset')
  const te = useTranslations('auth.errors')
  const [request] = useMutation(RequestPasswordResetDocument)
  const [sent, setSent] = useState(false)
  const [general, setGeneral] = useState<string | null>(null)
  const form = useForm<{ email: string }>({ resolver: zodResolver(z.object({ email: z.email() })), defaultValues: { email: '' } })

  const onSubmit = form.handleSubmit(async ({ email }) => {
    setGeneral(null)
    try {
      const { data } = await request({ variables: { email } })
      if (data?.requestPasswordReset.ok) setSent(true)
      else setGeneral(data?.requestPasswordReset.userErrors[0]?.message ?? te('generic'))
    } catch {
      setGeneral(te('generic'))
    }
  })

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {sent ? <Alert tone="success">{t('sent')}</Alert> : null}
      {general ? <Alert tone="error">{general}</Alert> : null}
      <Field label={t('email')} error={form.formState.errors.email ? te('email') : undefined}>
        <Input type="email" autoComplete="email" inputMode="email" {...form.register('email')} />
      </Field>
      <Button type="submit" size="lg" disabled={form.formState.isSubmitting}>{t('submit')}</Button>
    </form>
  )
}

function NewPassword({ token }: { token: string }) {
  const t = useTranslations('auth.reset')
  const ts = useTranslations('auth.signUp')
  const te = useTranslations('auth.errors')
  const [reset] = useMutation(ResetPasswordDocument)
  const [done, setDone] = useState(false)
  const [general, setGeneral] = useState<string | null>(null)
  const form = useForm<{ password: string }>({ resolver: zodResolver(z.object({ password: z.string().min(10) })), defaultValues: { password: '' } })
  const { errors } = form.formState

  const onSubmit = form.handleSubmit(async ({ password }) => {
    setGeneral(null)
    try {
      const { data } = await reset({ variables: { token, password } })
      const payload = data!.resetPassword
      if (payload.ok) return setDone(true)
      setGeneral(applyProblems(payload.userErrors, form.setError, ['password']))
    } catch {
      setGeneral(te('generic'))
    }
  })

  if (done) {
    return (
      <div className="flex flex-col gap-4">
        <Alert tone="success">{t('done')}</Alert>
        <Button asChild><Link href="/sign-in">{t('signIn')}</Link></Button>
      </div>
    )
  }
  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
      <h1 className="text-2xl font-semibold">{t('newTitle')}</h1>
      {general ? <Alert tone="error">{general}</Alert> : null}
      <Field label={t('password')} hint={ts('passwordHint')} error={errors.password ? (errors.password.type === 'server' ? errors.password.message : ts('passwordHint')) : undefined}>
        <Input type="password" autoComplete="new-password" {...form.register('password')} />
      </Field>
      <Button type="submit" size="lg" disabled={form.formState.isSubmitting}>{t('save')}</Button>
    </form>
  )
}
