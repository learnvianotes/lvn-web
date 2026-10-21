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
  TOPICS_MASTERED: { icon: Brain, tint: 'bg-teal-100 text-teal-700 dark:bg-teal-500/15 dark:text-teal-300' },
  QUIZ_MASTER: { icon: Target, tint: 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300' },
  EXAM_READY: { icon: ClipboardCheck, tint: 'bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300' },
  RHYTHM_WEEKS: { icon: CalendarCheck, tint: 'bg-orange-100 text-orange-700 dark:bg-orange-500/15 dark:text-orange-300' },
  SUBJECT_CONTRIBUTOR: { icon: HandHeart, tint: 'bg-pink-100 text-pink-700 dark:bg-pink-500/15 dark:text-pink-300' },
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
