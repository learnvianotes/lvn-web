'use client'

import { useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { ResourceDocument } from '@/graphql/generated/graphql'
import { ResourceForm } from './ResourceForm'

/** Its submitter's form for a waiting or rejected resource (lvn-backend ADR-0074); anything else is not theirs to edit. */
export function EditResource({ id }: { id: string }) {
  const t = useTranslations('resources')
  const { data } = useQuery(ResourceDocument, { variables: { id }, fetchPolicy: 'network-only' })
  if (!data) return null
  if (!data.resource?.viewerCan.edit) return <p className="py-16 text-center text-sm text-muted">{t('notFound')}</p>
  return <ResourceForm resource={data.resource} />
}
