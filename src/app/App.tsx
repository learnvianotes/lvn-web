/* ============================================================
   App — root component
   Wraps the application in providers.
   ============================================================ */

import { RouterProvider } from 'react-router-dom'
import { ThemeProvider } from './providers/ThemeProvider'
import { FirebaseProvider } from '@/contexts/FirebaseContext'
import { router } from './router'

export function App() {
  return (
    <FirebaseProvider>
      <ThemeProvider>
        <RouterProvider router={router} />
      </ThemeProvider>
    </FirebaseProvider>
  )
}
