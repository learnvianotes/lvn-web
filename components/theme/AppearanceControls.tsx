'use client'

import { useId, useEffect, useState } from 'react'
import { useTranslations } from 'next-intl'
import { ACCENTS, ACCENT_SWATCH, MODES, type AccentId, type ThemeMode } from '@/lib/theme'
import { cn } from '@/lib/cn'
import { useAppearance } from '@/state/theme'

/**
 * Mode and accent radios. The selected values wait until mount so the server HTML
 * matches the first client render; the page colors are already correct from the head script.
 */
export function AppearanceControls() {
  const t = useTranslations('site.theme')
  const id = useId()
  const mode = useAppearance((s) => s.mode)
  const accent = useAppearance((s) => s.accent)
  const setMode = useAppearance((s) => s.setMode)
  const setAccent = useAppearance((s) => s.setAccent)
  const [mounted, setMounted] = useState(false)
  useEffect(() => setMounted(true), [])
  const shownMode: ThemeMode = mounted ? mode : 'system'
  const shownAccent: AccentId = mounted ? accent : 'ink'

  return (
    <div className="flex flex-col gap-4">
      <div>
        <p id={`${id}-mode`} className="text-sm font-medium text-fg">{t('mode')}</p>
        <div role="radiogroup" aria-labelledby={`${id}-mode`} className="mt-2 grid grid-cols-3 gap-1 rounded-xl bg-surface-2 p-1">
          {MODES.map((item) => {
            const selected = shownMode === item
            return (
              <button
                key={item}
                type="button"
                role="radio"
                aria-checked={selected}
                onClick={() => setMode(item)}
                className={cn(
                  'min-h-10 rounded-lg px-2 text-sm font-medium',
                  selected ? 'bg-accent-soft text-accent' : 'text-muted hover:text-fg',
                )}
              >
                {t(item)}
              </button>
            )
          })}
        </div>
      </div>
      <div>
        <p id={`${id}-accent`} className="text-sm font-medium text-fg">{t('accent')}</p>
        <div role="radiogroup" aria-labelledby={`${id}-accent`} className="mt-2 grid grid-cols-6 gap-1">
          {ACCENTS.map((item) => {
            const selected = shownAccent === item
            return (
              <button
                key={item}
                type="button"
                role="radio"
                aria-checked={selected}
                onClick={() => setAccent(item)}
                className={cn(
                  'flex min-h-10 flex-col items-center justify-center gap-1 rounded-lg px-1 py-1.5 text-[11px] font-medium leading-none',
                  selected ? 'bg-accent-soft text-accent ring-2 ring-accent' : 'text-muted hover:bg-surface-2 hover:text-fg',
                )}
              >
                <span aria-hidden className="size-4 rounded-full border border-black/10" style={{ background: ACCENT_SWATCH[item] }} />
                {t(item)}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
