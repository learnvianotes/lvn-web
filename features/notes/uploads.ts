'use client'

import { useQuery } from '@apollo/client/react'
import { useEffect } from 'react'
import { UploadsEnabledDocument } from '@/graphql/generated/graphql'

/**
 * Whether people may upload files here (lvn-backend ADR-0097: off for the launch). While it is false — and until the API
 * has said — every upload control is hidden: media cards, voice notes, quick notes from photos and PDFs, reading a PDF,
 * imports, pictures and proof documents. Nothing is shown that would only fail.
 */
export function useUploadsEnabled(): boolean {
  const { data } = useQuery(UploadsEnabledDocument, { fetchPolicy: 'cache-first' })
  const enabled = data?.uploadsEnabled ?? false
  useEffect(() => {
    uploads.enabled = enabled
  }, [enabled])
  return enabled
}

/** The same answer for code outside React's render: the editor's slash menu, drop and paste. */
export const uploads = { enabled: false }
