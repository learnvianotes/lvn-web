'use client'

import { usePathname } from 'next/navigation'
import { useLayoutEffect } from 'react'
import { releaseLandingPaint } from '@/lib/auth/hint'

/** The hold is only for the landing page. Home, and every other address, shows as soon as it is ready. */
export function ReleaseLandingHold() {
  const path = usePathname()
  useLayoutEffect(() => {
    if (path !== '/') releaseLandingPaint()
  }, [path])
  return null
}
