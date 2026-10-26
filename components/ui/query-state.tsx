'use client'

import { RotateCcw } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { cn } from '@/lib/cn'
import { Alert } from './alert'
import { Button } from './button'

/**
 * What a screen shows before its data (P9e): loading, or failed with a way to ask again. Apollo keeps the data it had
 * when a later refetch fails, so these are for a query with no data yet (`loading && !data`, `error && !data`); an
 * empty state is only for data that arrived and holds nothing.
 */

/** Waiting for the first answer. */
export function Loading({ label, className }: { label?: string; className?: string }) {
  const t = useTranslations('states')
  const text = label ?? t('loading')
  return (
    <div role="status" aria-live="polite" className={cn('flex flex-col gap-3', className)}>
      <p className="text-sm text-muted">{text}</p>
      <div aria-hidden className="flex max-w-md flex-col gap-2">
        <span className="lvn-skeleton h-4 w-2/3" />
        <span className="lvn-skeleton h-4 w-full" />
        <span className="lvn-skeleton h-24 w-full" />
      </div>
    </div>
  )
}

/** The answer did not come (no connection, a server error): said so, and Try again asks again. */
export function LoadFailed({ onRetry, message, className }: { onRetry: () => unknown; message?: string; className?: string }) {
  const t = useTranslations('states')
  const [retrying, setRetrying] = useState(false)
  const retry = async () => {
    setRetrying(true)
    // A retry that fails again leaves the query's error, so this notice stays: nothing more to say here.
    await Promise.resolve()
      .then(onRetry)
      .catch(() => undefined)
    setRetrying(false)
  }
  return (
    <Alert tone="error" className={cn('flex flex-wrap items-center justify-between gap-x-4 gap-y-2', className)}>
      <span>{message ?? t('loadFailed')}</span>
      <Button type="button" variant="secondary" size="sm" className="gap-1.5" disabled={retrying} onClick={() => void retry()}>
        <RotateCcw className="size-4" aria-hidden />
        {t('retry')}
      </Button>
    </Alert>
  )
}

/** A query without its data: loading, failed with Try again, or nothing (skipped). */
export function QueryState({ loading, error, onRetry, className }: { loading: boolean; error?: unknown; onRetry: () => unknown; className?: string }) {
  if (loading) return <Loading className={className} />
  if (error) return <LoadFailed onRetry={onRetry} className={className} />
  return null
}
