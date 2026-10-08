import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { SignUpForm } from '@/components/auth/SignUpForm'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('auth.signUp'))('title') }
}

export default function SignUpPage() {
  return (
    <Suspense>
      <SignUpForm />
    </Suspense>
  )
}
