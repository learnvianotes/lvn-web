/* ============================================================
   SubjectsPage — full subject listing
   ============================================================ */

import { PageContainer } from '@/components/layout/PageContainer'
import { SubjectsDashboard } from '@/components/subjects/SubjectsDashboard'

export function SubjectsPage() {
  return (
    <PageContainer>
      <h1 className="sr-only">C-Note — All Subjects &amp; Roadmaps</h1>
      <SubjectsDashboard />
    </PageContainer>
  )
}
