'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { AlertTriangle } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useId, useState } from 'react'
import { Button } from '@/components/ui/button'
import { CancelAccountDeletionDocument, RequestAccountDeletionDocument, ViewerDocument } from '@/graphql/generated/graphql'

const day = (iso: string) => new Date(iso).toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric' })

/**
 * Settings → Delete your account (lvn-backend ADR-0088): the password (when the account has one) and the word DELETE ask
 * for it; 14 days later it goes. Until then the date shows here and on every page, with Keep my account.
 */
export function DeleteAccount() {
  const t = useTranslations('data.delete')
  const ids = { password: useId(), confirm: useId() }
  const viewer = useQuery(ViewerDocument).data?.viewer
  const [request, requesting] = useMutation(RequestAccountDeletionDocument, { refetchQueries: [ViewerDocument], awaitRefetchQueries: true })
  const [cancel, cancelling] = useMutation(CancelAccountDeletionDocument, { refetchQueries: [ViewerDocument], awaitRefetchQueries: true })
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState<string | null>(null)
  if (!viewer) return null
  const scheduled = viewer.deletionScheduledFor

  return (
    <section id="delete-account" aria-labelledby="delete-account-heading" className="flex scroll-mt-20 flex-col gap-4 rounded-2xl border border-red-500/40 bg-surface p-5">
      <h2 id="delete-account-heading" className="flex items-center gap-2 text-lg font-bold text-red-700 dark:text-red-400">
        <AlertTriangle className="size-5" aria-hidden />
        {t('heading')}
      </h2>
      <p className="text-sm text-muted">{t('lead')}</p>
      {scheduled ? (
        <div className="flex flex-wrap items-center gap-3">
          <p role="status" className="flex-1 text-sm font-semibold">
            {t('scheduled', { date: day(scheduled) })}
          </p>
          <Button disabled={cancelling.loading} onClick={() => void cancel()}>
            {t('cancel')}
          </Button>
        </div>
      ) : (
        <form
          className="flex flex-col gap-3"
          onSubmit={(e) => {
            e.preventDefault()
            setError(null)
            void request({ variables: { input: { password: password || null, confirm } } }).then(
              (res) => setError(res.data?.requestAccountDeletion.userErrors[0]?.message ?? null),
              () => setError(t('failed')),
            )
          }}
        >
          <label htmlFor={ids.password} className="flex flex-col gap-1 text-sm font-medium">
            {t('password')}
            <input id={ids.password} type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} className="h-10 rounded-lg border border-border bg-bg px-3" />
            <span className="text-xs font-normal text-muted">{t('passwordHint')}</span>
          </label>
          <label htmlFor={ids.confirm} className="flex flex-col gap-1 text-sm font-medium">
            {t('confirm')}
            <input id={ids.confirm} value={confirm} onChange={(e) => setConfirm(e.target.value)} autoComplete="off" className="h-10 rounded-lg border border-border bg-bg px-3" />
          </label>
          {error ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          ) : null}
          <button
            type="submit"
            disabled={requesting.loading || confirm.trim().toUpperCase() !== 'DELETE'}
            className="self-start rounded-xl bg-red-700 px-4 py-2 text-sm font-semibold text-white hover:bg-red-800 disabled:pointer-events-none disabled:opacity-50"
          >
            {t('request')}
          </button>
        </form>
      )}
    </section>
  )
}

/** On every signed-in page while a deletion is scheduled (ADR-0088). */
export function DeletionBanner() {
  const t = useTranslations('data.banner')
  const viewer = useQuery(ViewerDocument).data?.viewer
  const [cancel, cancelling] = useMutation(CancelAccountDeletionDocument, { refetchQueries: [ViewerDocument], awaitRefetchQueries: true })
  if (!viewer?.deletionScheduledFor) return null
  return (
    <div role="alert" className="flex flex-wrap items-center gap-3 border-b border-red-500/40 bg-red-50 px-4 py-2 text-sm text-red-900 dark:bg-red-950/40 dark:text-red-100">
      <span className="flex-1">{t('text', { date: day(viewer.deletionScheduledFor) })}</span>
      <button type="button" disabled={cancelling.loading} onClick={() => void cancel()} className="rounded-full bg-red-700 px-3 py-1 font-semibold text-white hover:bg-red-800 disabled:opacity-60">
        {t('keep')}
      </button>
    </div>
  )
}
