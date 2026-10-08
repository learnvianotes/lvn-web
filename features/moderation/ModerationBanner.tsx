'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation } from '@apollo/client/react'
import { Clock, ShieldAlert } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { AppealModerationDocument, type ModerationState } from '@/graphql/generated/graphql'

/**
 * What the owner of a note is told about moderation (ADR-0037): held for review, or hidden or removed with the
 * moderators' reason, and the one appeal.
 */
export function ModerationBanner({ noteId, moderation }: { noteId: string; moderation: { state: ModerationState; reason?: string | null; canAppeal: boolean } }) {
  const t = useTranslations('moderation.banner')
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [appealed, setAppealed] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [appeal, appealing] = useMutation(AppealModerationDocument)
  if (moderation.state === 'OK') return null
  const held = moderation.state === 'PENDING_REVIEW'

  const submit = async () => {
    setError(null)
    try {
      const res = await appeal({ variables: { input: { entityType: 'NOTE', entityId: noteId, message } } })
      const problem = res.data?.appealModeration.userErrors[0]?.message
      if (problem) setError(problem)
      else {
        setAppealed(true)
        setOpen(false)
      }
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  return (
    <div role="status" className={held ? 'flex items-start gap-3 rounded-2xl border border-amber-500/40 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100' : 'flex items-start gap-3 rounded-2xl border border-red-500/40 bg-red-50 px-4 py-3 text-sm text-red-950 dark:bg-red-950/30 dark:text-red-100'}>
      {held ? <Clock className="mt-0.5 size-5 shrink-0" aria-hidden /> : <ShieldAlert className="mt-0.5 size-5 shrink-0" aria-hidden />}
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <p className="font-semibold">{t(`title.${moderation.state}`)}</p>
        {moderation.reason ? <p>{moderation.reason}</p> : null}
        {held ? <p className="opacity-80">{t('heldLead')}</p> : null}
        {appealed ? <p className="font-medium">{t('appealed')}</p> : null}
      </div>
      {moderation.canAppeal && !appealed ? (
        <Button size="sm" variant="secondary" onClick={() => setOpen(true)}>
          {t('appeal')}
        </Button>
      ) : null}
      <Dialog open={open} onClose={() => setOpen(false)} title={t('appealTitle')}>
        <form
          className="flex flex-col gap-3"
          onSubmit={(e) => {
            e.preventDefault()
            void submit()
          }}
        >
          <p className="text-sm text-muted">{t('appealLead')}</p>
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium">{t('appealMessage')}</span>
            <textarea required className="min-h-28 rounded-xl border border-border bg-surface px-3 py-2 text-sm focus-visible:border-accent focus-visible:outline-none" maxLength={2000} value={message} onChange={(e) => setMessage(e.target.value)} />
          </label>
          {error ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          ) : null}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="ghost" onClick={() => setOpen(false)}>
              {t('cancel')}
            </Button>
            <Button type="submit" disabled={!message.trim() || appealing.loading}>
              {t('sendAppeal')}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  )
}
