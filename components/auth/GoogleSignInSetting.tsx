'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { AuthSettingsDocument, SetGoogleSignInEnabledDocument, ViewerDocument } from '@/graphql/generated/graphql'

/**
 * Platform admins turn Google sign-in on or off (lvn-backend authSettings). The choice is stored by the API.
 * Continue with Google still stays hidden on a deployment with no Firebase project.
 */
export function GoogleSignInSetting() {
  const t = useTranslations('authAdmin')
  const viewer = useQuery(ViewerDocument)
  const settings = useQuery(AuthSettingsDocument)
  const client = useApolloClient()
  const [save, saving] = useMutation(SetGoogleSignInEnabledDocument)
  const [error, setError] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [pending, setPending] = useState<boolean | null>(null)

  if (!viewer.data && !viewer.error) return <p className="text-muted">{t('loading')}</p>

  const forbidden =
    viewer.data?.viewer?.globalRole !== 'PLATFORM_ADMIN'
    || (CombinedGraphQLErrors.is(settings.error) && settings.error.errors.some((item) => item.extensions?.code === 'FORBIDDEN'))
    || (CombinedGraphQLErrors.is(viewer.error) && viewer.error.errors.some((item) => item.extensions?.code === 'FORBIDDEN'))
  if (forbidden) return <p className="text-muted">{t('notAllowed')}</p>

  const current = settings.data?.authSettings.googleSignInEnabled
  if (current === undefined && !settings.error) return <p className="text-muted">{t('loading')}</p>
  if (current === undefined) return <Alert tone="error">{t('failed')}</Alert>

  const on = pending ?? current
  const toggle = async (enabled: boolean) => {
    setError(null)
    setSaved(false)
    setPending(enabled)
    try {
      const { data } = await save({ variables: { enabled } })
      const payload = data?.setGoogleSignInEnabled
      const next = payload?.settings?.googleSignInEnabled
      if (payload?.userErrors.length || next === undefined || next === null) {
        setPending(null)
        setError(payload?.userErrors[0]?.message ?? t('failed'))
        return
      }
      client.writeQuery({ query: AuthSettingsDocument, data: { authSettings: { googleSignInEnabled: next } } })
      setPending(next)
      setSaved(true)
    } catch {
      setPending(null)
      setError(t('failed'))
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {error ? <Alert tone="error">{error}</Alert> : null}
      <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-border bg-surface p-4">
        <span className="flex min-w-0 flex-1 flex-col">
          <span id="google-sign-in-label" className="text-sm font-semibold">{t('google')}</span>
          <span className="text-xs leading-5 text-muted">{t('googleHint')}</span>
        </span>
        <input
          type="checkbox"
          role="switch"
          aria-labelledby="google-sign-in-label"
          className="peer sr-only"
          checked={on}
          disabled={saving.loading}
          onChange={(event) => void toggle(event.target.checked)}
        />
        <span aria-hidden className="relative mt-0.5 h-6 w-11 shrink-0 rounded-full bg-surface-2 ring-1 ring-border transition after:absolute after:left-0.5 after:top-0.5 after:size-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:bg-accent peer-checked:after:translate-x-5 peer-focus-visible:ring-2 peer-focus-visible:ring-accent" />
      </label>
      {saved ? <p role="status" className="text-sm text-muted">{t('saved')}</p> : null}
    </div>
  )
}
