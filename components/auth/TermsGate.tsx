'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { FileText } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { AcceptTermsDocument, TermsStatusDocument } from '@/graphql/generated/graphql'
import { ACCEPTED_DOCUMENTS, LEGAL_DOCUMENTS } from '@/features/legal/documents'

/**
 * Re-prompt on material change (§15.2): when the Terms, Privacy Policy and content licence have a new version, signed-in
 * pages wait until it is accepted. The account page stays open, so people who do not agree can sign out or leave.
 */
export function TermsGate() {
  const t = useTranslations('legalGate')
  const pathname = usePathname()
  const status = useQuery(TermsStatusDocument)
  const [accept, accepting] = useMutation(AcceptTermsDocument)
  const [error, setError] = useState<string | null>(null)
  const open = status.data?.viewer?.termsAccepted === false && pathname !== '/profile'
  if (!open) return null

  const agree = async () => {
    setError(null)
    const res = await accept({ variables: { version: status.data!.termsVersion } }).catch(() => null)
    if (res?.data?.acceptTerms.ok) await status.refetch()
    else setError(res?.data?.acceptTerms.userErrors[0]?.message ?? t('failed'))
  }

  return (
    <Dialog open persistent onClose={() => undefined} title={t('title')}>
      <div className="flex flex-col gap-4">
        <p className="text-sm text-muted">{t('lead')}</p>
        <ul className="flex flex-col gap-2">
          {ACCEPTED_DOCUMENTS.map((key) => LEGAL_DOCUMENTS[key]).map((d) => (
            <li key={d.path}>
              <Link href={d.path} target="_blank" className="flex items-center gap-2 rounded-xl border border-border bg-surface px-3 py-2 text-sm font-medium hover:border-accent hover:text-accent">
                <FileText className="size-4" aria-hidden />
                {d.title}
              </Link>
            </li>
          ))}
        </ul>
        {error ? (
          <p role="alert" className="text-sm text-bad">
            {error}
          </p>
        ) : null}
        <div className="flex flex-wrap items-center justify-between gap-2">
          <Link href="/profile" className="text-sm text-muted hover:text-fg hover:underline">
            {t('signOut')}
          </Link>
          <Button onClick={() => void agree()} disabled={accepting.loading}>
            {t('accept')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
