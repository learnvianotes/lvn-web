/* ============================================================
   ComplexityBlock — Sheet 150
   Renders the Time and Space complexity pair as badges.
   Used inside ApproachSection for both naive and optimal.
   ============================================================ */

import { Clock, MemoryStick } from 'lucide-react'

interface ComplexityBlockProps {
  timeComplexity: string
  spaceComplexity: string
}

export function ComplexityBlock({ timeComplexity, spaceComplexity }: ComplexityBlockProps) {
  return (
    <div className="s150-complexity">
      <div className="s150-complexity__item">
        <Clock size={12} aria-hidden="true" className="s150-complexity__icon" />
        <span className="s150-complexity__label">Time</span>
        <code className="s150-complexity__value">{timeComplexity}</code>
      </div>
      <div className="s150-complexity__sep" aria-hidden="true" />
      <div className="s150-complexity__item">
        <MemoryStick size={12} aria-hidden="true" className="s150-complexity__icon" />
        <span className="s150-complexity__label">Space</span>
        <code className="s150-complexity__value">{spaceComplexity}</code>
      </div>
    </div>
  )
}
