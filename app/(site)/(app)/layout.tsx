import { AuthProvider } from '@/components/auth/AuthProvider'
import { RequireSession } from '@/components/auth/RequireSession'
import { TermsGate } from '@/components/auth/TermsGate'
import { SearchPalette } from '@/features/search/SearchPalette'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

/** Signed-in pages (§12.1 `(app)`): the account page and the notes; each page sets its own width. */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SiteHeader />
      <main id="main" className="mx-auto min-h-[70dvh] w-full max-w-6xl px-4 py-6 sm:py-8">
        <RequireSession>
          {children}
          <TermsGate />
          <SearchPalette />
        </RequireSession>
      </main>
      <SiteFooter />
    </AuthProvider>
  )
}
