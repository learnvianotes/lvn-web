import { AuthProvider } from '@/components/auth/AuthProvider'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

/** Sign-in, sign-up, verification and reset (§12.1 `(auth)`): client pages around one narrow card. */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthProvider>
      <SiteHeader />
      <main id="main" className="mx-auto flex min-h-[70dvh] w-full max-w-md flex-col px-4 py-10">{children}</main>
      <SiteFooter />
    </AuthProvider>
  )
}
