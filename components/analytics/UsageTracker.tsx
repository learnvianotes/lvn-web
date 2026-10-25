'use client'

import { usePathname } from 'next/navigation'
import { useEffect } from 'react'
import { startUsageTracking, trackUsage } from '@/lib/analytics'

/** Sends a page view on each route change and starts the batched, opt-out-aware tracker. */
export function UsageTracker() {
  const path = usePathname()
  useEffect(() => startUsageTracking(), [])
  useEffect(() => {
    trackUsage('page_view')
  }, [path])
  return null
}
