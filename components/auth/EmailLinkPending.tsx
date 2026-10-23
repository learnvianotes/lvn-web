'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'

/**
 * Sign-up reached a verified account that has no password yet (made with Google, or another provider).
 * The same emailed /verify?token= link confirms the address and links the password; sign-in then reaches that account.
 */
export function EmailLinkPending({ email }: { email: string }) {
  const t = useTranslations('auth.linkPending')
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead', { email })}</p>
      </header>
      <Button asChild>
        <Link href="/sign-in">{t('signIn')}</Link>
      </Button>
    </div>
  )
}
