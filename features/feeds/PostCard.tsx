'use client'

import { BookOpen, FolderGit2, Megaphone, MessageSquare, PenLine } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { ReactionBar } from '@/features/discussion/Reactions'
import { ago } from '@/features/notes/look'
import { SaveNoteButton } from '@/features/saved/SaveNoteButton'
import type { PostCardFieldsFragment } from '@/graphql/generated/graphql'

/** A picture for each kind of public note when it has none of its own (board A's cards). */
const ART = {
  NOTE: { icon: BookOpen, from: '#2847a8', to: '#2847a8' },
  BLOG: { icon: PenLine, from: '#9a4a2b', to: '#9a4a2b' },
  POST: { icon: Megaphone, from: '#4a4740', to: '#4a4740' },
  PROJECT: { icon: FolderGit2, from: '#3d6b2c', to: '#3d6b2c' },
} as const

/**
 * A public note in Community (lvn-backend ADR-0076): its author and department, when, its title and first words, its
 * picture, its topic, reactions, comments and Save. Every part leads somewhere: the note, its discussion, the topic.
 */
export function PostCard({ note, topic, onChanged }: { note: PostCardFieldsFragment; topic?: { id: string; title: string } | null; onChanged: () => void }) {
  const t = useTranslations('community')
  const art = ART[note.kind] ?? ART.NOTE
  const Icon = art.icon
  const chip = topic ?? note.topics[0] ?? null
  const href = `/notes/${note.id}`
  const department = note.owner.profile?.department
  return (
    <article aria-label={note.title || t('untitled')} className="flex flex-col overflow-hidden rounded-2xl border border-border bg-surface">
      <Link href={href} aria-hidden tabIndex={-1} className="block">
        {note.previewPicture ? (
          // eslint-disable-next-line @next/next/no-img-element -- signed storage URLs, not optimised by Next
          <img src={note.previewPicture.mediumUrl ?? note.previewPicture.url} alt="" className="h-40 w-full object-cover" />
        ) : (
          <span className="grid h-20 place-items-center" style={{ backgroundColor: art.from }}>
            <Icon className="size-7 text-white" />
          </span>
        )}
      </Link>
      <div className="flex flex-col gap-2 p-4">
        <p className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted">
          <Link href={`/u/${note.owner.handle}`} className="font-semibold text-fg hover:text-accent">
            {note.owner.displayName}
          </Link>
          {department ? <span>· {department}</span> : null}
          {note.publishedAt ? <span>· {ago(note.publishedAt)}</span> : null}
          <span className="rounded-full bg-surface-2 px-2 py-0.5 font-semibold">{t(`kind.${note.kind}`)}</span>
        </p>
        <Link href={href} className="text-lg font-semibold leading-snug hover:text-accent">
          {note.title || t('untitled')}
        </Link>
        {note.excerpt ? <p className="line-clamp-2 text-sm text-muted">{note.excerpt}</p> : null}
        {chip ? (
          <Link href={`/search?${new URLSearchParams({ topic: chip.id, topicTitle: chip.title }).toString()}`} className="w-fit rounded-[10px] bg-accent-soft px-2.5 py-0.5 text-xs font-semibold text-accent hover:underline">
            {chip.title}
          </Link>
        ) : null}
        <div className="flex flex-wrap items-center gap-3 pt-1">
          {note.discussion ? <ReactionBar target={{ type: 'NOTE', id: note.id }} reactions={note.discussion.reactions} onChanged={onChanged} size="sm" /> : null}
          <Link href={`${href}?tab=discussions`} className="inline-flex items-center gap-1 text-sm text-muted hover:text-accent">
            <MessageSquare className="size-4" aria-hidden />
            {t('comments', { count: note.discussion?.commentCount ?? 0 })}
          </Link>
          <span className="ml-auto">
            <SaveNoteButton noteId={note.id} saved={note.viewerSaved} />
          </span>
        </div>
      </div>
    </article>
  )
}
