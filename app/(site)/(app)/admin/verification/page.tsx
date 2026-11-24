import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ReviewRequests } from '@/features/verification/ReviewRequests'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('verification.review'))('adminTitle'), robots: { index: false } }
}

/** Proof of enrolment for platform admins to review (lvn-backend ADR-0019), until the admin app exists. */
export default function VerificationReviewPage() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <ReviewRequests title />
    </div>
  )
}
