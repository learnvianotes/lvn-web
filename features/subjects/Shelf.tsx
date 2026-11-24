import { FileText, Library } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { publicNotePath } from '@/features/public-notes/paths'
import type { TopicNote, TopicResource } from './data'

/** Public notes and approved resources on a subject or topic, with a way to add one when there are none. */
export function Shelf({ notes, resources, topicTitle }: { notes: TopicNote[]; resources: TopicResource[]; topicTitle: string }) {
  const t = useTranslations('subjects')
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
      <section aria-labelledby="shelf-notes" className="flex flex-col gap-3">
        <h2 id="shelf-notes" className="text-lg font-semibold">
          {t('notes')}
        </h2>
        {notes.length ? (
          <ul className="flex flex-col gap-2">
            {notes.map((n) => (
              <li key={n.id}>
                <Link href={publicNotePath(n)} className="flex items-start gap-3 rounded-2xl border border-border bg-surface p-4 hover:border-accent/40">
                  <FileText className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                  <span className="flex flex-col">
                    <span className="font-semibold">{n.title || t('untitled')}</span>
                    <span className="text-xs text-muted">{t('by', { name: n.owner.displayName })}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl border border-dashed border-border px-5 py-6 text-sm text-muted">
            {t('noNotes', { topic: topicTitle })}{' '}
            <Link href="/notes" className="font-semibold text-accent hover:underline">
              {t('writeOne')}
            </Link>
          </p>
        )}
      </section>
      <section aria-labelledby="shelf-resources" className="flex flex-col gap-3">
        <h2 id="shelf-resources" className="text-lg font-semibold">
          {t('resources')}
        </h2>
        {resources.length ? (
          <ul className="flex flex-col gap-2">
            {resources.map((r) => (
              <li key={r.id}>
                <Link href={`/resources/${r.id}`} className="flex items-start gap-3 rounded-2xl border border-border bg-surface p-3 hover:border-accent/40">
                  <Library className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
                  <span className="flex min-w-0 flex-col">
                    <span className="truncate font-medium">{r.title}</span>
                    <span className="text-xs text-muted">{[r.author, r.host].filter(Boolean).join(' · ')}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted">
            {t('noResources')}{' '}
            <Link href="/resources" className="font-semibold text-accent hover:underline">
              {t('browseResources')}
            </Link>
          </p>
        )}
      </section>
    </div>
  )
}
