/* ============================================================
   SimilarQuestions — Sheet 150
   Renders the "See Also" block of related problems.
   Links navigate to /sheet-150/problems/:slug when a slug
   is available; otherwise shows a plain LeetCode reference.
   ============================================================ */

import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import type { SimilarQuestion } from '@/types/sheet150'

interface SimilarQuestionsProps {
  questions: SimilarQuestion[]
}

const DIFFICULTY_CLASS: Record<string, string> = {
  easy:   's150-similar__diff--easy',
  medium: 's150-similar__diff--medium',
  hard:   's150-similar__diff--hard',
}

export function SimilarQuestions({ questions }: SimilarQuestionsProps) {
  if (!questions || questions.length === 0) return null

  return (
    <section className="s150-section s150-similar" aria-labelledby="similar-heading">
      <h2 className="s150-section__heading" id="similar-heading">
        Similar Questions
      </h2>

      <ul className="s150-similar__list">
        {questions.map((q) => {
          const diffClass = DIFFICULTY_CLASS[q.difficulty?.toLowerCase()] ?? ''

          return (
            <li key={q.lc} className="s150-similar__item">
              {q.slug ? (
                <Link
                  to={`/sheet-150/problems/${q.slug}`}
                  className="s150-similar__link"
                >
                  <span className="s150-similar__lc">#{q.lc}</span>
                  <span className="s150-similar__title">{q.title}</span>
                  <span className={`s150-similar__diff ${diffClass}`}>
                    {q.difficulty}
                  </span>
                  <ArrowRight size={13} aria-hidden="true" className="s150-similar__arrow" />
                </Link>
              ) : (
                <a
                  href={`https://leetcode.com/problems/${q.title.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="s150-similar__link s150-similar__link--external"
                >
                  <span className="s150-similar__lc">#{q.lc}</span>
                  <span className="s150-similar__title">{q.title}</span>
                  <span className={`s150-similar__diff ${diffClass}`}>
                    {q.difficulty}
                  </span>
                  <ArrowRight size={13} aria-hidden="true" className="s150-similar__arrow" />
                </a>
              )}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
