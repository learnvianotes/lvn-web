import Link from 'next/link'
import { cn } from '@/lib/cn'
import { groupTopics } from '../group'
import type { Subject } from '../schema'

export function TopicSidebar({ subject, currentId, label }: { subject: Subject; currentId: string; label: string }) {
  return (
    <nav aria-label={label} className="hidden lg:block">
      <div className="sticky top-20 max-h-[calc(100dvh-6rem)] space-y-5 overflow-y-auto pb-8">
        {groupTopics(subject.topics).map(({ group, topics }) => (
          <div key={group || 'topics'}>
            {group && <p className="px-3 pb-1 text-xs font-semibold uppercase tracking-wider text-muted">{group}</p>}
            <ol className="space-y-0.5">
              {topics.map((topic) => (
                <li key={topic.id}>
                  <Link
                    href={`/core/${subject.id}/${topic.id}`}
                    aria-current={topic.id === currentId ? 'page' : undefined}
                    className={cn(
                      'block rounded-lg px-3 py-1.5 text-sm',
                      topic.id === currentId ? 'bg-accent-soft font-medium text-accent' : 'text-muted hover:bg-surface-2 hover:text-fg',
                    )}
                  >
                    {topic.title}
                  </Link>
                </li>
              ))}
            </ol>
          </div>
        ))}
      </div>
    </nav>
  )
}
