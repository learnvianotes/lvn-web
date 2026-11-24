'use client'

import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { cn } from '@/lib/cn'
import { firstLine, STUDY_LINES, type WaitKind } from '@/lib/study-lines'

const LINE_MS = 5_000

/**
 * What shows while something takes a moment (ADR-0114): what is happening, a highlighter bar (the real share when it is
 * known, a calm sweep when it is not), and one short study line that changes every few seconds. The status is
 * announced once; the rotating line is decoration for the eyes and not read out. No motion when reduced motion is on.
 */
export function StudyLoader({
  kind = 'general',
  label,
  progress,
  detail,
  className,
  compact = false,
}: {
  kind?: WaitKind
  label?: string
  /** 0 to 1 when the share done is known. */
  progress?: number | null
  /** A second plain line, e.g. "2 of 5 files". */
  detail?: string | null
  className?: string
  compact?: boolean
}) {
  const t = useTranslations('wait')
  const [line, setLine] = useState(() => firstLine(kind))
  const [shown, setShown] = useState(true)
  useEffect(() => {
    const timer = setInterval(() => {
      setShown(false)
      setTimeout(() => {
        setLine((n) => (n + 1) % STUDY_LINES.length)
        setShown(true)
      }, 200)
    }, LINE_MS)
    return () => clearInterval(timer)
  }, [])
  const share = progress == null ? null : Math.max(0, Math.min(1, progress))

  return (
    <div role="status" aria-live="polite" className={cn('flex w-full max-w-md flex-col gap-3', compact ? 'items-start' : 'items-center text-center', className)}>
      <p className="text-base font-medium">{label ?? t(kind)}</p>
      {detail ? <p className="-mt-2 text-sm text-muted tabular-nums">{detail}</p> : null}
      <div className="h-1 w-full max-w-60 overflow-hidden rounded-full bg-surface-2" aria-hidden>
        {share == null ? (
          <span className="lvn-sweep block h-full w-2/5 rounded-full bg-spark" />
        ) : (
          <span className="block h-full rounded-full bg-spark transition-[width] duration-300 ease-out" style={{ width: `${Math.round(share * 100)}%` }} />
        )}
      </div>
      {compact ? null : (
        <p aria-hidden className={cn('min-h-10 max-w-sm text-sm text-pretty text-muted transition-opacity duration-200', shown ? 'opacity-100' : 'opacity-0')}>
          {STUDY_LINES[line]}
        </p>
      )}
    </div>
  )
}
