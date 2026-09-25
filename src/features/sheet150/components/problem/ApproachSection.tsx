/* ============================================================
   ApproachSection — Sheet 150
   Renders one solution approach (naive OR optimized).
   Composes: title → explanation → steps list → ComplexityBlock → CodeBlock
   All data comes from Firebase. No problem-specific logic here.
   ============================================================ */

import { ComplexityBlock } from './ComplexityBlock'
import { CodeBlock } from './CodeBlock'
import type { CodeSolution } from '@/types/sheet150'

interface ApproachSectionProps {
  /** "Brute Force" or "Optimized" — displayed as a label */
  variant: 'brute-force' | 'optimized'
  solution: CodeSolution
}

const VARIANT_LABELS = {
  'brute-force': 'Brute Force',
  optimized: 'Optimized Approach',
}

export function ApproachSection({ variant, solution }: ApproachSectionProps) {
  const headingId = `approach-heading-${variant}`

  return (
    <section
      className={`s150-section s150-approach s150-approach--${variant}`}
      aria-labelledby={headingId}
    >
      {/* Section label */}
      <p className="s150-approach__variant-label section-label">
        {VARIANT_LABELS[variant]}
      </p>

      {/* Solution title from Firebase, e.g. "Naive Solution — O(n²) Brute Force" */}
      <h2 className="s150-section__heading" id={headingId}>
        {solution.title}
      </h2>

      {/* Explanation text */}
      {solution.explanation && (
        <p className="s150-approach__explanation">{solution.explanation}</p>
      )}

      {/* Step-by-step approach list */}
      {solution.approach && solution.approach.length > 0 && (
        <ol className="s150-approach__steps">
          {solution.approach.map((step, i) => (
            <li key={i} className="s150-approach__step">
              {step}
            </li>
          ))}
        </ol>
      )}

      {/* Complexity */}
      <ComplexityBlock
        timeComplexity={solution.complexityTime}
        spaceComplexity={solution.complexitySpace}
      />

      {/* Code */}
      <CodeBlock code={solution.code} />
    </section>
  )
}
