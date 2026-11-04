'use client'

import { useEffect } from 'react'
import { trackFeature } from './usage'
import type { UsageFeature } from './usage-events'

/** Records that a product area was opened, when its screen mounts (once per page session; null records nothing). */
export function useFeatureUse(feature: UsageFeature | null | undefined): void {
  useEffect(() => {
    if (feature) trackFeature(feature)
  }, [feature])
}
