import { FileText, TextQuote } from 'lucide-react'
import { getTranslations } from 'next-intl/server'

/**
 * The landing hero's visual: the product itself, drawn in code (ADR-0114, unslop). A PDF page with one line marked by
 * the highlighter, and Nova's answer to a question about it, citing the page. Plausible content from an Operating
 * Systems unit, the course most of the first users take.
 */
export async function HeroPreview({ className }: { className?: string }) {
  const t = await getTranslations('home.hero.preview')
  const lines = t.raw('lines') as string[]
  return (
    <div className={className} aria-hidden="true">
      <div className="relative flex flex-col gap-3">
        <div className="rounded-2xl border border-border bg-surface p-2 shadow-md">
          <div className="flex items-center gap-2 px-2 pt-1 pb-3 text-xs text-muted">
            <FileText className="size-4" strokeWidth={1.5} />
            <span className="truncate">{t('file')}</span>
            <span className="ms-auto font-mono tabular-nums">{t('page')}</span>
          </div>
          <div className="rounded-xl border border-border bg-bg px-5 py-5 sm:px-6">
            <p className="text-base font-medium">{t('heading')}</p>
            <div className="mt-3 flex flex-col gap-2 text-sm leading-6 text-muted">
              {lines.map((line, i) => (
                <p key={line} className={i === 2 ? 'text-fg' : undefined}>
                  {i === 2 ? <span className="lvn-marker">{line}</span> : line}
                </p>
              ))}
            </div>
          </div>
        </div>
        <div className="rounded-2xl border border-border bg-surface p-4 shadow-md sm:ms-10">
          <p className="text-sm font-medium">{t('question')}</p>
          <div className="mt-3 flex gap-3">
            <span className="grid size-7 shrink-0 place-items-center rounded-lg bg-accent-soft text-accent">
              <TextQuote className="size-4" strokeWidth={1.5} />
            </span>
            <div className="flex min-w-0 flex-col gap-2">
              <p className="text-sm leading-6 text-fg">{t('answer')}</p>
              <p className="flex items-center gap-2 text-xs text-muted">
                <span className="lvn-marker rounded px-1 font-mono text-fg">{t('cite')}</span>
                <span>{t('askedBy')}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
