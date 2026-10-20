/* ============================================================
   APP — providers + routes. Every page except Home is its own
   chunk, loaded when first visited (and prefetched when the
   browser is idle), so the first load stays small as the app
   grows.
   ============================================================ */

import { lazy, Suspense, useEffect } from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { CatalogProvider } from '@/features/catalog/CatalogProvider'
import { HomePage } from '@/features/home/HomePage'
import { NotFound } from '@/shared/ui/Status'
import { RouteProgress } from '@/shared/ui/RouteProgress'
import { useCatalog } from '@/features/catalog/hooks'
import { hideSplash } from './splash'
import { AppShell } from './shell/AppShell'
import { LayoutProvider } from './shell/LayoutState'

const pages = {
  topic: () => import('@/features/study/TopicPage'),
  subject: () => import('@/features/study/SubjectPage'),
  history: () => import('@/features/progress/HistoryPage'),
  auth: () => import('@/features/auth/AuthPage'),
  about: () => import('@/features/about/AboutPage'),
  settings: () => import('@/features/settings/SettingsPage'),
  legal: () => import('@/features/legal/LegalPage'),
}

const TopicPage = lazy(() => pages.topic().then((m) => ({ default: m.TopicPage })))
const SubjectPage = lazy(() => pages.subject().then((m) => ({ default: m.SubjectPage })))
const HistoryPage = lazy(() => pages.history().then((m) => ({ default: m.HistoryPage })))
const AuthPage = lazy(() => pages.auth().then((m) => ({ default: m.AuthPage })))
const AboutPage = lazy(() => pages.about().then((m) => ({ default: m.AboutPage })))
const SettingsPage = lazy(() => pages.settings().then((m) => ({ default: m.SettingsPage })))
const LegalPage = lazy(() => pages.legal().then((m) => ({ default: m.LegalPage })))

function Layout() {
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

const router = createBrowserRouter([
  {
    element: <Layout />,
    errorElement: <NotFound />,
    children: [
      { path: '/', element: <HomePage /> },
      { path: '/about', element: page(<AboutPage />) },
      { path: '/login', element: page(<AuthPage mode="login" />) },
      { path: '/signup', element: page(<AuthPage mode="signup" />) },
      { path: '/forgot-password', element: page(<AuthPage mode="reset" />) },
      { path: '/history', element: page(<HistoryPage />) },
      { path: '/settings', element: page(<SettingsPage />) },
      { path: '/privacy', element: page(<LegalPage doc="privacy" />) },
      { path: '/terms', element: page(<LegalPage doc="terms" />) },
      { path: '/grievance', element: page(<LegalPage doc="grievance" />) },
      { path: '/:subjectId', element: page(<SubjectPage />) },
      { path: '/:subjectId/:topicId', element: page(<TopicPage />) },
      { path: '*', element: <NotFound /> },
    ],
  },
])

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
