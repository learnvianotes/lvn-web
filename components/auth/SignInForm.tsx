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
import { SignInDocument } from '@/graphql/generated/graphql'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { refusalMessage } from '@/lib/limit-error'
import { AgeBlocked } from './AgeBlocked'
import { InviteOnlyNotice } from './InviteOnlyNotice'
import { applyProblems } from './forms'
import { ProviderButtons } from './ProviderButtons'
import { useFinishSignIn } from './useFinishSignIn'

const schema = z.object({ email: z.email(), password: z.string().min(1) })
type Values = z.infer<typeof schema>

export function SignInForm() {
  const t = useTranslations('auth.signIn')
  const te = useTranslations('auth.errors')
  const params = useSearchParams()
  const next = params.get('next')
  const inviteFromQuery = params.get('error') === 'invite_only'
  const [signIn] = useMutation(SignInDocument)
  const finish = useFinishSignIn()
  const [general, setGeneral] = useState<string | null>(null)
  const [refused, setRefused] = useState<string | null>(null)
  const [hold, setHold] = useState<AgeHold | null>(null)
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { email: '', password: '' } })
  const { errors, isSubmitting } = form.formState

  const onSubmit = form.handleSubmit(async (values) => {
    setGeneral(null)
    setRefused(null)
    try {
      const { data } = await signIn({ variables: { input: values } })
      const payload = data!.signIn
      const ageHold = ageHoldFromProblems(payload.userErrors)
      if (ageHold) return setHold(ageHold)
      if (payload.session) return finish(payload.session, next, payload.mfaRequired)
      const blocked = payload.userErrors.find((error) => error.code === 'FORBIDDEN')
      const rest = blocked ? payload.userErrors.filter((error) => error !== blocked) : payload.userErrors
      if (blocked) setRefused(blocked.message)
      setGeneral(applyProblems(rest, form.setError, ['email', 'password']))
    } catch (error) {
      setGeneral(refusalMessage(error) ?? te('generic'))
    }
  })

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <InviteOnlyNotice />
      {inviteFromQuery || refused ? <Alert tone="error">{refused ?? te('inviteOnly')}</Alert> : null}
      <ProviderButtons next={next} onAgeHold={setHold} />
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
        {general ? <Alert tone="error">{general}</Alert> : null}
        <Field label={t('email')} error={errors.email ? te('email') : undefined}>
          <Input type="email" autoComplete="email" inputMode="email" {...form.register('email')} />
        </Field>
        <Field label={t('password')} error={errors.password ? (errors.password.type === 'server' ? errors.password.message : te('required')) : undefined}>
          <Input type="password" autoComplete="current-password" {...form.register('password')} />
        </Field>
        <Button type="submit" size="lg" disabled={isSubmitting}>{t('submit')}</Button>
        <Link href="/reset" className="text-center text-sm text-accent hover:underline">{t('forgot')}</Link>
      </form>
      <p className="text-center text-sm text-muted">
        {t('noAccount')} <Link href={next ? `/sign-up?next=${encodeURIComponent(next)}` : '/sign-up'} className="font-medium text-accent hover:underline">{t('signUp')}</Link>
      </p>
    </div>
  )
}
