/* ============================================================
   C-NOTE ROUTER
   React Router v7 — all routes defined here.
   Pages are simple placeholder components for Phase 1.
   ============================================================ */

import { createBrowserRouter, Outlet } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { ErrorBoundary } from '@/components/feedback/ErrorBoundary'
import { ErrorState } from '@/components/feedback/ErrorState'
import { PageContainer } from '@/components/layout/PageContainer'

import { HomePage } from '@/pages/HomePage'
import { SubjectsPage } from '@/pages/SubjectsPage'
import { SubjectDetailPage } from '@/pages/SubjectDetailPage'
import { TopicDetailPage } from '@/pages/TopicDetailPage'
import { QuestionDetailPage } from '@/pages/QuestionDetailPage'
import { DesignSystemPage } from '@/pages/DesignSystemPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { Sheet150Page } from '@/pages/Sheet150Page'
import { Sheet150CategoryPage } from '@/pages/Sheet150CategoryPage'
import { Sheet150ProblemPage } from '@/pages/Sheet150ProblemPage'

/** Root layout — wraps all routes in AppShell + ErrorBoundary */
function RootLayout() {
  return (
    <ErrorBoundary
      fallback={
        <AppShell>
          <PageContainer>
            <ErrorState
              title="Application error"
              description="An unexpected error occurred. Please refresh the page."
            />
          </PageContainer>
        </AppShell>
      }
    >
      <AppShell>
        <Outlet />
      </AppShell>
    </ErrorBoundary>
  )
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'subjects', element: <SubjectsPage /> },
      { path: 'subjects/:subjectId', element: <SubjectDetailPage /> },
      {
        path: 'subjects/:subjectId/topics/:topicId',
        element: <TopicDetailPage />,
      },
      {
        path: 'subjects/:subjectId/topics/:topicId/questions/:questionId',
        element: <QuestionDetailPage />,
      },
      { path: 'sheet-150', element: <Sheet150Page /> },
      { path: 'sheet-150/category/:categoryId', element: <Sheet150CategoryPage /> },
      { path: 'sheet-150/problems/:slug', element: <Sheet150ProblemPage /> },
      { path: 'design-system', element: <DesignSystemPage /> },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])
