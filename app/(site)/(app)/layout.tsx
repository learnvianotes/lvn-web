import { AuthProvider } from '@/components/auth/AuthProvider'
import { RequireSession } from '@/components/auth/RequireSession'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

/** Signed-in pages (§12.1 `(app)`). Phase 1 has the account page; the rest arrive with their backends. */
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SiteHeader />
      <main id="main" className="mx-auto min-h-[70dvh] w-full max-w-2xl px-4 py-8">
        <RequireSession>{children}</RequireSession>
      </main>
      <SiteFooter />
    </AuthProvider>
  )
}
