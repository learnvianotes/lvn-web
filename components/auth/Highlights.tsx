import { CalendarCheck, NotebookPen, Users } from 'lucide-react'
import { getTranslations } from 'next-intl/server'
import { cn } from '@/lib/cn'

/** Three reasons to sign up, as quiet rows: one icon set, one stroke, muted (ADR-0114). */
export async function Highlights({ className }: { className?: string }) {
  const t = await getTranslations('auth.welcome.features')
  const items = [
    { Icon: NotebookPen, text: t('notes') },
    { Icon: CalendarCheck, text: t('rhythm') },
    { Icon: Users, text: t('together') },
  ]
  return (
    <ul className={cn('flex flex-col gap-3', className)}>
      {items.map(({ Icon, text }) => (
        <li key={text} className="flex items-center gap-3 text-[15px]">
          <Icon className="size-[18px] shrink-0 text-muted" strokeWidth={1.5} aria-hidden />
          {text}
        </li>
      ))}
    </ul>
  )
}
