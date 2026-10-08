'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { CompleteRegistrationDocument, SignInOptionsDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { safeNext } from '@/lib/auth/destination'
import { applyProblems } from './forms'

const schema = z.object({
  displayName: z.string().trim().min(1),
  dateOfBirth: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  institutionalEmail: z.union([z.literal(''), z.email()]),
  terms: z.literal(true),
})
type Values = z.infer<typeof schema>
const FIELDS = ['displayName', 'dateOfBirth', 'institutionalEmail'] as const

/** Registration details for accounts created by Google, GitHub or LinkedIn (ADR-0017), given once. */
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
  const [general, setGeneral] = useState<string | null>(null)
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { displayName: '', dateOfBirth: '', institutionalEmail: '', terms: false as unknown as true } })
  const { errors, isSubmitting } = form.formState

  // Provider accounts arrive with a name; offer it.
  const name = viewer?.viewer?.displayName
  useEffect(() => {
    if (name && !form.getValues('displayName')) form.setValue('displayName', name)
  }, [name, form])
  useEffect(() => {
    if (viewer?.viewer?.registrationComplete) router.replace(safeNext(next) ?? '/profile')
  }, [viewer, router, next])

  const onSubmit = form.handleSubmit(async ({ terms: _terms, institutionalEmail, ...values }) => {
    setGeneral(null)
    try {
      const { data } = await complete({ variables: { input: { ...values, institutionalEmail: institutionalEmail || null, acceptedTermsVersion: options?.termsVersion ?? '' } } })
      const payload = data!.completeRegistration
      if (!payload.ok) return setGeneral(applyProblems(payload.userErrors, form.setError, FIELDS))
      await client.refetchQueries({ include: [ViewerDocument] })
      router.replace(institutionalEmail ? '/verify' : (safeNext(next) ?? '/profile'))
    } catch {
      setGeneral(te('generic'))
    }
  })

  const message = (n: (typeof FIELDS)[number], fallback: string) => (errors[n] ? (errors[n]!.type === 'server' ? errors[n]!.message : fallback) : undefined)

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
        <Field label={ts('dob')} hint={ts('dobHint')} error={message('dateOfBirth', te('required'))}>
          <Input type="date" autoComplete="bday" {...form.register('dateOfBirth')} />
        </Field>
        <Field label={ts('institutionalEmail')} hint={ts('institutionalHint')} error={message('institutionalEmail', te('email'))}>
          <Input type="email" inputMode="email" {...form.register('institutionalEmail')} />
        </Field>
        <label className="flex items-start gap-3 text-sm">
          <input type="checkbox" className="mt-1 size-4 accent-[var(--accent)]" {...form.register('terms')} />
          <span>{ts('terms')}</span>
        </label>
        {errors.terms ? <p role="alert" className="-mt-2 text-xs font-medium text-red-600 dark:text-red-400">{ts('termsRequired')}</p> : null}
        <Button type="submit" size="lg" disabled={isSubmitting || !options}>{t('submit')}</Button>
      </form>
    </div>
  )
}
