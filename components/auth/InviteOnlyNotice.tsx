'use client'

import { useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { Alert } from '@/components/ui/alert'
import { AccessPolicyDocument } from '@/graphql/generated/graphql'

/** A calm note when the beta allowlist is on. A refused sign-in is a separate error. */
export function InviteOnlyNotice() {
  const t = useTranslations('auth.invite')
  const { data } = useQuery(AccessPolicyDocument, { fetchPolicy: 'cache-first' })
  if (!data?.accessPolicy.inviteOnly) return null
  return <Alert tone="info">{t('notice')}</Alert>
}
