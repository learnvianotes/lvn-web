'use client'

import { useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { ResourceDocument } from '@/graphql/generated/graphql'
import { isNotThere } from '@/lib/query'
import { ResourceForm } from './ResourceForm'

/** Its submitter's form for a waiting or rejected resource (lvn-backend ADR-0074); anything else is not theirs to edit. */
export function EditResource({ id }: { id: string }) {
  const t = useTranslations('resources')
  const { data, loading, error, refetch } = useQuery(ResourceDocument, { variables: { id }, fetchPolicy: 'network-only' })
  if (!data && loading) return <Loading className="py-16 text-center" />
  // Not there only when the API said so; a resource that could not be asked for is offered again.
  if (!data && error && !isNotThere(error)) return <LoadFailed className="mx-auto my-16 max-w-md" onRetry={refetch} />
  if (!data?.resource?.viewerCan.edit) return <p className="py-16 text-center text-sm text-muted">{t('notFound')}</p>
  return <ResourceForm resource={data.resource} />
}
