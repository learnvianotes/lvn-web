'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { legalLinks } from '@/features/legal/links'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { SignInOptionsDocument, SignUpDocument } from '@/graphql/generated/graphql'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { refusalMessage } from '@/lib/limit-error'
import { queueWalkthrough } from '@/lib/walkthrough'
import { AgeBlocked } from './AgeBlocked'
import { InviteOnlyNotice } from './InviteOnlyNotice'
import { applyProblems } from './forms'
import { ProviderButtons } from './ProviderButtons'
import { useFinishSignIn } from './useFinishSignIn'

const schema = z.object({
  displayName: z.string().trim().min(1),
  email: z.email(),
  password: z.string().min(10),
})
type Values = z.infer<typeof schema>
const FIELDS = ['displayName', 'email', 'password'] as const

/**
 * Sign-up on one screen: Google first, then name, email and password. No age is asked (the API no longer needs one).
 * Pressing the button accepts the Terms, as the line under it says. A college email is added later from /verify.
 */
export function SignUpForm() {
  const t = useTranslations('auth.signUp')
  const te = useTranslations('auth.errors')
  const params = useSearchParams()
  const next = params.get('next')
  const inviteFromQuery = params.get('error') === 'invite_only'
  const { data: options } = useQuery(SignInOptionsDocument)
  const [signUp] = useMutation(SignUpDocument)
  const finish = useFinishSignIn()
  const [general, setGeneral] = useState<string | null>(null)
  const [hold, setHold] = useState<AgeHold | null>(null)
  const [inviteMessage, setInviteMessage] = useState<string | null>(null)
  // Teachers go on to the application to teach after sign-up (lvn-backend ADR-0073).
  const teaches = params.get('as') === 'teacher'
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { displayName: '', email: '', password: '' } })
  const { errors, isSubmitting } = form.formState

  const onSubmit = form.handleSubmit(async (values) => {
    setGeneral(null)
    setInviteMessage(null)
    try {
      const { data } = await signUp({ variables: { input: { ...values, acceptedTermsVersion: options?.termsVersion ?? '' } } })
      const payload = data!.signUp
      if (payload.session) {
        if (payload.session.user.registrationComplete) queueWalkthrough(payload.session.user.id)
        return await finish(payload.session, teaches ? '/teach' : next || '/home', payload.mfaRequired)
      }
      const ageHold = ageHoldFromProblems(payload.userErrors)
      if (ageHold) return setHold(ageHold)
      const blocked = payload.userErrors.find((error) => error.code === 'FORBIDDEN')
      const rest = blocked ? payload.userErrors.filter((error) => error !== blocked) : payload.userErrors
      if (blocked) setInviteMessage(blocked.message)
      setGeneral(applyProblems(rest, form.setError, FIELDS))
    } catch (error) {
      setGeneral(refusalMessage(error) ?? te('generic'))
    }
  })

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />

  const message = (name: (typeof FIELDS)[number], fallback: string) => {
    const e = errors[name]
    if (!e) return undefined
    return e.type === 'server' ? e.message : fallback
  }

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">{teaches ? t('titleTeacher') : t('title')}</h1>
        <p className="text-sm text-muted">{teaches ? t('teacherHint') : t('lead')}</p>
      </header>
      <InviteOnlyNotice />
      {inviteFromQuery || inviteMessage ? <Alert tone="error">{inviteMessage ?? te('inviteOnly')}</Alert> : null}
      <ProviderButtons next={teaches ? '/teach' : next} onAgeHold={setHold} />
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-3">
        {general ? <Alert tone="error">{general}</Alert> : null}
        <Field label={t('name')} error={message('displayName', te('required'))}>
          <Input autoComplete="name" {...form.register('displayName')} />
        </Field>
        <Field label={t('email')} error={message('email', te('email'))}>
          <Input type="email" autoComplete="email" inputMode="email" {...form.register('email')} />
        </Field>
        <Field label={t('password')} error={message('password', t('passwordHint'))}>
          <Input type="password" autoComplete="new-password" placeholder={t('passwordPlaceholder')} {...form.register('password')} />
        </Field>
        <Button type="submit" size="lg" className="mt-1" disabled={isSubmitting || !options}>
          {t('submit')}
        </Button>
        <p className="text-xs leading-relaxed text-muted">{t.rich('termsNotice', legalLinks)}</p>
      </form>
      <p className="text-sm text-muted">
        {t('haveAccount')}{' '}
        <Link href={next ? `/sign-in?next=${encodeURIComponent(next)}` : '/sign-in'} className="font-medium text-accent hover:underline">
          {t('signIn')}
        </Link>
        {teaches ? null : (
          <>
            {' · '}
            <Link href="/sign-up?as=teacher" className="font-medium text-fg hover:underline">
              {t('teacherLink')}
            </Link>
          </>
        )}
      </p>
    </div>
  )
}
