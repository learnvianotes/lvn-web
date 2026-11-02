'use client'

import { useQuery } from '@apollo/client/react'
import { UnverifiedGatedActionsDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { holdsVerification, isGated } from '@/lib/auth/gates'

/** The signed-in viewer and the public list of actions closed until their sign-in email is confirmed. */
export function useUnverifiedGates() {
  const viewer = useQuery(ViewerDocument).data?.viewer
  const held = holdsVerification(viewer)
  const listed = useQuery(UnverifiedGatedActionsDocument, { skip: !held, fetchPolicy: 'cache-first' }).data?.unverifiedGatedActions
  return {
    viewer,
    held,
    actions: held ? (listed ?? []) : [],
    gated: (action: string) => isGated(viewer, listed, action),
  }
}
