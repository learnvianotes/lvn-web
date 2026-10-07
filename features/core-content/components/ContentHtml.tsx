import { cn } from '@/lib/cn'

/**
 * Pipeline HTML that went through renderContent() at build time. The source is first-party
 * content sanitised by scripts/content/sanitize.mjs, never user input — user-authored notes
 * (Phase 2) are Tiptap JSON rendered by components, not HTML.
 */
export function ContentHtml({ html, className }: { html: string; className?: string }) {
  return <div className={cn('lvn-prose', className)} dangerouslySetInnerHTML={{ __html: html }} />
}
