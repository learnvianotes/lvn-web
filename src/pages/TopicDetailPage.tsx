/* ============================================================
   TopicDetailPage — single topic overview
   Phase 1: placeholder showing topic + question stubs
   ============================================================ */

import { useParams } from 'react-router-dom'
import { PageContainer } from '@/components/layout/PageContainer'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import { EmptyState } from '@/components/ui/EmptyState'
import { getSubjectById } from '@/data/subjects'
import { NotFound } from '@/components/feedback/NotFound'
import { FileText } from 'lucide-react'

function formatSlug(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export function TopicDetailPage() {
  const { subjectId, topicId } = useParams<{
    subjectId: string
    topicId: string
  }>()

  const subject = subjectId ? getSubjectById(subjectId) : undefined

  if (!subject || !topicId) {
    return (
      <PageContainer>
        <NotFound message="Topic not found." />
      </PageContainer>
    )
  }

  const topicLabel = formatSlug(topicId)

  return (
    <PageContainer>
      <Breadcrumbs
        items={[
          { label: 'Subjects', to: '/subjects' },
          { label: subject.title, to: `/subjects/${subject.id}` },
          { label: topicLabel },
        ]}
      />

      <div className="page-header">
        <p className="page-header__label">{subject.shortTitle ?? subject.title}</p>
        <h1 className="page-header__title">{topicLabel}</h1>
        <p className="page-header__description">
          Questions and content for this topic will be available in a future phase.
        </p>
      </div>

      <section aria-label="Questions">
        <EmptyState
          icon={<FileText size={28} />}
          title="No questions yet"
          description="This topic's questions will be added when content is populated in Phase 2+."
        />
      </section>
    </PageContainer>
  )
}
