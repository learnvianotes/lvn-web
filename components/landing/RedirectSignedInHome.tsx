'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useLayoutEffect } from 'react'
import { APP_HOME } from '@/lib/auth/destination'
import { holdLandingPaint, releaseLandingPaint, shouldHoldLanding, SIGNED_IN_HINT_KEY } from '@/lib/auth/hint'
import { useSession } from '@/state/session'

/** A stale hint must not leave the landing blank if the session never comes back. */
const REVEAL_AFTER_MS = 8_000

/**
 * Signed-in people do not stay on the landing page. When this browser has signed in before, the head script has
 * already hidden it; this opens Home once the session is known. A visitor, or a hint left behind after sign-out,
 * sees the page.
 */
export function RedirectSignedInHome() {
  const status = useSession((s) => s.status)
  const router = useRouter()

  useLayoutEffect(() => {
    if (status === 'signed-in') {
      // Hide before the browser paints, including a client navigation where the head script does not run again.
      holdLandingPaint()
      router.replace(APP_HOME)
      return
    }
    if (status === 'signed-out') releaseLandingPaint()
  }, [status, router])

  useEffect(() => {
    let hint: string | null = null
    try {
      hint = localStorage.getItem(SIGNED_IN_HINT_KEY)
    } catch {
      hint = null
    }
    if (!shouldHoldLanding(window.location.pathname, hint)) return
    const timer = window.setTimeout(() => {
      if (useSession.getState().status !== 'signed-in') releaseLandingPaint()
    }, REVEAL_AFTER_MS)
    return () => window.clearTimeout(timer)
  }, [])

  return null
}
