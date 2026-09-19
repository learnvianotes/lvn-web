/* ============================================================
   NotFoundPage — 404 route handler
   ============================================================ */

import { PageContainer } from '@/components/layout/PageContainer'
import { NotFound } from '@/components/feedback/NotFound'

export function NotFoundPage() {
  return (
    <PageContainer>
      <NotFound />
    </PageContainer>
  )
}
