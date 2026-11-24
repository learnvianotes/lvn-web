import { CalendarCheck, Layers, MessagesSquare, NotebookPen, TextQuote, Users } from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'

const TILES = [
  { key: 'notes', href: '/notes', icon: NotebookPen },
  { key: 'ai', href: '/ask', icon: TextQuote },
  { key: 'groups', href: '/groups', icon: Users },
  { key: 'exams', href: '/exams', icon: CalendarCheck },
  { key: 'quizzes', href: '/review', icon: Layers },
  { key: 'community', href: '/community', icon: MessagesSquare },
] as const

/** The six ways in: what LearnViaNotes does, each a link. Quiet rows: one icon set, one stroke, muted (ADR-0114). */
export async function FeatureTiles() {
  const t = await getTranslations('home.features')
  return (
    <section id="features" aria-label={t('label')} className="relative z-10 mx-auto max-w-6xl px-4 py-10">
      <ul className="grid grid-cols-2 gap-2 rounded-2xl border border-border bg-surface p-2 sm:grid-cols-3 lg:grid-cols-6">
        {TILES.map(({ key, href, icon: Icon }) => (
          <li key={key}>
            <Link href={href} className="flex h-full flex-col items-start gap-1 rounded-xl p-4 transition-colors hover:bg-surface-2">
              <Icon className="mb-2 size-[18px] text-muted" strokeWidth={1.5} aria-hidden />
              <span className="text-sm font-medium">{t(`${key}.title`)}</span>
              <span className="text-xs text-muted">{t(`${key}.lead`)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
