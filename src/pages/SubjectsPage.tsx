/* ============================================================
   SubjectsPage — full subject listing
   ============================================================ */

import { PageContainer } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen } from 'lucide-react'
import { SUBJECTS } from '@/data/subjects'

export function SubjectsPage() {
  return (
    <PageContainer>
      <div className="page-header">
        <p className="page-header__label">C-NOTE</p>
        <h1 className="page-header__title">All Subjects</h1>
        <p className="page-header__description">
          {SUBJECTS.length} subjects covering computer science fundamentals, systems, and applied topics.
        </p>
      </div>

      <div className="subjects-list" role="list">
        {SUBJECTS.map((subject) => (
          <article key={subject.id} className="subject-row" role="listitem">
            <div className="subject-row__icon" aria-hidden="true">
              <BookOpen size={15} />
            </div>

            <div className="subject-row__body">
              <Link to={`/subjects/${subject.id}`} className="subject-row__title">
                {subject.title}
              </Link>
              <p className="subject-row__description">{subject.description}</p>
            </div>

            <div className="subject-row__meta">
              {subject.itemCount != null && subject.itemCount > 0 ? (
                <Badge variant="default">{subject.itemCount} items</Badge>
              ) : (
                <Badge variant="default">Coming soon</Badge>
              )}
              <Link
                to={`/subjects/${subject.id}`}
                className="subject-row__arrow"
                aria-label={`Open ${subject.title}`}
                tabIndex={-1}
                aria-hidden="true"
              >
                <ArrowRight size={14} />
              </Link>
            </div>
          </article>
        ))}
      </div>
    </PageContainer>
  )
}
