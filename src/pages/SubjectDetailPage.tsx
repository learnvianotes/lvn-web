/* ============================================================
   SubjectDetailPage — single subject overview
   Phase 1: placeholder showing subject metadata + topic stubs
   ============================================================ */

import { useParams, Link } from 'react-router-dom'
import { PageContainer } from '@/components/layout/PageContainer'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import { Badge } from '@/components/ui/Badge'
import { EmptyState } from '@/components/ui/EmptyState'
import { NotFound } from '@/components/feedback/NotFound'
import { getSubjectById } from '@/data/subjects'
import { Layers } from 'lucide-react'

export function SubjectDetailPage() {
  const { subjectId } = useParams<{ subjectId: string }>()
  const subject = subjectId ? getSubjectById(subjectId) : undefined

  if (!subject) {
    return (
      <PageContainer>
        <NotFound message={`Subject "${subjectId}" was not found.`} />
      </PageContainer>
    )
  }

  return (
    <PageContainer>
      <Breadcrumbs
        items={[
          { label: 'Subjects', to: '/subjects' },
          { label: subject.title },
        ]}
      />

      <div className="page-header">
        <p className="page-header__label">Subject</p>
        <h1 className="page-header__title">{subject.title}</h1>
        <p className="page-header__description">{subject.description}</p>
      </div>

      {/* Topics list — placeholder */}
      <section aria-labelledby="topics-heading">
        <h2 id="topics-heading" className="section-title">Topics</h2>

        {subject.topicIds.length > 0 ? (
          <div className="topic-list" role="list">
            {subject.topicIds.map((topicId, index) => (
              <div key={topicId} className="topic-row" role="listitem">
                <span className="topic-row__number" aria-hidden="true">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <Link
                  to={`/subjects/${subject.id}/topics/${topicId}`}
                  className="topic-row__title"
                >
                  {topicId
                    .split('-')
                    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                    .join(' ')}
                </Link>
                <Badge variant="default">Coming soon</Badge>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Layers size={28} />}
            title="No topics yet"
            description="Topics for this subject will be added in a future phase."
          />
        )}
      </section>
    </PageContainer>
  )
}
