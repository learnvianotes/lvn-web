import { AdminShell } from '@/features/admin/AdminNav'

/** Shared frame for platform-admin pages. Who may see each page is still decided by that page. */
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <AdminShell>{children}</AdminShell>
}
