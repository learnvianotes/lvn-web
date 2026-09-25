/* ============================================================
   ProblemStatement — Sheet 150
   Renders the problem description, input/output examples,
   and constraints. All data comes from Firebase.
   ============================================================ */

import type { Sheet150Problem } from '@/types/sheet150'

interface ProblemStatementProps {
  problem: Pick<Sheet150Problem, 'problemStatement' | 'inputOutput' | 'constraints'>
}

export function ProblemStatement({ problem }: ProblemStatementProps) {
  const { problemStatement, inputOutput, constraints } = problem

  return (
    <section className="s150-section" aria-labelledby="problem-statement-heading">
      <h2 className="s150-section__heading" id="problem-statement-heading">
        Problem Statement
      </h2>

      <p className="s150-problem-text">{problemStatement}</p>

      {/* Examples */}
      {inputOutput?.examples && inputOutput.examples.length > 0 && (
        <div className="s150-examples">
          {inputOutput.examples.map((ex, i) => (
            <div key={i} className="s150-example">
              <div className="s150-example__row">
                <span className="s150-example__label">Input</span>
                <code className="s150-example__code">{ex.in}</code>
              </div>
              <div className="s150-example__row">
                <span className="s150-example__label">Output</span>
                <code className="s150-example__code">{ex.out}</code>
              </div>
              {ex.comment && (
                <p className="s150-example__comment">{ex.comment}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Constraints */}
      {constraints && constraints.length > 0 && (
        <div className="s150-constraints">
          <p className="s150-constraints__label">Constraints</p>
          <ul className="s150-constraints__list">
            {constraints.map((c, i) => (
              <li key={i} className="s150-constraints__item">
                <code>{c}</code>
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
