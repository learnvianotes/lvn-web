'use client'

import { X } from 'lucide-react'
import { useEffect, useId, useRef, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

/**
 * A modal dialog on the native <dialog> element: focus is trapped and Escape closes it, as the platform does; the
 * title labels it for screen readers (§12.2: focus management in dialogs).
 */
/** `persistent`: Escape, clicks outside and the close button are off — for decisions that must be made. */
export function Dialog({ open, onClose, title, children, wide, side, sheet, persistent }: { open: boolean; onClose: () => void; title: string; children: ReactNode; wide?: boolean; side?: boolean; sheet?: boolean; persistent?: boolean }) {
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
      onCancel={(e) => persistent && e.preventDefault()}
      onClick={(e) => !persistent && e.target === ref.current && onClose()}
      className={cn(
        'm-auto max-h-[90dvh] w-[calc(100%-2rem)] max-w-full rounded-2xl border border-border bg-bg p-0 text-fg shadow-2xl backdrop:bg-black/40',
        wide ? 'max-w-3xl' : 'max-w-md',
        side && 'my-0 ml-auto mr-0 h-dvh max-h-dvh rounded-none sm:w-[28rem]',
        sheet && 'max-sm:m-0 max-sm:h-dvh max-sm:max-h-dvh max-sm:w-full max-sm:max-w-none max-sm:rounded-none',
      )}
    >
      {open ? (
        <div className={cn('flex max-h-[inherit] min-h-0 flex-col', sheet && 'max-sm:h-dvh max-sm:max-h-dvh')}>
          <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-2 sm:px-5 sm:py-3">
            <h2 id={titleId} className="min-w-0 text-lg font-bold tracking-tight break-words">
              {title}
            </h2>
            {persistent ? null : (
              <button type="button" onClick={onClose} className="grid size-11 shrink-0 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg" aria-label="Close">
                <X className="size-4" aria-hidden />
              </button>
            )}
          </header>
          <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4 sm:px-5">{children}</div>
        </div>
      ) : null}
    </dialog>
  )
}
