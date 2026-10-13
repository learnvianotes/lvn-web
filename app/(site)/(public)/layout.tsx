import { PublicFrame } from '@/components/shell/PublicFrame'
import { SiteFooter } from '@/components/SiteFooter'
import { SiteHeader } from '@/components/SiteHeader'

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return (
    <PublicFrame header={<SiteHeader />} footer={<SiteFooter />}>
      {children}
    </PublicFrame>
  )
}
