/* ============================================================
   InsightsPanel — progress wheel, streak calendar and the ad slot.
   Used on the landing page and (collapsible) in every workspace.
   ============================================================ */

import { useMemo } from 'react'
import { useCatalog } from '@/content/hooks'
import { useProgress } from '@/progress/store'
import { subjectProgress } from '@/progress/stats'
import { ProgressBreakdown, ProgressWheel } from './ProgressWheel'
import { StreakCalendar } from './StreakCalendar'
import { ADSENSE_CLIENT } from '@/config'

interface Props {
  selectedId?: string
  onSelectSubject: (subjectId: string) => void
}

export function InsightsPanel({ selectedId, onSelectSubject }: Props) {
  const { data: catalog } = useCatalog()
  const progress = useProgress()
  const items = useMemo(
    () => (catalog ? catalog.subjects.map((s) => subjectProgress(s, progress)) : []),
    [catalog, progress],
  )

  return (
    <div className="insights">
      <section className="panel">
        <h2 className="panel-title">Progress</h2>
        {items.length > 0 && (
          <>
            <ProgressWheel items={items} selectedId={selectedId} onSelect={onSelectSubject} />
            <details className="breakdown-toggle">
              <summary>By subject</summary>
              <ProgressBreakdown items={items} selectedId={selectedId} onSelect={onSelectSubject} />
            </details>
          </>
        )}
      </section>
      <section className="panel">
        <h2 className="panel-title">Study streak</h2>
        <StreakCalendar progress={progress} />
      </section>
      <AdSlot />
    </div>
  )
}

/**
 * Reserved space for a single ad unit. Renders nothing until an ad
 * client is configured (ADSENSE_CLIENT in src/config.ts), so no
 * third-party script loads by default.
 */
function AdSlot() {
  if (!ADSENSE_CLIENT) return null
  return <aside className="panel ad-slot" aria-label="Advertisement" data-ad-client={ADSENSE_CLIENT} />
}
