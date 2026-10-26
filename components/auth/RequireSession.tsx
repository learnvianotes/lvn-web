'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, type ReactNode } from 'react'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { retrySession } from '@/lib/auth/session'
import { useSession } from '@/state/session'

/** Shows children to signed-in visitors; sends everyone else to sign in and back here afterwards. */
export function RequireSession({ children }: { children: ReactNode }) {
  const status = useSession((s) => s.status)
  const t = useTranslations('states')
  const router = useRouter()
  const path = usePathname()
  useEffect(() => {
    if (status === 'signed-out') router.replace(`/sign-in?next=${encodeURIComponent(path)}`)
  }, [status, router, path])
  if (status === 'signed-in') return <>{children}</>
  if (status === 'unreachable') {
    return (
      <div className="mx-auto max-w-md py-16">
        <LoadFailed message={t('offline')} onRetry={() => retrySession()} />
      </div>
    )
  }
  return <Loading className="py-16" />
}
