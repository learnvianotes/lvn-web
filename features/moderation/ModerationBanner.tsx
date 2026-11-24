'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation } from '@apollo/client/react'
import { Clock, MessageSquareWarning, ShieldAlert } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { AppealModerationDocument, type ModerationState, type ReportEntityType } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

/**
 * What the author is told about moderation (ADR-0037, ADR-0051): held for review, hidden or removed with the
 * moderators' reason, or a warning on content that stays; and the one appeal. Only the author is ever sent a reason.
 * `compact` is for a comment, post, announcement or doubt inside a list.
 */
export function ModerationBanner({ entityType, entityId, moderation, compact, onAppealed }: { entityType: ReportEntityType; entityId: string; moderation: { state: ModerationState; reason?: string | null; canAppeal: boolean }; compact?: boolean; onAppealed?: () => void }) {
  const t = useTranslations('moderation.banner')
  const [open, setOpen] = useState(false)
  const [message, setMessage] = useState('')
  const [appealed, setAppealed] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [appeal, appealing] = useMutation(AppealModerationDocument)
  const warned = moderation.state === 'OK'
  if (warned && !moderation.reason) return null
  const held = moderation.state === 'PENDING_REVIEW'
  const note = entityType === 'NOTE'

  const submit = async () => {
    setError(null)
    try {
      const res = await appeal({ variables: { input: { entityType, entityId, message } } })
      const problem = res.data?.appealModeration.userErrors[0]?.message
      if (problem) setError(problem)
      else {
        setAppealed(true)
        setOpen(false)
        onAppealed?.()
      }
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  const tone = held || warned ? 'border-warn/40 bg-warn/10 text-warn' : 'border-bad/40 bg-bad/10 text-bad'
  const Icon = held ? Clock : warned ? MessageSquareWarning : ShieldAlert
  const lead = held ? (note ? t('heldLead') : t('heldLeadContent')) : warned ? t('warnedLead') : note ? null : t('hiddenLeadContent')
  return (
    <div role="status" className={cn('flex items-start gap-3 border', compact ? 'rounded-xl px-3 py-2 text-xs' : 'rounded-2xl px-4 py-3 text-sm', tone)}>
      <Icon className={cn('mt-0.5 shrink-0', compact ? 'size-4' : 'size-5')} aria-hidden />
      <div className="flex min-w-0 flex-1 flex-col gap-1">
        <p className="font-semibold">{t(`title.${warned ? 'WARNED' : moderation.state}`)}</p>
        {moderation.reason ? <p>{moderation.reason}</p> : null}
        {lead ? <p className="opacity-80">{lead}</p> : null}
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
          <p className="text-sm text-muted">{note ? t('appealLead') : t('appealLeadContent')}</p>
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium">{t('appealMessage')}</span>
            <textarea required className="min-h-28 rounded-xl border border-border bg-surface px-3 py-2 text-sm focus-visible:border-accent focus-visible:outline-none" maxLength={2000} value={message} onChange={(e) => setMessage(e.target.value)} />
          </label>
          {error ? (
            <p role="alert" className="text-sm text-bad">
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

/** The banner for a comment, post, announcement or doubt, from its moderation fields; nothing when there is nothing to tell. */
export function ContentModeration({ entityType, item, onAppealed }: { entityType: ReportEntityType; item: { id: string; moderation: ModerationState; moderationReason?: string | null; moderationCanAppeal: boolean }; onAppealed?: () => void }) {
  if (item.moderation === 'OK' && !item.moderationReason) return null
  return <ModerationBanner compact entityType={entityType} entityId={item.id} moderation={{ state: item.moderation, reason: item.moderationReason, canAppeal: item.moderationCanAppeal }} onAppealed={onAppealed} />
}
