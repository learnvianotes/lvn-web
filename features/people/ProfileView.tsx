import { BadgeCheck, GraduationCap } from 'lucide-react'
import { getTranslations } from 'next-intl/server'
import { AchievementBadges } from '@/features/achievements/AchievementBadges'
import type { PublicProfile } from './data'
import { ProfileActions } from './ProfileActions'
import { ProfileTabs } from './ProfileTabs'

/** A person as anyone sees them (lvn-backend ADR-0043, ADR-0014, ADR-0015): who they are and what they made public. */
export async function ProfileView({ person }: { person: PublicProfile }) {
  const t = await getTranslations('people')
  const teacher = person.globalRole === 'TEACHER'
  const study = [person.profile?.department, person.profile?.yearOfStudy ? t(`year.${person.profile.yearOfStudy}`) : null].filter(Boolean).join(' · ')
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-8">
      <header className="flex flex-col gap-4 rounded-3xl border border-border bg-surface p-6 shadow-sm sm:flex-row sm:items-center">
        <span aria-hidden className="grid size-20 shrink-0 place-items-center rounded-full bg-accent-soft text-3xl font-semibold text-accent">
          {person.displayName.slice(0, 1).toUpperCase()}
        </span>
        <div className="flex min-w-0 flex-1 flex-col gap-1">
          <h1 className="flex flex-wrap items-center gap-2 text-2xl font-semibold">
            {person.displayName}
            {person.verified ? <BadgeCheck className="size-5 text-accent" aria-label={t('verified')} /> : null}
          </h1>
          <p className="text-sm text-muted">@{person.handle}</p>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-sm">
            {teacher ? (
              <span className="inline-flex items-center gap-1 rounded-[4px] bg-accent-soft px-2.5 py-0.5 font-semibold text-accent">
                <GraduationCap className="size-4" aria-hidden />
                {t('teacher')}
              </span>
            ) : null}
            {study ? <span className="text-muted">{study}</span> : null}
            {person.followerMilestone ? <span className="text-muted">{t('followersMilestone', { count: person.followerMilestone })}</span> : null}
          </div>
        </div>
        <ProfileActions id={person.id} handle={person.handle} />
      </header>
      {person.achievements?.length ? (
        <section aria-labelledby="profile-achievements" className="flex flex-col gap-3">
          <h2 id="profile-achievements" className="flex flex-wrap items-baseline gap-2 text-lg font-semibold">
            {t('achievements')}
            {person.contribution && person.contribution.level !== 'NEWCOMER' ? <span className="text-sm font-semibold text-accent">{t(`level.${person.contribution.level}`)}</span> : null}
          </h2>
          <AchievementBadges items={person.achievements} />
        </section>
      ) : null}
      <ProfileTabs teacher={teacher} notes={person.notes} skills={person.teacherProfile} />
    </div>
  )
}
