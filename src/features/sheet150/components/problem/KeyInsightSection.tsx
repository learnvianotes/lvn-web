/* ============================================================
   KeyInsightSection — Sheet 150
   Renders the "Key Insight / Understanding" block.
   Displayed between the problem statement and approaches.
   ============================================================ */

import { Lightbulb } from 'lucide-react'

interface KeyInsightSectionProps {
  insight: string
}

export function KeyInsightSection({ insight }: KeyInsightSectionProps) {
  return (
    <section className="s150-section s150-insight" aria-labelledby="key-insight-heading">
      <div className="s150-insight__header">
        <Lightbulb size={15} aria-hidden="true" className="s150-insight__icon" />
        <h2 className="s150-section__heading s150-section__heading--inline" id="key-insight-heading">
          Key Insight
        </h2>
      </div>
      <p className="s150-insight__text">{insight}</p>
    </section>
  )
}
