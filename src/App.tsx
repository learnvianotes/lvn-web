import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { CatalogProvider } from '@/content/hooks'
import { AppShell } from '@/components/layout/AppShell'
import { LayoutProvider } from '@/components/layout/LayoutState'
import { NotFound } from '@/components/Status'
import { HomePage } from '@/pages/HomePage'
import { SubjectPage } from '@/pages/SubjectPage'
import { TopicPage } from '@/pages/TopicPage'
import { AboutPage } from '@/pages/AboutPage'

function Layout() {
  return (
    <LayoutProvider>
      <AppShell />
    </LayoutProvider>
  )
}

const router = createBrowserRouter([
  {
    element: <Layout />,
    errorElement: <NotFound />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/about', element: <AboutPage /> },
      { path: '/:subjectId', element: <SubjectPage /> },
      { path: '/:subjectId/:topicId', element: <TopicPage /> },
      { path: '*', element: <NotFound /> },
    ],
  },
])

export function App() {
  return (
    <CatalogProvider>
      <RouterProvider router={router} />
    </CatalogProvider>
  )
}
