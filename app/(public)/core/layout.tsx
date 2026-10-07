import { TabsEnhancer } from '@/features/core-content/components/TabsEnhancer'
import '@/features/core-content/content.css'

/** /core — the existing LearnViaNotes study content, read-only and statically generated (ADR-0002). */
export default function CoreLayout({ children }: { children: React.ReactNode }) {
  return (
    <>
      <TabsEnhancer />
      {children}
    </>
  )
}
