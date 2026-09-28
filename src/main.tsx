// Global styles first, so feature styles (imported by their components) come later in the cascade.
import '@/shared/styles/base.css'
import '@/shared/styles/layout.css'
import '@/shared/styles/components.css'
import '@/shared/styles/prose.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { App } from '@/app/App'
import { initTheme } from '@/shared/lib/theme'
import { initAuth } from '@/features/auth/auth'
import { initSync } from '@/features/progress/sync'
import { initAnalytics } from '@/services/analytics'
import { initTracking } from '@/features/telemetry/track'

initTheme()
initSync()
initTracking()
initAuth()
void initAnalytics()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
