'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { legalLinks } from '@/features/legal/links'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { CompleteRegistrationDocument, SignInOptionsDocument, SignOutDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { AGE_INPUT, markAgeRefused } from '@/lib/age'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { signedInDestination } from '@/lib/auth/destination'
import { signedOut } from '@/lib/auth/session'
import { queueWalkthrough } from '@/lib/walkthrough'
import { AgeBlocked } from './AgeBlocked'
import { ageField, AgeRefused, useAgeMessage, useAgeRefused } from './AgeCheck'
import { applyProblems } from './forms'

const schema = z.object({
  displayName: z.string().trim().min(1),
  age: ageField,
  institutionalEmail: z.union([z.literal(''), z.email()]),
  terms: z.literal(true),
})
type Fields = z.input<typeof schema>
type Values = z.output<typeof schema>
const FIELDS = ['displayName', 'age', 'institutionalEmail'] as const

/**
 * Registration details for accounts created by Google, GitHub or LinkedIn (ADR-0017), given once. The age, in whole
 * years (lvn-backend ADR-0104), is checked by the form and then sent. An answer under 13 (ADR-0091) signs out
 * here and shows the outcome: AGE_RESTRICTED (the account is held) names who to contact, UNDER_MINIMUM_AGE shows the
 * refusal. A refusal already on this device only closes the form: the account is left alone, and the person may sign
 * out.
 */
export function DetailsForm() {
  const t = useTranslations('auth.details')
  const ts = useTranslations('auth.signUp')
  const te = useTranslations('auth.errors')
  const next = useSearchParams().get('next')
  const router = useRouter()
  const client = useApolloClient()
  const { data: viewer } = useQuery(ViewerDocument)
  const { data: options } = useQuery(SignInOptionsDocument)
  const [complete] = useMutation(CompleteRegistrationDocument)
  const [signOut] = useMutation(SignOutDocument)
  const [general, setGeneral] = useState<string | null>(null)
  const [hold, setHold] = useState<AgeHold | null>(null)
  const refused = useAgeRefused()
  const form = useForm<Fields, unknown, Values>({ resolver: zodResolver(schema), defaultValues: { displayName: '', age: '', institutionalEmail: '', terms: false as unknown as true } })
  const { errors, isSubmitting } = form.formState
  const ageMessage = useAgeMessage()

  // Provider accounts arrive with a name; offer it.
  const name = viewer?.viewer?.displayName
  useEffect(() => {
    if (name && !form.getValues('displayName')) form.setValue('displayName', name)
  }, [name, form])
  useEffect(() => {
    if (viewer?.viewer?.registrationComplete) router.replace(signedInDestination(next))
  }, [viewer, router, next])

  /** Leaves this browser's session (and its cache) behind; the API side is already gone or is ended here. */
  const leave = async (to: string) => {
    await signOut().catch(() => undefined)
    signedOut()
    await client.clearStore()
    router.replace(to)
  }

  // Only `age` is sent; the deprecated `dateOfBirth` is for phone builds from before ADR-0104.
  const send = async ({ terms: _terms, institutionalEmail, ...values }: Values) => {
    try {
      const { data } = await complete({ variables: { input: { ...values, institutionalEmail: institutionalEmail || null, acceptedTermsVersion: options?.termsVersion ?? '' } } })
      // Extra fields on the payload (a welcome email, for example) are ignored: only ok and userErrors are read.
      const payload = data?.completeRegistration
      if (!payload) return setGeneral(te('generic'))
      const ageHold = ageHoldFromProblems(payload.userErrors)
      if (ageHold) {
        await signOut().catch(() => undefined)
        signedOut()
        await client.clearStore()
        setHold(ageHold)
        return
      }
      if (payload.userErrors.some((e) => e.code === 'UNDER_MINIMUM_AGE')) {
        // The API erased this unfinished account; the sign-up page shows the refusal from now on.
        markAgeRefused()
        return await leave('/sign-up')
      }
      if (!payload.ok) return setGeneral(applyProblems(payload.userErrors, form.setError, FIELDS))
      await client.refetchQueries({ include: [ViewerDocument] })
      const id = client.readQuery({ query: ViewerDocument })?.viewer?.id
      if (id) queueWalkthrough(id)
      router.replace(institutionalEmail ? '/verify' : signedInDestination(next))
    } catch {
      setGeneral(te('generic'))
    }
  }

  const onSubmit = form.handleSubmit(async (values) => {
    setGeneral(null)
    await send(values)
  })

  const message = (n: (typeof FIELDS)[number], fallback: string) => (errors[n] ? (errors[n]!.type === 'server' ? errors[n]!.message : fallback) : undefined)

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />

  if (refused) {
    return (
      <AgeRefused
        action={
          <Button type="button" variant="secondary" onClick={() => void leave('/')}>
            {t('signOut')}
          </Button>
        }
      />
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">{name ? t('titleNamed', { name: name.split(' ')[0]! }) : t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
        {general ? <Alert tone="error">{general}</Alert> : null}
        <Field label={ts('name')} error={message('displayName', te('required'))}>
          <Input autoComplete="name" {...form.register('displayName')} />
        </Field>
        <Field label={ts('age')} hint={ts('ageHint')} error={ageMessage(errors.age)}>
          <Input {...AGE_INPUT} className="max-w-32" {...form.register('age')} />
        </Field>
        <Field label={ts('institutionalEmail')} hint={ts('institutionalHint')} error={message('institutionalEmail', te('email'))}>
          <Input type="email" inputMode="email" {...form.register('institutionalEmail')} />
        </Field>
        <label className="flex items-start gap-3 text-sm">
          <input type="checkbox" className="mt-1 size-4 accent-[var(--accent)]" {...form.register('terms')} />
          <span>{ts.rich('terms', legalLinks)}</span>
        </label>
        {errors.terms ? <p role="alert" className="-mt-2 text-xs font-medium text-bad">{ts('termsRequired')}</p> : null}
        <Button type="submit" size="lg" disabled={isSubmitting || !options}>{t('submit')}</Button>
      </form>
    </div>
  )
}
