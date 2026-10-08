import { FileText } from 'lucide-react'
import Link from 'next/link'
import type { ReactNode } from 'react'
import { LEGAL_DOCUMENTS, TERMS_VERSION, type LegalDocument } from './documents'

/**
 * The frame of the Terms, the Privacy Policy and the content licence (§15.2): the version people accepted, links between
 * the three, and — until the owner's lawyer has reviewed them — a banner saying they are drafts.
 */
export function LegalPage({ doc, children }: { doc: LegalDocument; children: ReactNode }) {
  const current = LEGAL_DOCUMENTS[doc]
  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-10">
      <nav aria-label="Legal" className="flex flex-wrap gap-2 text-sm">
        {(Object.keys(LEGAL_DOCUMENTS) as LegalDocument[]).map((d) => (
          <Link key={d} href={LEGAL_DOCUMENTS[d].path} aria-current={d === doc ? 'page' : undefined} className={d === doc ? 'rounded-full bg-accent px-3 py-1 font-medium text-accent-fg' : 'rounded-full border border-border px-3 py-1 text-muted hover:border-accent hover:text-accent'}>
            {LEGAL_DOCUMENTS[d].title}
          </Link>
        ))}
      </nav>
      <header className="flex flex-col gap-2">
        <h1 className="flex items-center gap-2 text-3xl font-extrabold tracking-tight">
          <FileText className="size-7 text-accent" aria-hidden />
          {current.title}
        </h1>
        <p className="text-sm text-muted">Version {TERMS_VERSION}</p>
      </header>
      <p role="note" className="rounded-2xl border border-amber-500/40 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">
        Draft for review. This text was written for LearnViaNotes’ owner to review with a lawyer before launch; items in
        [square brackets] are still to be filled in.
      </p>
      <div className="legal flex flex-col gap-4 leading-relaxed [&_h2]:mt-4 [&_h2]:text-xl [&_h2]:font-bold [&_li]:ml-5 [&_li]:list-disc [&_ul]:flex [&_ul]:flex-col [&_ul]:gap-1">{children}</div>
    </div>
  )
}
