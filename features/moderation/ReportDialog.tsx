'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation } from '@apollo/client/react'
import { Check, Flag } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { ReportContentDocument, type ReportEntityType, type ReportReason } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

const REASONS: ReportReason[] = ['SPAM', 'HARASSMENT', 'HATE', 'SEXUAL', 'SELF_HARM', 'COPYRIGHT', 'OTHER']

/** "Report" (§15.1): a reason and a few words; moderators see it in their queue, the author never sees who sent it. */
export function ReportButton({ entityType, entityId, className }: { entityType: ReportEntityType; entityId: string; className?: string }) {
  const t = useTranslations('moderation.report')
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState<ReportReason | null>(null)
  const [details, setDetails] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [report, reporting] = useMutation(ReportContentDocument)

  const submit = async () => {
    if (!reason) return
    setError(null)
    try {
      const res = await report({ variables: { input: { entityType, entityId, reason, details: details.trim() || null } } })
      const problem = res.data?.reportContent.userErrors[0]?.message
      if (problem) setError(problem)
      else setSent(true)
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  const close = () => {
    setOpen(false)
    setSent(false)
    setReason(null)
    setDetails('')
    setError(null)
  }

  return (
    <>
      <Button variant="ghost" size="sm" className={cn('gap-1.5 text-muted', className)} onClick={() => setOpen(true)}>
        <Flag className="size-4" aria-hidden />
        {t('button')}
      </Button>
      <Dialog open={open} onClose={close} title={t('title')}>
        {sent ? (
          <div role="status" className="flex flex-col items-center gap-3 py-4 text-center">
            <span className="grid size-12 place-items-center rounded-full bg-emerald-500/15 text-emerald-600 dark:text-emerald-400">
              <Check className="size-6" aria-hidden />
            </span>
            <p className="font-semibold">{t('thanks')}</p>
            <p className="text-sm text-muted">{t('thanksLead')}</p>
            <Button onClick={close}>{t('done')}</Button>
          </div>
        ) : (
          <form
            className="flex flex-col gap-4"
            onSubmit={(e) => {
              e.preventDefault()
              void submit()
            }}
          >
            <fieldset className="flex flex-col gap-2">
              <legend className="pb-2 text-sm text-muted">{t('lead')}</legend>
              {REASONS.map((r) => (
                <label key={r} className={cn('flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition', reason === r ? 'border-accent bg-accent-soft' : 'border-border bg-surface hover:border-accent/40')}>
                  <input type="radio" name="reason" value={r} checked={reason === r} onChange={() => setReason(r)} className="mt-1 accent-[var(--accent)]" />
                  <span className="flex flex-col">
                    <span className="text-sm font-semibold">{t(`reasons.${r}`)}</span>
                    <span className="text-xs text-muted">{t(`hints.${r}`)}</span>
                  </span>
                </label>
              ))}
            </fieldset>
            <label className="flex flex-col gap-1">
              <span className="text-sm font-medium">{t('details')}</span>
              <textarea className="min-h-20 rounded-xl border border-border bg-surface px-3 py-2 text-sm focus-visible:border-accent focus-visible:outline-none" maxLength={1000} value={details} onChange={(e) => setDetails(e.target.value)} placeholder={t('detailsPlaceholder')} />
            </label>
            {reason === 'SELF_HARM' ? <p className="rounded-xl bg-amber-50 px-3 py-2 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">{t('selfHarmHelp')}</p> : null}
            {error ? (
              <p role="alert" className="text-sm text-red-600 dark:text-red-400">
                {error}
              </p>
            ) : null}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="ghost" onClick={close}>
                {t('cancel')}
              </Button>
              <Button type="submit" disabled={!reason || reporting.loading}>
                {t('send')}
              </Button>
            </div>
          </form>
        )}
      </Dialog>
    </>
  )
}
