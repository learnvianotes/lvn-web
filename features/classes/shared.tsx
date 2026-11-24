'use client'

import { GraduationCap, Users } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import type { ClassroomCardFragment } from '@/graphql/generated/graphql'

/** Codes are typed by hand: spaces and dashes are dropped, letters made upper case (lvn-backend ADR-0046). */
export const cleanCode = (code: string) => code.replace(/[\s-]+/g, '').toUpperCase()

export function ClassCardView({ classroom }: { classroom: ClassroomCardFragment }) {
  const t = useTranslations('classes')
  return (
    <Link href={`/classes/${classroom.id}`} className="flex h-full flex-col gap-2 rounded-2xl border border-border bg-surface p-4 transition-colors hover:border-accent/50 hover:shadow-md">
      <span className="flex items-center gap-2 font-semibold">
        <GraduationCap className="size-4 shrink-0 text-accent" aria-hidden />
        <span className="truncate">{classroom.name}</span>
      </span>
      <span className="truncate text-sm text-muted">{t('byTeacher', { name: classroom.teacher.displayName })}</span>
      {classroom.description ? <span className="line-clamp-2 text-sm text-muted">{classroom.description}</span> : null}
      <span className="mt-auto flex items-center gap-1.5 text-xs text-muted">
        <Users className="size-3.5" aria-hidden />
        {t('members', { count: classroom.memberCount })}
        {classroom.viewerRole ? <span className="ml-auto rounded-[10px] bg-accent-soft px-2 py-0.5 font-semibold text-accent">{t(`role.${classroom.viewerRole}`)}</span> : null}
      </span>
    </Link>
  )
}
