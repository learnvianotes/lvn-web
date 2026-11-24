'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { BookOpen, CalendarClock, Library, ListChecks, RotateCcw, TrendingUp, X } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { LoadFailed } from '@/components/ui/query-state'
import { DismissRecommendationDocument, RecommendationsDocument, type RecommendationKind, type RecommendationsQuery } from '@/graphql/generated/graphql'

type Rec = RecommendationsQuery['recommendations'][number]

const ICONS: Record<RecommendationKind, typeof BookOpen> = { EXAM_TOPIC: CalendarClock, REVISE_TOPIC: RotateCcw, CONTINUE_NOTE: BookOpen, QUIZ_ON_TOPIC: ListChecks, POPULAR_NOTE: TrendingUp, RESOURCE: Library }
const coreName = (key: string) => key.replace(/^core:/, '').replace('/', ' / ').replace(/-/g, ' ')

/** Where an item leads: the note, or the notes on the topic. */
function hrefOf(r: Rec): string {
  if (r.note) return `/notes/${r.note.id}`
  if (r.resource) return `/resources/${r.resource.id}`
  if (r.topic) return `/search?topic=${r.topic.id}&topicTitle=${encodeURIComponent(r.topicTitle ?? '')}`
  return `/search?q=${encodeURIComponent(r.topicTitle ?? coreName(r.topicKey ?? ''))}`
}

/**
 * Recommended for the viewer (lvn-backend ADR-0071): each with why, best first; one can be set aside for 30 days. The
 * API reads every note through the read rule when asked, so nothing here is a note the viewer may not open.
 */
export function Recommendations({ limit = 6 }: { limit?: number }) {
  const t = useTranslations('recommendations')
  const { data, error, refetch } = useQuery(RecommendationsDocument, { variables: { limit }, fetchPolicy: 'cache-and-network' })
  const [dismiss] = useMutation(DismissRecommendationDocument, { refetchQueries: [RecommendationsDocument] })
  const items = data?.recommendations
  // Nothing while it loads (the page around it is there); a failure says so in one line where the list would be.
  if (!items) return error && !data ? <LoadFailed message={t('loadFailed')} onRetry={refetch} /> : null
  return (
    <section aria-labelledby="recommended" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="recommended" className="text-lg font-semibold">
        {t('title')}
      </h2>
      {!items.length ? <p className="text-sm text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-2">
        {items.map((r) => {
          const Icon = ICONS[r.kind]
          const title = r.resource?.title || r.noteTitle || r.topicTitle || (r.topicKey ? coreName(r.topicKey) : t('untitled'))
          const entityId = r.resource?.id ?? r.note?.id ?? r.topicKey ?? ''
          return (
            <li key={`${r.kind}:${entityId}`} className="flex items-start gap-3 rounded-xl bg-surface-2 px-3 py-2.5">
              <Icon aria-hidden className="mt-0.5 size-5 shrink-0 text-accent" />
              <Link href={hrefOf(r)} className="flex min-w-0 flex-1 flex-col hover:underline">
                <span className="truncate font-medium">{title}</span>
                <span className="text-sm text-muted">{r.reason}</span>
              </Link>
              <button type="button" aria-label={t('dismiss', { title })} className="rounded-full p-1 text-muted hover:bg-surface hover:text-fg" onClick={() => void dismiss({ variables: { input: { kind: r.kind, entityId } } })}>
                <X aria-hidden className="size-4" />
              </button>
            </li>
          )
        })}
      </ul>
    </section>
  )
}
