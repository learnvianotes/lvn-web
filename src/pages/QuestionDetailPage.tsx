/* ============================================================
   QuestionDetailPage — individual question view
   Phase 1: placeholder only — no real question content
   ============================================================ */

import { useParams } from 'react-router-dom'
import { PageContainer } from '@/components/layout/PageContainer'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import { EmptyState } from '@/components/ui/EmptyState'
import { getSubjectById } from '@/data/subjects'
import { NotFound } from '@/components/feedback/NotFound'
import { Code2 } from 'lucide-react'

function formatSlug(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export function QuestionDetailPage() {
  const { subjectId, topicId, questionId } = useParams<{
    subjectId: string
    topicId: string
    questionId: string
  }>()

  const subject = subjectId ? getSubjectById(subjectId) : undefined

  if (!subject || !topicId || !questionId) {
    return (
      <PageContainer>
        <NotFound message="Question not found." />
      </PageContainer>
    )
  }

  return (
    <PageContainer narrow>
      <Breadcrumbs
        items={[
          { label: 'Subjects', to: '/subjects' },
          { label: subject.title, to: `/subjects/${subject.id}` },
          {
            label: formatSlug(topicId),
            to: `/subjects/${subject.id}/topics/${topicId}`,
          },
          { label: formatSlug(questionId) },
        ]}
      />

      <div className="page-header">
        <p className="page-header__label">Question</p>
        <h1 className="page-header__title">{formatSlug(questionId)}</h1>
      </div>

      <EmptyState
        icon={<Code2 size={28} />}
        title="Content coming soon"
        description="Question content will be populated in Phase 2. This page establishes the route and layout structure."
      />
    </PageContainer>
  )
}
