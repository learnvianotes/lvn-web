'use client'

import { usePathname, useRouter } from 'next/navigation'
import { useEffect } from 'react'
import { ADMIN_VERIFY_PATH, adminVerifyPath, isAdminMfaRole } from '@/lib/auth/mfa'
import { useSession } from '@/state/session'

/**
 * Sends an admin whose session still needs a code to the email screen, from anywhere outside the admin area.
 * Inside the admin area the layout shows the same screen and keeps the page they were on. Other roles are ignored.
 */
export function AdminMfaRedirect() {
  const pending = useSession((state) => state.mfaPending)
  const role = useSession((state) => state.role)
  const pathname = usePathname()
  const router = useRouter()

  useEffect(() => {
    if (!pending || !isAdminMfaRole(role)) return
    if (pathname === ADMIN_VERIFY_PATH || pathname.startsWith('/admin/') || pathname === '/admin') return
    const next = `${window.location.pathname}${window.location.search}`
    router.replace(adminVerifyPath(next))
  }, [pending, role, pathname, router])

  return null
}
