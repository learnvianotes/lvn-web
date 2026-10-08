'use client'

import { useEffect, useId, useRef, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

/**
 * A modal dialog on the native <dialog> element: focus is trapped and Escape closes it, as the platform does; the
 * title labels it for screen readers (§12.2: focus management in dialogs).
 */
export function Dialog({ open, onClose, title, children, wide, side }: { open: boolean; onClose: () => void; title: string; children: ReactNode; wide?: boolean; side?: boolean }) {
  const ref = useRef<HTMLDialogElement>(null)
  const titleId = useId()
  useEffect(() => {
    const d = ref.current
    if (!d) return
    if (open && !d.open) d.showModal()
    if (!open && d.open) d.close()
  }, [open])
  return (
    <dialog
      ref={ref}
      aria-labelledby={titleId}
      onClose={onClose}
      onClick={(e) => e.target === ref.current && onClose()}
      className={cn(
        'max-h-[90dvh] w-[calc(100%-2rem)] rounded-2xl border border-border bg-bg p-0 text-fg shadow-2xl backdrop:bg-black/40',
        wide ? 'max-w-3xl' : 'max-w-md',
        side && 'ml-auto mr-0 h-dvh max-h-dvh rounded-none sm:w-[28rem]',
      )}
    >
      {open ? (
        <div className="flex max-h-[inherit] flex-col">
          <header className="flex items-center justify-between gap-4 border-b border-border px-5 py-3">
            <h2 id={titleId} className="text-lg font-bold tracking-tight">
              {title}
            </h2>
            <button type="button" onClick={onClose} className="rounded-lg px-2 py-1 text-muted hover:bg-surface-2 hover:text-fg" aria-label="Close">
              ✕
            </button>
          </header>
          <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">{children}</div>
        </div>
      ) : null}
    </dialog>
  )
}
