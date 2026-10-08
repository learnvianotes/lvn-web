import Link from 'next/link'
import type { ReactNode } from 'react'
import { LEGAL_DOCUMENTS } from './documents'

/** Links for `<terms>`, `<privacy>` and `<licence>` in translated sentences; they open beside forms, keeping what was typed. */
function link(path: string) {
  return function LegalLink(chunks: ReactNode) {
    return (
      <Link href={path} target="_blank" className="font-medium text-accent underline-offset-2 hover:underline">
        {chunks}
      </Link>
    )
  }
}

export const legalLinks = {
  terms: link(LEGAL_DOCUMENTS.terms.path),
  privacy: link(LEGAL_DOCUMENTS.privacy.path),
  licence: link(LEGAL_DOCUMENTS.licence.path),
}
