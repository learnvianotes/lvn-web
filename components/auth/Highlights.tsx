import { CalendarCheck, NotebookPen, Users } from 'lucide-react'
import { getTranslations } from 'next-intl/server'
import { cn } from '@/lib/cn'

/** Three reasons to sign up, as glass chips on the night sky; they rise in one after another. */
export async function Highlights({ className }: { className?: string }) {
  const t = await getTranslations('auth.welcome.features')
  const items = [
    { Icon: NotebookPen, text: t('notes') },
    { Icon: CalendarCheck, text: t('rhythm') },
    { Icon: Users, text: t('together') },
  ]
  return (
    <ul className={cn('flex flex-col gap-2.5', className)}>
      {items.map(({ Icon, text }, i) => (
        <li key={text} className="flex w-fit animate-rise items-center gap-3 rounded-2xl border border-white/15 bg-white/10 px-3.5 py-2.5 text-[15px] font-medium" style={{ animationDelay: `${180 + i * 110}ms` }}>
          <span className="grid size-8 place-items-center rounded-xl bg-[#93C5FD]/20">
            <Icon className="size-[18px] text-[#BFDBFE]" aria-hidden />
          </span>
          {text}
        </li>
      ))}
    </ul>
  )
}
