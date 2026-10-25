'use client'

import { useQuery } from '@apollo/client/react'
import { ViewerDocument } from '@/graphql/generated/graphql'

/** The signed-in person's role, once the viewer query has answered. */
export function useViewerRole() {
  const q = useQuery(ViewerDocument)
  return { role: q.data?.viewer?.globalRole ?? null, ready: Boolean(q.data) || !q.loading }
}
