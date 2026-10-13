import { BrainCircuit, CalendarCheck, Layers, NotebookPen, Users, MessagesSquare } from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

const TILES = [
  { key: 'notes', href: '/notes', icon: NotebookPen, tone: 'bg-orange-100 text-orange-600 dark:bg-orange-950/50 dark:text-orange-300' },
  { key: 'ai', href: '/ask', icon: BrainCircuit, tone: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-950/60 dark:text-indigo-300' },
  { key: 'groups', href: '/groups', icon: Users, tone: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-300' },
  { key: 'exams', href: '/exams', icon: CalendarCheck, tone: 'bg-violet-100 text-violet-600 dark:bg-violet-950/50 dark:text-violet-300' },
  { key: 'quizzes', href: '/review', icon: Layers, tone: 'bg-sky-100 text-sky-600 dark:bg-sky-950/50 dark:text-sky-300' },
  { key: 'community', href: '/community', icon: MessagesSquare, tone: 'bg-pink-100 text-pink-600 dark:bg-pink-950/50 dark:text-pink-300' },
] as const

/** Board A's six feature tiles: what LearnViaNotes does, each a way in. */
export async function FeatureTiles() {
  const t = await getTranslations('home.features')
  return (
    <section id="features" aria-label={t('label')} className="relative z-10 mx-auto -mt-10 max-w-6xl px-4">
      <ul className="grid grid-cols-2 gap-3 rounded-3xl border border-border bg-surface p-4 shadow-xl shadow-indigo-900/5 sm:grid-cols-3 sm:p-6 lg:grid-cols-6">
        {TILES.map(({ key, href, icon: Icon, tone }) => (
          <li key={key}>
            <Link href={href} className="flex h-full flex-col items-center gap-2 rounded-2xl p-3 text-center hover:bg-surface-2">
              <span className={`grid size-12 place-items-center rounded-2xl ${tone}`}>
                <Icon className="size-6" aria-hidden />
              </span>
              <span className="text-sm font-semibold">{t(`${key}.title`)}</span>
              <span className="text-xs text-muted">{t(`${key}.lead`)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
