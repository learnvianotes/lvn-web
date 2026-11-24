'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { browserSupportsWebAuthn, startRegistration } from '@simplewebauthn/browser'
import { KeyRound, Trash2 } from 'lucide-react'
import { useFormatter, useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { FinishPasskeyRegistrationDocument, MyPasskeysDocument, RemovePasskeyDocument, StartPasskeyRegistrationDocument } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { refusalMessage } from '@/lib/limit-error'

/** A name for this device from the browser, e.g. "Chrome on Android". The person can keep it. */
function deviceName(): string {
  if (typeof navigator === 'undefined') return 'Passkey'
  const ua = navigator.userAgent
  const os = /Android/.test(ua) ? 'Android' : /iPhone|iPad/.test(ua) ? 'iPhone' : /Mac OS X/.test(ua) ? 'Mac' : /Windows/.test(ua) ? 'Windows' : /Linux/.test(ua) ? 'Linux' : 'this device'
  const browser = /Edg\//.test(ua) ? 'Edge' : /Firefox\//.test(ua) ? 'Firefox' : /Chrome\//.test(ua) ? 'Chrome' : /Safari\//.test(ua) ? 'Safari' : 'Browser'
  return `${browser} on ${os}`
}

/**
 * Passkeys for this account (lvn-backend ADR-0115): add one for this device, see where each was made and last used,
 * remove one. Only the public key is stored on our side.
 */
export function PasskeySettings({ className }: { className?: string }) {
  const t = useTranslations('profile.passkeys')
  const format = useFormatter()
  const { data, refetch } = useQuery(MyPasskeysDocument)
  const [start] = useMutation(StartPasskeyRegistrationDocument)
  const [finish] = useMutation(FinishPasskeyRegistrationDocument)
  const [remove] = useMutation(RemovePasskeyDocument)
  const [supported, setSupported] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [done, setDone] = useState<string | null>(null)
  useEffect(() => setSupported(browserSupportsWebAuthn()), [])
  const passkeys = data?.myPasskeys ?? []

  const add = async () => {
    setBusy(true)
    setError(null)
    setDone(null)
    try {
      const { data: begun } = await start()
      const options = begun?.startPasskeyRegistration.optionsJson
      if (!options) throw new Error('no options')
      let response
      try {
        response = await startRegistration({ optionsJSON: JSON.parse(options) })
      } catch {
        setError(t('cancelled'))
        return
      }
      const { data: saved } = await finish({ variables: { input: { responseJson: JSON.stringify(response), name: deviceName() } } })
      const problem = saved?.finishPasskeyRegistration.userErrors[0]
      if (problem) return setError(problem.message)
      setDone(t('added'))
      await refetch()
    } catch (e) {
      setError(refusalMessage(e) ?? t('failed'))
    } finally {
      setBusy(false)
    }
  }

  const drop = async (id: string) => {
    setError(null)
    setDone(null)
    const { data: res } = await remove({ variables: { id } }).catch(() => ({ data: null }))
    const problem = res?.removePasskey.userErrors[0]
    if (!res?.removePasskey.ok) return setError(problem?.message ?? t('failed'))
    await refetch()
  }

  return (
    <section className={cn(className)} aria-labelledby="passkeys">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <h2 id="passkeys" className="text-lg font-medium">{t('title')}</h2>
          <p className="max-w-prose text-sm text-muted">{t('lead')}</p>
        </div>
        {supported ? (
          <Button variant="secondary" disabled={busy} onClick={() => void add()} className="gap-2">
            <KeyRound className="size-4" strokeWidth={1.5} aria-hidden />
            {busy ? t('adding') : t('add')}
          </Button>
        ) : null}
      </div>
      {!supported ? <p className="mt-3 text-sm text-muted">{t('unsupported')}</p> : null}
      {error ? <Alert tone="error" className="mt-3">{error}</Alert> : null}
      {done ? <Alert tone="success" className="mt-3">{done}</Alert> : null}
      {passkeys.length ? (
        <ul className="mt-4 divide-y divide-border rounded-xl border border-border">
          {passkeys.map((p) => (
            <li key={p.id} className="flex items-center gap-3 px-4 py-3">
              <KeyRound className="size-[18px] shrink-0 text-muted" strokeWidth={1.5} aria-hidden />
              <div className="flex min-w-0 flex-1 flex-col">
                <span className="truncate text-sm font-medium">{p.name}</span>
                <span className="text-xs text-muted">
                  {t('made', { date: format.dateTime(new Date(p.createdAt), { dateStyle: 'medium' }) })}
                  {p.lastUsedAt ? ` · ${t('used', { date: format.relativeTime(new Date(p.lastUsedAt)) })}` : ''}
                  {p.backedUp ? ` · ${t('synced')}` : ''}
                </span>
              </div>
              <Button variant="ghost" size="icon" aria-label={t('remove', { name: p.name })} onClick={() => void drop(p.id)}>
                <Trash2 className="size-4" strokeWidth={1.5} aria-hidden />
              </Button>
            </li>
          ))}
        </ul>
      ) : supported ? (
        <p className="mt-3 text-sm text-muted">{t('none')}</p>
      ) : null}
    </section>
  )
}
