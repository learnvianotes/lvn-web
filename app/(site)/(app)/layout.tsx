import { AuthProvider } from '@/components/auth/AuthProvider'
import { RequireSession } from '@/components/auth/RequireSession'
import { TermsGate } from '@/components/auth/TermsGate'
import { AppShell } from '@/components/shell/AppShell'
import { SiteFooter } from '@/components/SiteFooter'
import { SearchPalette } from '@/features/search/SearchPalette'

/** Signed-in pages (§12.1 `(app)`) in board A's frame (lvn-backend ADR-0076): the sidebar, the top bar, the page. */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <AppShell footer={<SiteFooter />}>
        <RequireSession>
          {children}
          <TermsGate />
          <SearchPalette />
        </RequireSession>
      </AppShell>
    </AuthProvider>
  )
}
