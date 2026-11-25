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
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { signedInDestination } from '@/lib/auth/destination'
import { signedOut } from '@/lib/auth/session'
import { queueWalkthrough } from '@/lib/walkthrough'
import { AgeBlocked } from './AgeBlocked'
import { applyProblems } from './forms'

const schema = z.object({ displayName: z.string().trim().min(1) })
type Values = z.infer<typeof schema>
const FIELDS = ['displayName'] as const

/**
 * The one step after a first Google sign-in (ADR-0017): confirm the name. No age is asked. Pressing Continue accepts
 * the Terms, as the line under it says.
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
  const form = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { displayName: '' } })
  const { errors, isSubmitting } = form.formState

  // Provider accounts arrive with a name; offer it.
  const name = viewer?.viewer?.displayName
  useEffect(() => {
    if (name && !form.getValues('displayName')) form.setValue('displayName', name)
  }, [name, form])
  useEffect(() => {
    if (viewer?.viewer?.registrationComplete) router.replace(signedInDestination(next))
  }, [viewer, router, next])

  const onSubmit = form.handleSubmit(async (values) => {
    setGeneral(null)
    try {
      const { data } = await complete({ variables: { input: { ...values, acceptedTermsVersion: options?.termsVersion ?? '' } } })
      const payload = data?.completeRegistration
      if (!payload) return setGeneral(te('generic'))
      const ageHold = ageHoldFromProblems(payload.userErrors)
      if (ageHold) {
        await signOut().catch(() => undefined)
        signedOut()
        await client.clearStore()
        return setHold(ageHold)
      }
      if (!payload.ok) return setGeneral(applyProblems(payload.userErrors, form.setError, FIELDS))
      await client.refetchQueries({ include: [ViewerDocument] })
      const id = client.readQuery({ query: ViewerDocument })?.viewer?.id
      if (id) queueWalkthrough(id)
      router.replace(signedInDestination(next))
    } catch {
      setGeneral(te('generic'))
    }
  })

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />

  const nameError = errors.displayName ? (errors.displayName.type === 'server' ? errors.displayName.message : te('required')) : undefined

  return (
    <div className="flex flex-col gap-5">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold tracking-tight">{name ? t('titleNamed', { name: name.split(' ')[0]! }) : t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <form onSubmit={onSubmit} noValidate className="flex flex-col gap-3">
        {general ? <Alert tone="error">{general}</Alert> : null}
        <Field label={ts('name')} error={nameError}>
          <Input autoComplete="name" {...form.register('displayName')} />
        </Field>
        <Button type="submit" size="lg" className="mt-1" disabled={isSubmitting || !options}>
          {t('submit')}
        </Button>
        <p className="text-xs leading-relaxed text-muted">{ts.rich('termsNotice', legalLinks)}</p>
      </form>
    </div>
  )
}
