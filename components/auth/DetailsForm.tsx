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
import { markAgeRefused } from '@/lib/age'
import { safeNext } from '@/lib/auth/destination'
import { signedOut } from '@/lib/auth/session'
import { AgeRefused, BirthDateHint, ConfirmBirthDate, useAgeRefused } from './AgeCheck'
import { applyProblems } from './forms'

const schema = z.object({
  displayName: z.string().trim().min(1),
  dateOfBirth: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  institutionalEmail: z.union([z.literal(''), z.email()]),
  terms: z.literal(true),
})
type Values = z.infer<typeof schema>
const FIELDS = ['displayName', 'dateOfBirth', 'institutionalEmail'] as const

/**
 * Registration details for accounts created by Google, GitHub or LinkedIn (ADR-0017), given once. The date of birth is
 * confirmed in words before it is sent. An answer under the minimum age (lvn-backend ADR-0091) makes the API erase this
 * unfinished account; the page then signs out here and shows the refusal. A refusal already on this device only closes
 * the form: the account is left alone, and the person may sign out.
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
  const refused = useAgeRefused()
  const [pending, setPending] = useState<Values | null>(null)
  const [sending, setSending] = useState(false)
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { displayName: '', dateOfBirth: '', institutionalEmail: '', terms: false as unknown as true } })
  const { errors, isSubmitting } = form.formState
  const dateOfBirth = form.watch('dateOfBirth')

  // Provider accounts arrive with a name; offer it.
  const name = viewer?.viewer?.displayName
  useEffect(() => {
    if (name && !form.getValues('displayName')) form.setValue('displayName', name)
  }, [name, form])
  useEffect(() => {
    if (viewer?.viewer?.registrationComplete) router.replace(safeNext(next) ?? '/profile')
  }, [viewer, router, next])

  const onSubmit = form.handleSubmit((values) => {
    setGeneral(null)
    setPending(values)
  })

  /** Leaves this browser's session (and its cache) behind; the API side is already gone or is ended here. */
  const leave = async (to: string) => {
    await signOut().catch(() => undefined)
    signedOut()
    await client.clearStore()
    router.replace(to)
  }

  const send = async ({ terms: _terms, institutionalEmail, ...values }: Values) => {
    setSending(true)
    try {
      const { data } = await complete({ variables: { input: { ...values, institutionalEmail: institutionalEmail || null, acceptedTermsVersion: options?.termsVersion ?? '' } } })
      const payload = data!.completeRegistration
      if (payload.userErrors.some((e) => e.code === 'UNDER_MINIMUM_AGE')) {
        // The API erased this unfinished account; the sign-up page shows the refusal from now on.
        markAgeRefused()
        return await leave('/sign-up')
      }
      if (!payload.ok) return setGeneral(applyProblems(payload.userErrors, form.setError, FIELDS))
      await client.refetchQueries({ include: [ViewerDocument] })
      router.replace(institutionalEmail ? '/verify' : (safeNext(next) ?? '/profile'))
    } catch {
      setGeneral(te('generic'))
    } finally {
      setPending(null)
      setSending(false)
    }
  }

  const message = (n: (typeof FIELDS)[number], fallback: string) => (errors[n] ? (errors[n]!.type === 'server' ? errors[n]!.message : fallback) : undefined)

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
        <h1 className="text-2xl font-bold tracking-tight">{name ? t('titleNamed', { name: name.split(' ')[0]! }) : t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
        {general ? <Alert tone="error">{general}</Alert> : null}
        <Field label={ts('name')} error={message('displayName', te('required'))}>
          <Input autoComplete="name" {...form.register('displayName')} />
        </Field>
        <Field label={ts('dob')} hint={<BirthDateHint value={dateOfBirth} hint={ts('dobHint')} />} error={message('dateOfBirth', te('required'))}>
          <Input type="date" autoComplete="bday" {...form.register('dateOfBirth')} />
        </Field>
        <Field label={ts('institutionalEmail')} hint={ts('institutionalHint')} error={message('institutionalEmail', te('email'))}>
          <Input type="email" inputMode="email" {...form.register('institutionalEmail')} />
        </Field>
        <label className="flex items-start gap-3 text-sm">
          <input type="checkbox" className="mt-1 size-4 accent-[var(--accent)]" {...form.register('terms')} />
          <span>{ts.rich('terms', legalLinks)}</span>
        </label>
        {errors.terms ? <p role="alert" className="-mt-2 text-xs font-medium text-red-600 dark:text-red-400">{ts('termsRequired')}</p> : null}
        <Button type="submit" size="lg" disabled={isSubmitting || sending || !options}>{t('submit')}</Button>
      </form>
      <ConfirmBirthDate
        value={pending?.dateOfBirth ?? null}
        busy={sending}
        onConfirm={() => pending && void send(pending)}
        onChange={() => {
          setPending(null)
          form.setFocus('dateOfBirth')
        }}
      />
    </div>
  )
}
