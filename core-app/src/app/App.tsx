/* ============================================================
   APP — providers + routes. Every page except Home is its own
   chunk, loaded when first visited (and prefetched when the
   browser is idle), so the first load stays small as the app
   grows.
   ============================================================ */

import { lazy, Suspense, useEffect } from 'react'
import { createBrowserRouter, RouterProvider, useLocation } from 'react-router-dom'
import { CatalogProvider } from '@core/features/catalog/CatalogProvider'
import { HomePage } from '@core/features/home/HomePage'
import { NotFound } from '@core/shared/ui/Status'
import { RouteProgress } from '@core/shared/ui/RouteProgress'
import { useCatalog } from '@core/features/catalog/hooks'
import { hideSplash } from './splash'
import { pageInfo } from './title'
import { AppShell } from './shell/AppShell'
import { LayoutProvider } from './shell/LayoutState'

const pages = {
  topic: () => import('@core/features/study/TopicPage'),
  subject: () => import('@core/features/study/SubjectPage'),
  about: () => import('@core/features/about/AboutPage'),
}

const TopicPage = lazy(() => pages.topic().then((m) => ({ default: m.TopicPage })))
const SubjectPage = lazy(() => pages.subject().then((m) => ({ default: m.SubjectPage })))
const AboutPage = lazy(() => pages.about().then((m) => ({ default: m.AboutPage })))

/** Keeps the tab title in step with the page (the server sets it for the first paint). */
function useDocumentTitle() {
  const { pathname } = useLocation()
  const { data } = useCatalog()
  useEffect(() => { document.title = pageInfo(data, pathname.split('/').filter(Boolean)).title }, [data, pathname])
}

function Layout() {
  useDocumentTitle()
  // Warm the study pages once the landing page is idle.
  useEffect(() => {
    const idle = window.requestIdleCallback ?? ((cb: () => void) => window.setTimeout(cb, 1500))
    idle(() => { void pages.topic(); void pages.subject() })
  }, [])
  return (
    <LayoutProvider>
      <AppShell />
    </LayoutProvider>
  )
}

const page = (el: React.ReactNode) => <Suspense fallback={<RouteProgress />}>{el}</Suspense>

// Mounted at /core inside lvn-web (lvn-backend ADR-0002); every link and route is relative to it.
const router = createBrowserRouter([
  {
    element: <Layout />,
    errorElement: <NotFound />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/about', element: page(<AboutPage />) },
      { path: '/:subjectId', element: page(<SubjectPage />) },
      { path: '/:subjectId/:topicId', element: page(<TopicPage />) },
      { path: '*', element: <NotFound /> },
    ],
  },
], { basename: '/core' })

/** Every page needs the catalog: once it has loaded (or failed), the splash goes. */
function SplashGate() {
  const { status } = useCatalog()
  useEffect(() => { if (status !== 'loading') requestAnimationFrame(() => hideSplash()) }, [status])
  return null
}

export function App() {
  return (
    <CatalogProvider>
      <SplashGate />
      <RouterProvider router={router} />
    </CatalogProvider>
  )
}
