import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import type { Subject } from '../schema'

/** Catalog icon names → Tabler icon class. */
export function iconClass(icon: string) {
  return `ti ti-${icon}`
}

export async function SubjectCard({ subject }: { subject: Subject }) {
  const t = await getTranslations('core')
  return (
    <Link
      href={`/core/${subject.id}`}
      className="group flex h-full flex-col gap-3 rounded-2xl border border-border bg-surface p-5 transition-colors hover:border-accent"
    >
      <span className="flex size-10 items-center justify-center rounded-xl bg-accent-soft text-accent">
        <i className={`${iconClass(subject.icon)} text-xl`} aria-hidden />
      </span>
      <span className="font-semibold tracking-tight group-hover:text-accent">{subject.title}</span>
      <span className="line-clamp-3 text-sm text-muted">{subject.description}</span>
      <span className="mt-auto text-xs font-medium text-muted">
        {subject.kind === 'problems' ? t('problems', { count: subject.itemCount }) : t('topics', { count: subject.itemCount })}
      </span>
    </Link>
  )
}
