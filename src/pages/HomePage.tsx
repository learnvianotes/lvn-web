/* ============================================================
   HomePage — C-NOTE landing / dashboard
   Phase 1: Overview of subjects with placeholder state
   ============================================================ */

import { Link } from 'react-router-dom'
import { ArrowRight, BookOpen } from 'lucide-react'
import { PageContainer } from '@/components/layout/PageContainer'
import { Badge } from '@/components/ui/Badge'
import { SUBJECTS } from '@/data/subjects'

export function HomePage() {
  return (
    <PageContainer>
      {/* Page header */}
      <div className="page-header">
        <p className="page-header__label">C-NOTE</p>
        <h1 className="page-header__title">Computer Science Reference</h1>
        <p className="page-header__description">
          A personal technical knowledge system for learning and interview preparation.
          Browse subjects below to begin.
        </p>
      </div>

      {/* Subjects section */}
      <section aria-labelledby="subjects-heading">
        <div className="home-section-header">
          <h2 id="subjects-heading" className="home-section-title">
            Subjects
            <span className="home-section-count">{SUBJECTS.length}</span>
          </h2>
        </div>

        <div className="subjects-list" role="list">
          {SUBJECTS.map((subject) => (
            <article
              key={subject.id}
              className="subject-row"
              role="listitem"
            >
              <div className="subject-row__icon" aria-hidden="true">
                <BookOpen size={15} />
              </div>

              <div className="subject-row__body">
                <Link
                  to={`/subjects/${subject.id}`}
                  className="subject-row__title"
                >
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
      </section>
    </PageContainer>
  )
}
