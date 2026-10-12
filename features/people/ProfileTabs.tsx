'use client'

import { FileText } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { publicNotePath } from '@/features/public-notes/paths'
import type { PublicProfile } from './data'

type Kind = PublicProfile['notes'][number]['kind']

/** Notes · Projects for everyone; teachers add Blog and Posts (ADR-0014, ADR-0015). */
export function ProfileTabs({ teacher, notes }: { teacher: boolean; notes: PublicProfile['notes'] }) {
  const t = useTranslations('people.tabs')
  const kinds: Kind[] = teacher ? ['NOTE', 'BLOG', 'PROJECT', 'POST'] : ['NOTE', 'PROJECT']
  const [kind, setKind] = useState<Kind>('NOTE')
  const shown = notes.filter((n) => n.kind === kind)
  return (
    <section className="flex flex-col gap-4">
      <div role="tablist" aria-label={t('label')} className="flex gap-1 overflow-x-auto border-b border-border">
        {kinds.map((k) => (
          <button
            key={k}
            role="tab"
            type="button"
            aria-selected={k === kind}
            onClick={() => setKind(k)}
            className={`-mb-px whitespace-nowrap border-b-2 px-4 py-2 text-sm font-semibold ${k === kind ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}
          >
            {t(k)} <span className="font-normal">{notes.filter((n) => n.kind === k).length}</span>
          </button>
        ))}
      </div>
      <div role="tabpanel">
        {shown.length ? (
          <ul className="grid gap-3 sm:grid-cols-2">
            {shown.map((n) => (
              <li key={n.id}>
                <Link href={publicNotePath(n)} className="flex h-full items-start gap-3 rounded-2xl border border-border bg-surface p-4 transition hover:border-accent/50 hover:shadow-md">
                  <FileText className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
                  <span className="flex min-w-0 flex-col">
                    <span className="font-semibold">{n.title || t('untitled')}</span>
                    {n.publishedAt ? <span className="text-xs text-muted">{new Date(n.publishedAt).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' })}</span> : null}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-muted">{t(`empty.${kind}`)}</p>
        )}
      </div>
    </section>
  )
}
