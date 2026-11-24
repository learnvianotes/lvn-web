'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation } from '@apollo/client/react'
import type { LucideIcon } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { ModerateContentDocument, type ModerationActionType, type ReportEntityType } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

export type ModerationChoice = {
  action: ModerationActionType
  /** Key under moderation.queue.actions */
  label: string
  icon: LucideIcon
  tone: string
}

const NEEDS_REASON = new Set<ModerationActionType>(['HIDE', 'REMOVE', 'WARN', 'SUSPEND'])
/** How long a suspension lasts, in days (ADR-0053: 1 to 365). */
const SUSPEND_DAYS = [1, 3, 7, 14, 30, 90, 365] as const

/**
 * The decision controls from the moderation queue. Hide, remove, warn and suspend tell the author, so they need a
 * reason. `children` is an extra control in the same row (a group queue mutes the author here).
 */
export function ModerationActions({ entityType, entityId, actions, onDone, children }: { entityType: ReportEntityType; entityId: string; actions: ModerationChoice[]; onDone: () => void; children?: ReactNode }) {
  const t = useTranslations('moderation.queue')
  const [moderate, deciding] = useMutation(ModerateContentDocument)
  const [reason, setReason] = useState('')
  const [days, setDays] = useState<number>(7)
  const [error, setError] = useState<string | null>(null)

  const decide = async (action: ModerationActionType) => {
    setError(null)
    if (NEEDS_REASON.has(action) && !reason.trim()) return setError(t('reasonNeeded'))
    try {
      const res = await moderate({ variables: { input: { entityType, entityId, action, reason: reason.trim() || null, ...(action === 'SUSPEND' ? { suspendDays: days } : {}) } } })
      const problem = res.data?.moderateContent.userErrors[0]?.message
      if (problem) setError(problem)
      else onDone()
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label className="flex flex-col gap-1">
        <span className="text-xs font-semibold text-muted">{t('reason')}</span>
        <input className="h-11 w-full min-w-0 rounded-xl border border-border bg-bg px-3 text-sm focus-visible:border-accent focus-visible:outline-none" value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonPlaceholder')} />
      </label>
      {actions.some((a) => a.action === 'SUSPEND') ? (
        <label className="flex items-center gap-2 text-xs font-semibold text-muted">
          {t('suspendFor')}
          <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="h-9 rounded-lg border border-border bg-bg px-2 text-sm font-normal text-fg">
            {SUSPEND_DAYS.map((d) => (
              <option key={d} value={d}>
                {t('days', { count: d })}
              </option>
            ))}
          </select>
        </label>
      ) : null}
      <div className="flex flex-wrap gap-2">
        {actions.map(({ action, label, icon: Icon, tone }) => (
          <Button key={`${action}:${label}`} size="sm" variant={action === 'APPROVE' ? 'primary' : 'secondary'} className={cn('h-11 gap-1.5', tone)} disabled={deciding.loading} onClick={() => void decide(action)}>
            <Icon className="size-4" aria-hidden />
            {t(`actions.${label}`)}
          </Button>
        ))}
        {children}
      </div>
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </div>
  )
}
