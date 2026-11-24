'use client'

import { useEffect } from 'react'
import { useAppearance } from '@/state/theme'

/** Keep the document and the picker aligned with storage and the OS scheme after hydration. */
export function ThemeSync() {
  const sync = useAppearance((s) => s.sync)
  useEffect(() => {
    sync()
    const query = window.matchMedia('(prefers-color-scheme: dark)')
    const onChange = () => sync()
    query.addEventListener('change', onChange)
    window.addEventListener('storage', onChange)
    return () => {
      query.removeEventListener('change', onChange)
      window.removeEventListener('storage', onChange)
    }
  }, [sync])
  return null
}
