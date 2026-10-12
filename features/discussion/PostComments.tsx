'use client'

import { MessageSquare } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Discussion } from './Discussion'

/** Under a group post or class announcement: its comment count, opening its discussion (lvn-backend ADR-0047). */
export function PostComments({ type, id, count }: { type: 'GROUP_POST' | 'CLASSROOM_POST'; id: string; count: number }) {
  const t = useTranslations('discussion')
  const [open, setOpen] = useState(false)
  return (
    <div className="flex flex-col gap-3">
      <button type="button" aria-expanded={open} onClick={() => setOpen(!open)} className="inline-flex w-fit items-center gap-1.5 text-xs font-semibold text-muted hover:text-accent">
        <MessageSquare className="size-3.5" aria-hidden />
        {open ? t('hide') : t('comments', { count })}
      </button>
      {open ? <Discussion target={{ type, id }} compact /> : null}
    </div>
  )
}
