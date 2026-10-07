'use client'

/* ============================================================
   Entry of the /core pages inside lvn-web (replaces main.tsx).
   The old site was a single-page app with its own router; it
   runs in the browser only, exactly as before.
   ============================================================ */

import dynamic from 'next/dynamic'
import { StrictMode, useEffect } from 'react'
import { initTheme } from '@core/shared/lib/theme'

const App = dynamic(() => import('./App').then((m) => m.App), { ssr: false })

export function CoreApp() {
  useEffect(() => initTheme(), [])
  return (
    <StrictMode>
      <App />
    </StrictMode>
  )
}
