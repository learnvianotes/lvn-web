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
import { AGE_INPUT, markAgeRefused } from '@/lib/age'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { refusalMessage } from '@/lib/limit-error'
import { queueWalkthrough } from '@/lib/walkthrough'
import { AgeBlocked } from './AgeBlocked'
import { ageField, AgeRefused, ConfirmAge, useAgeMessage, useAgeRefused } from './AgeCheck'
import { InviteOnlyNotice } from './InviteOnlyNotice'
import { applyProblems } from './forms'
import { ProviderButtons } from './ProviderButtons'
import { useFinishSignIn } from './useFinishSignIn'

const schema = z.object({
  displayName: z.string().trim().min(1),
  email: z.email(),
  password: z.string().min(10),
  age: ageField,
  institutionalEmail: z.union([z.literal(''), z.email()]),
  terms: z.literal(true),
})
type Fields = z.input<typeof schema>
type Values = z.output<typeof schema>
const FIELDS = ['displayName', 'email', 'password', 'age', 'institutionalEmail'] as const

/**
 * Email + password registration with the details of ADR-0017; Google, GitHub and LinkedIn above it. The age, in whole
 * years (lvn-backend ADR-0104), is confirmed before anything is sent; a refusal (ADR-0091) closes this form on the
 * device for a day.
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
  // "I teach" leads to the application to teach after sign-up (lvn-backend ADR-0073).
  const [teaches, setTeaches] = useState(false)
  const refused = useAgeRefused()
  // The values waiting for "Is this right?" about the age.
  const [pending, setPending] = useState<Values | null>(null)
  const [sending, setSending] = useState(false)
  const form = useForm<Fields, unknown, Values>({
    resolver: zodResolver(schema),
    defaultValues: { displayName: '', email: '', password: '', age: '', institutionalEmail: '', terms: false as unknown as true },
  })
  const { errors, isSubmitting } = form.formState
  const ageMessage = useAgeMessage()

  const onSubmit = form.handleSubmit((values) => {
    setGeneral(null)
    setInviteMessage(null)
    setPending(values)
  })

  // Only `age` is sent; the deprecated `dateOfBirth` is for phone builds from before ADR-0104.
  const send = async ({ terms: _terms, institutionalEmail, ...values }: Values) => {
    setSending(true)
    try {
      const { data } = await signUp({
        variables: { input: { ...values, institutionalEmail: institutionalEmail || null, acceptedTermsVersion: options?.termsVersion ?? '' } },
      })
      const payload = data!.signUp
      // Creating an account still opens the account page. Signing in, with nowhere else to go, opens Home.
      if (payload.session) {
        // Email sign-up creates the profile here. Ages 8 to 17 are sent; the API marks the account restricted.
        if (payload.session.user.registrationComplete) queueWalkthrough(payload.session.user.id)
        return await finish(payload.session, teaches ? '/teach' : institutionalEmail ? '/verify' : (next || '/profile'), payload.mfaRequired)
      }
      // Too young for an account: nothing was created; this device keeps the form closed for a day.
      const ageHold = ageHoldFromProblems(payload.userErrors)
      if (ageHold) return setHold(ageHold)
      if (payload.userErrors.some((e) => e.code === 'UNDER_MINIMUM_AGE')) return markAgeRefused()
      const blocked = payload.userErrors.find((error) => error.code === 'FORBIDDEN')
      const rest = blocked ? payload.userErrors.filter((error) => error !== blocked) : payload.userErrors
      if (blocked) setInviteMessage(blocked.message)
      setGeneral(applyProblems(rest, form.setError, FIELDS))
    } catch (error) {
      setGeneral(refusalMessage(error) ?? te('generic'))
    } finally {
      setPending(null)
      setSending(false)
    }
  }

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />
  if (refused) return <AgeRefused />

  const message = (name: (typeof FIELDS)[number] | 'terms', fallback: string) => {
    const e = errors[name]
    if (!e) return undefined
    return e.type === 'server' ? e.message : fallback
  }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <InviteOnlyNotice />
      {inviteFromQuery || inviteMessage ? <Alert tone="error">{inviteMessage ?? te('inviteOnly')}</Alert> : null}
      <ProviderButtons next={next} onAgeHold={setHold} />
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
        {general ? <Alert tone="error">{general}</Alert> : null}
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm font-medium">{t('iAm')}</legend>
          <div className="grid grid-cols-2 gap-2">
            {([false, true] as const).map((v) => (
              <label key={String(v)} className={`flex cursor-pointer items-center justify-center gap-2 rounded-xl border px-3 py-2.5 text-sm font-medium ${teaches === v ? 'border-accent bg-accent-soft text-accent' : 'border-border'}`}>
                <input type="radio" name="iAm" className="sr-only" checked={teaches === v} onChange={() => setTeaches(v)} />
                {v ? t('teacher') : t('learner')}
              </label>
            ))}
          </div>
          {teaches ? <p className="text-xs text-muted">{t('teacherHint')}</p> : null}
        </fieldset>
        <Field label={t('name')} error={message('displayName', te('required'))}>
          <Input autoComplete="name" {...form.register('displayName')} />
        </Field>
        <Field label={t('email')} error={message('email', te('email'))}>
          <Input type="email" autoComplete="email" inputMode="email" {...form.register('email')} />
        </Field>
        <Field label={t('password')} hint={t('passwordHint')} error={message('password', t('passwordHint'))}>
          <Input type="password" autoComplete="new-password" {...form.register('password')} />
        </Field>
        <Field label={t('age')} hint={t('ageHint')} error={ageMessage(errors.age)}>
          <Input {...AGE_INPUT} className="max-w-32" {...form.register('age')} />
        </Field>
        <Field label={t('institutionalEmail')} hint={t('institutionalHint')} error={message('institutionalEmail', te('email'))}>
          <Input type="email" inputMode="email" {...form.register('institutionalEmail')} />
        </Field>
        <label className="flex items-start gap-3 text-sm">
          <input type="checkbox" className="mt-1 size-4 accent-[var(--accent)]" aria-invalid={errors.terms ? true : undefined} {...form.register('terms')} />
          <span>{t.rich('terms', legalLinks)}</span>
        </label>
        {errors.terms ? <p role="alert" className="-mt-2 text-xs font-medium text-red-600 dark:text-red-400">{t('termsRequired')}</p> : null}
        <Button type="submit" size="lg" disabled={isSubmitting || sending || !options}>{t('submit')}</Button>
      </form>
      <ConfirmAge
        age={pending?.age ?? null}
        busy={sending}
        onConfirm={() => pending && void send(pending)}
        onChange={() => {
          setPending(null)
          form.setFocus('age')
        }}
      />
      <p className="text-center text-sm text-muted">
        {t('haveAccount')} <Link href={next ? `/sign-in?next=${encodeURIComponent(next)}` : '/sign-in'} className="font-medium text-accent hover:underline">{t('signIn')}</Link>
      </p>
    </div>
  )
}
