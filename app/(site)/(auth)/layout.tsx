import { AuthHero } from '@/components/auth/AuthHero'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

/**
 * Sign-in, sign-up, verification and reset (§12.1 `(auth)`): the night-sky hero, and the page as a sheet over it on
 * phones or a card beside it from `lg` — the same look as the mobile welcome screen.
 */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SiteHeader />
      <main id="main" className="mx-auto w-full max-w-6xl lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,30rem)] lg:items-start lg:gap-12 lg:px-4 lg:py-10">
        <AuthHero />
        <div className="relative -mt-6 rounded-t-[28px] bg-bg px-4 pb-12 pt-8 sm:px-6 lg:mt-0 lg:rounded-3xl lg:border lg:border-border lg:bg-surface lg:p-10 lg:shadow-sm">
          <div className="mx-auto flex min-h-[50dvh] w-full max-w-md flex-col lg:min-h-0">{children}</div>
        </div>
      </main>
      <SiteFooter />
    </AuthProvider>
  )
}
