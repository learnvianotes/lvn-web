import Link from 'next/link'
import type { Subject, TopicOutline } from '../schema'

interface Props {
  subject: Subject
  prev?: TopicOutline
  next?: TopicOutline
  labels: { previous: string; next: string }
}

export function PrevNext({ subject, prev, next, labels }: Props) {
  const card = 'flex flex-col gap-1 rounded-2xl border border-border bg-surface p-4 hover:border-accent'
  return (
    <nav className="mt-12 grid gap-3 sm:grid-cols-2" aria-label={`${labels.previous} / ${labels.next}`}>
      {prev ? (
        <Link href={`/core/${subject.id}/${prev.id}`} className={card} rel="prev">
          <span className="text-xs text-muted"><i className="ti ti-arrow-left" aria-hidden /> {labels.previous}</span>
          <span className="font-medium">{prev.title}</span>
        </Link>
      ) : <span />}
      {next && (
        <Link href={`/core/${subject.id}/${next.id}`} className={`${card} sm:text-right`} rel="next">
          <span className="text-xs text-muted">{labels.next} <i className="ti ti-arrow-right" aria-hidden /></span>
          <span className="font-medium">{next.title}</span>
        </Link>
      )}
    </nav>
  )
}
