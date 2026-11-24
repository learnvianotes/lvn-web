'use client'

import { usePathname } from 'next/navigation'
import { useEffect } from 'react'
import { startUsageTracking, trackFeature, trackUsage } from '@/lib/analytics'
import { featureOfPath } from '@/lib/analytics/usage-events'

/**
 * Sends a page view on each route change and starts the batched, opt-out-aware tracker. A page that is a product area
 * by itself (groups, a class, exams, …) also records that feature, once per page session (lvn-backend ADR-0107).
 */
export function UsageTracker() {
  const path = usePathname()
  useEffect(() => startUsageTracking(), [])
  useEffect(() => {
    trackUsage('page_view')
    const feature = featureOfPath(path ?? '/')
    if (feature) trackFeature(feature)
  }, [path])
  return null
}
