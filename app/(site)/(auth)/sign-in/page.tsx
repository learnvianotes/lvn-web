import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { SignInForm } from '@/components/auth/SignInForm'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('auth.signIn'))('title'), robots: { index: false } }
}

export default function SignInPage() {
  return (
    <Suspense>
      <SignInForm />
    </Suspense>
  )
}
