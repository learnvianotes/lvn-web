'use client'

import { useMutation } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { UnsubscribeEmailDocument } from '@/graphql/generated/graphql'

/**
 * /unsubscribe?t= (lvn-backend ADR-0050): the link in an email. It asks for one click, so a link scanner opening the
 * page changes nothing; mail clients' one-click POST goes to /unsubscribe/one-click instead.
 */
export function Unsubscribe({ token }: { token: string }) {
  return (
    <AuthProvider>
      <Inner token={token} />
    </AuthProvider>
  )
}

function Inner({ token }: { token: string }) {
  const t = useTranslations('settings')
  const [run, running] = useMutation(UnsubscribeEmailDocument)
  const [done, setDone] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const go = async () => {
    const res = await run({ variables: { token } }).catch(() => null)
    const payload = res?.data?.unsubscribeEmail
    if (payload?.kind) setDone(payload.kind)
    else setError(payload?.userErrors[0]?.message ?? t('failed'))
  }
  return (
    <div className="mx-auto flex max-w-md flex-col gap-4 px-4 py-16">
      <h1 className="text-2xl font-extrabold tracking-tight">{t('unsubscribeTitle')}</h1>
      {done ? (
        <p role="status">{t(`unsubscribed.${done}`)}</p>
      ) : (
        <>
          <p className="text-muted">{t('unsubscribeLead')}</p>
          <Button className="w-fit" disabled={!token || running.loading} onClick={() => void go()}>
            {t('unsubscribe')}
          </Button>
        </>
      )}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <Link href="/profile/notifications" className="text-sm text-accent hover:underline">
        {t('allSettings')}
      </Link>
    </div>
  )
}
