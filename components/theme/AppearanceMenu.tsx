'use client'

import { Monitor, Moon, Sun } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'
import { useTranslations } from 'next-intl'
import { useAppearance } from '@/state/theme'
import { AppearanceControls } from './AppearanceControls'

/** Header control. Icon shows the mode; the panel holds mode and accent. Not named Menu. */
export function AppearanceMenu() {
  const t = useTranslations('site.theme')
  const mode = useAppearance((s) => s.mode)
  const panelId = useId()
  const [open, setOpen] = useState(false)
  const [mounted, setMounted] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  useEffect(() => setMounted(true), [])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key !== 'Escape') return
      setOpen(false)
      buttonRef.current?.focus()
    }
    const onPointer = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false)
    }
    document.addEventListener('keydown', onKey)
    document.addEventListener('pointerdown', onPointer)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.removeEventListener('pointerdown', onPointer)
    }
  }, [open])

  const shown = mounted ? mode : 'system'
  const Icon = shown === 'light' ? Sun : shown === 'dark' ? Moon : Monitor

  return (
    <div className="relative" ref={rootRef}>
      <button
        ref={buttonRef}
        type="button"
        aria-label={t('appearance')}
        aria-expanded={open}
        aria-haspopup="dialog"
        aria-controls={open ? panelId : undefined}
        onClick={() => setOpen((value) => !value)}
        className="inline-flex size-10 items-center justify-center rounded-xl text-muted hover:bg-surface-2 hover:text-fg"
      >
        <Icon className="size-[18px]" aria-hidden />
      </button>
      {open ? (
        <div
          id={panelId}
          role="dialog"
          aria-label={t('appearance')}
          className="absolute right-0 z-40 mt-2 w-72 rounded-2xl border border-border bg-surface p-4 shadow-md"
        >
          <AppearanceControls />
        </div>
      ) : null}
    </div>
  )
}
