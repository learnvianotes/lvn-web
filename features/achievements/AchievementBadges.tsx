import { Brain, CalendarCheck, ClipboardCheck, HandHeart, Target, type LucideIcon } from 'lucide-react'
import { cn } from '@/lib/cn'

export type AchievementKindName = 'TOPICS_MASTERED' | 'QUIZ_MASTER' | 'EXAM_READY' | 'RHYTHM_WEEKS' | 'SUBJECT_CONTRIBUTOR'

export interface Badge {
  id: string
  kind: AchievementKindName
  title: string
  description: string
}

/** Each kind's icon and tint, as board A draws its achievement row. */
const LOOK: Record<AchievementKindName, { icon: LucideIcon; tint: string }> = {
  TOPICS_MASTERED: { icon: Brain, tint: 'bg-def/10 text-def' },
  QUIZ_MASTER: { icon: Target, tint: 'bg-warn/10 text-warn' },
  EXAM_READY: { icon: ClipboardCheck, tint: 'bg-accent/10 text-accent' },
  RHYTHM_WEEKS: { icon: CalendarCheck, tint: 'bg-warn/10 text-warn' },
  SUBJECT_CONTRIBUTOR: { icon: HandHeart, tint: 'bg-bad/10 text-bad' },
}

/**
 * Achievements as a row of badges (lvn-backend ADR-0080): the highest tier of each, its name under it and what it
 * means on hover and for screen readers. Used on the person's page and, when they show them, on their profile.
 */
export function AchievementBadges({ items, className }: { items: Badge[]; className?: string }) {
  return (
    <ul className={cn('grid grid-cols-2 gap-3 sm:grid-cols-4', className)}>
      {items.map((a) => {
        const { icon: Icon, tint } = LOOK[a.kind]
        return (
          <li key={a.id} className="flex flex-col items-center gap-2 rounded-2xl border border-border bg-surface p-3 text-center" title={a.description}>
            <span aria-hidden className={cn('grid size-12 place-items-center rounded-full', tint)}>
              <Icon className="size-6" />
            </span>
            <span className="text-sm font-semibold leading-tight">{a.title}</span>
            <span className="sr-only">{a.description}</span>
          </li>
        )
      })}
    </ul>
  )
}
