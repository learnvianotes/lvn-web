/* ============================================================
   HomePage — C-NOTE landing / dashboard
   ============================================================ */

import { PageContainer } from '@/components/layout/PageContainer'
import { SubjectsDashboard } from '@/components/subjects/SubjectsDashboard'

export function HomePage() {
  return (
    <PageContainer>
      <h1 className="sr-only">C-Note — Computer Science &amp; System Design Reference</h1>
      <SubjectsDashboard />
    </PageContainer>
  )
}

