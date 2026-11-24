import type { Metadata } from 'next'
import { AuthHero } from '@/components/auth/AuthHero'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

/** Sign-in pages are for people, not search results (links in emails carry tokens). */
export const metadata: Metadata = { robots: { index: false, follow: false } }

/**
 * Sign-in, sign-up, verification and reset (§12.1 `(auth)`): the form alone on phones, and from `lg` a card beside a
 * quiet panel that says what LearnViaNotes is (ADR-0114).
 */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SiteHeader />
      <main id="main" className="mx-auto w-full max-w-6xl lg:grid lg:grid-cols-[minmax(0,1fr)_minmax(0,30rem)] lg:items-start lg:gap-12 lg:px-4 lg:py-10">
        <AuthHero />
        <div className="px-4 pb-12 pt-8 sm:px-6 lg:rounded-2xl lg:border lg:border-border lg:bg-surface lg:p-10 lg:shadow-sm">
          <div className="mx-auto flex min-h-[50dvh] w-full max-w-md flex-col lg:min-h-0">{children}</div>
        </div>
      </main>
      <SiteFooter />
    </AuthProvider>
  )
}
