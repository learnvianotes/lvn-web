import { BrainCircuit, CalendarCheck, Layers, NotebookPen, Users, MessagesSquare } from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

const TILES = [
  { key: 'notes', href: '/notes', icon: NotebookPen },
  { key: 'ai', href: '/ask', icon: BrainCircuit },
  { key: 'groups', href: '/groups', icon: Users },
  { key: 'exams', href: '/exams', icon: CalendarCheck },
  { key: 'quizzes', href: '/review', icon: Layers },
  { key: 'community', href: '/community', icon: MessagesSquare },
] as const

/** Board A's six feature tiles: what LearnViaNotes does, each a way in. */
export async function FeatureTiles() {
  const t = await getTranslations('home.features')
  return (
    <section id="features" aria-label={t('label')} className="relative z-10 mx-auto max-w-6xl px-4 py-10">
      <ul className="grid grid-cols-2 gap-3 rounded-3xl border border-border bg-surface p-4 shadow-sm sm:grid-cols-3 sm:p-6 lg:grid-cols-6">
        {TILES.map(({ key, href, icon: Icon }) => (
          <li key={key}>
            <Link href={href} className="flex h-full flex-col items-center gap-2 rounded-2xl p-3 text-center hover:bg-surface-2">
              <span className="grid size-12 place-items-center rounded-2xl bg-accent-soft text-accent">
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
