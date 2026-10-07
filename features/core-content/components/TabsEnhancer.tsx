'use client'

import { usePathname } from 'next/navigation'
import { useEffect } from 'react'

const LANG_KEY = 'lvn:code-tab'

function select(tab: HTMLElement, focus = false) {
  const tabs = tab.closest('[data-tabs]')
  if (!tabs) return
  for (const t of tabs.querySelectorAll<HTMLElement>(':scope > [role=tablist] > [role=tab]')) {
    const on = t === tab
    t.setAttribute('aria-selected', String(on))
    t.tabIndex = on ? 0 : -1
    const panel = document.getElementById(t.getAttribute('aria-controls') ?? '')
    if (panel) panel.hidden = !on
  }
  if (focus) tab.focus()
}

/** Show the reader's last-picked language in every tab set that has it. */
function applyLabel(label: string) {
  for (const tab of document.querySelectorAll<HTMLElement>(`[data-tabs] [role=tab][data-label="${CSS.escape(label)}"]`)) select(tab)
}

/** Wires up the server-rendered tab sets inside .lvn-prose (see features/core-content/render.ts). */
export function TabsEnhancer() {
  const pathname = usePathname()

  // Each page brings new tab sets; open them on the saved language.
  useEffect(() => {
    try {
      const saved = localStorage.getItem(LANG_KEY)
      if (saved) applyLabel(saved)
    } catch { /* storage unavailable */ }
  }, [pathname])

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const tab = (e.target as HTMLElement).closest<HTMLElement>('[data-tabs] [role=tab]')
      if (!tab) return
      const label = tab.dataset.label ?? ''
      const top = tab.getBoundingClientRect().top
      applyLabel(label)
      select(tab)
      // Switching every tab set can change heights above; keep the clicked tab still.
      window.scrollBy(0, tab.getBoundingClientRect().top - top)
      try { localStorage.setItem(LANG_KEY, label) } catch { /* storage unavailable */ }
    }
    const onKey = (e: KeyboardEvent) => {
      const tab = (e.target as HTMLElement).closest<HTMLElement>('[data-tabs] [role=tab]')
      if (!tab || !['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) return
      const all = [...(tab.parentElement?.querySelectorAll<HTMLElement>('[role=tab]') ?? [])]
      const i = all.indexOf(tab)
      const next = e.key === 'Home' ? all[0] : e.key === 'End' ? all.at(-1) : all[(i + (e.key === 'ArrowRight' ? 1 : -1) + all.length) % all.length]
      if (next) { e.preventDefault(); select(next, true) }
    }
    document.addEventListener('click', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('click', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [])
  return null
}
