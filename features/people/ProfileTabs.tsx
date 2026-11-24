'use client'

import { FileText } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { publicNotePath } from '@/features/public-notes/paths'
import { safeLinkHref } from '@/lib/http-url'
import type { PublicProfile } from './data'

type Kind = PublicProfile['notes'][number]['kind'] | 'SKILLS'

/** Notes · Projects for everyone; teachers add Blog, Posts and Skills (ADR-0012, ADR-0014, ADR-0015). */
export function ProfileTabs({ teacher, notes, skills }: { teacher: boolean; notes: PublicProfile['notes']; skills: PublicProfile['teacherProfile'] }) {
  const t = useTranslations('people.tabs')
  const kinds: Kind[] = teacher ? ['NOTE', 'BLOG', 'PROJECT', 'POST', 'SKILLS'] : ['NOTE', 'PROJECT']
  const [kind, setKind] = useState<Kind>('NOTE')
  const shown = notes.filter((n) => n.kind === kind)
  return (
    <section className="flex flex-col gap-4">
      <div role="tablist" aria-label={t('label')} className="flex gap-1 overflow-x-auto border-b border-border">
        {kinds.map((k) => (
          <button
            key={k}
            role="tab"
            type="button"
            aria-selected={k === kind}
            onClick={() => setKind(k)}
            className={`-mb-px whitespace-nowrap border-b-2 px-4 py-2 text-sm font-semibold ${k === kind ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}
          >
            {t(k)} {k === 'SKILLS' ? null : <span className="font-normal">{notes.filter((n) => n.kind === k).length}</span>}
          </button>
        ))}
      </div>
      <div role="tabpanel">
        {kind === 'SKILLS' ? (
          <Skills profile={skills} />
        ) : shown.length ? (
          <ul className="grid gap-3 sm:grid-cols-2">
            {shown.map((n) => (
              <li key={n.id}>
                <Link href={publicNotePath(n)} className="flex h-full items-start gap-3 rounded-2xl border border-border bg-surface p-4 transition hover:border-accent/50 hover:shadow-md">
                  <FileText className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
                  <span className="flex min-w-0 flex-col">
                    <span className="font-semibold">{n.title || t('untitled')}</span>
                    {n.publishedAt ? <span className="text-xs text-muted">{new Date(n.publishedAt).toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' })}</span> : null}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-muted">{t(`empty.${kind}`)}</p>
        )}
      </div>
    </section>
  )
}

const SKILL_KINDS = ['QUALIFICATION', 'EXPERIENCE', 'SKILL', 'PROJECT', 'PUBLICATION'] as const

/** The Skills tab (ADR-0012, ADR-0077): what the teacher wrote, and what they imported with where and when it came from. */
function Skills({ profile }: { profile: PublicProfile['teacherProfile'] }) {
  const t = useTranslations('people.skills')
  if (!profile || (!profile.headline && !profile.bio && !profile.skills.length)) {
    return <p className="rounded-2xl border border-dashed border-border px-6 py-10 text-center text-muted">{t('empty')}</p>
  }
  return (
    <div className="flex flex-col gap-5">
      {profile.headline ? <p className="text-lg font-semibold">{profile.headline}</p> : null}
      {profile.bio ? <p className="whitespace-pre-line text-muted">{profile.bio}</p> : null}
      {SKILL_KINDS.map((k) => {
        const items = profile.skills.filter((s) => s.kind === k)
        if (!items.length) return null
        return (
          <section key={k} aria-labelledby={`skills-${k}`} className="flex flex-col gap-2">
            <h2 id={`skills-${k}`} className="text-sm font-semibold text-muted">
              {t(`kind.${k}`)}
            </h2>
            {k === 'SKILL' ? (
              <ul className="flex flex-wrap gap-2">
                {items.map((s) => (
                  <li
                    key={s.id}
                    className="rounded-[10px] bg-accent-soft px-3 py-1 text-sm font-medium text-accent"
                    title={[s.detail, s.source !== 'MANUAL' ? t('from', { source: t(`source.${s.source}`) }) : null].filter(Boolean).join(' · ') || undefined}
                  >
                    {s.name}
                  </li>
                ))}
              </ul>
            ) : (
              <ul className="flex flex-col gap-2">
                {items.map((s) => {
                  const href = s.kind === 'PROJECT' ? safeLinkHref(s.sourceUrl) : null
                  return (
                  <li key={s.id} className="rounded-2xl border border-border bg-surface px-4 py-3">
                    <p className="font-semibold">
                      {href ? (
                        <a href={href} rel="nofollow noopener" target="_blank" className="hover:underline">
                          {s.name}
                        </a>
                      ) : (
                        s.name
                      )}
                    </p>
                    {s.detail ? <p className="text-sm text-muted">{s.detail}</p> : null}
                    {s.source !== 'MANUAL' ? <Provenance skill={s} /> : null}
                  </li>
                  )
                })}
              </ul>
            )}
          </section>
        )
      })}
    </div>
  )
}

/** Where an imported item came from and when it was checked (ADR-0077). */
function Provenance({ skill }: { skill: NonNullable<PublicProfile['teacherProfile']>['skills'][number] }) {
  const t = useTranslations('people.skills')
  const format = useFormatter()
  const source = t(`source.${skill.source}`)
  const href = safeLinkHref(skill.sourceUrl)
  return (
    <p className="mt-1 text-xs text-muted">
      {href ? (
        <a href={href} rel="nofollow noopener" target="_blank" className="hover:underline">
          {t('from', { source })}
        </a>
      ) : (
        t('from', { source })
      )}
      {skill.fetchedAt ? ` · ${t('checked', { date: format.dateTime(new Date(skill.fetchedAt), { day: 'numeric', month: 'short', year: 'numeric' }) })}` : null}
    </p>
  )
}
