'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useEffect, type ReactNode } from 'react'
import { useSession } from '@/state/session'

/** Shows children to signed-in visitors; sends everyone else to sign in and back here afterwards. */
export function RequireSession({ children }: { children: ReactNode }) {
  const status = useSession((s) => s.status)
  const router = useRouter()
  const path = usePathname()
  useEffect(() => {
    if (status === 'signed-out') router.replace(`/sign-in?next=${encodeURIComponent(path)}`)
  }, [status, router, path])
  if (status !== 'signed-in') return <p className="py-10 text-center text-sm text-muted" role="status">…</p>
  return <>{children}</>
}
