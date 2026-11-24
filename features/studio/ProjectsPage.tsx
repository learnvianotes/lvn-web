'use client'

import { useApolloClient } from '@apollo/client/react'
import { FolderKanban, Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { AiButton } from '@/features/ai/AiPanel'
import { AiResultPanel } from '@/features/ai/AiAction'
import { CreateNoteDocument } from '@/graphql/generated/graphql'
import { useStudioAsk } from './useStudioAsk'

/** A project workspace: a brief, a task board and links, not a note in a list. */
export function ProjectsPage() {
  const t = useTranslations('studio.projects')
  const client = useApolloClient()
  const router = useRouter()
  const [brief, setBrief] = useState('')
  const [tasks, setTasks] = useState<{ id: string; text: string; done: boolean }[]>([{ id: 't1', text: '', done: false }])
  const [link, setLink] = useState('')
  const [links, setLinks] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const ai = useStudioAsk(t('noteTitle'), [brief, ...tasks.map((task) => task.text), ...links].filter(Boolean).join('\n'))
  const create = async () => {
    setError(null)
    try {
      const res = await client.mutate({ mutation: CreateNoteDocument, variables: { input: { title: brief.trim() || t('noteTitle'), kind: 'PROJECT' } } })
      const id = res.data?.createNote.note?.id
      if (id) router.push(`/notes/${id}`)
      else setError(res.data?.createNote.userErrors[0]?.message ?? t('failed'))
    } catch {
      setError(t('failed'))
    }
  }
  return (
    <div className="flex w-full flex-col gap-4">
      <header className="flex flex-wrap items-start justify-between gap-3 rounded-3xl border border-warn/30 bg-warn/10 px-4 py-4 text-warn">
        <div className="flex min-w-0 flex-col gap-1">
          <p className="text-xs font-semibold">{t('kicker')}</p>
          <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-tight sm:text-3xl">
            <FolderKanban className="size-7 shrink-0" aria-hidden />
            {t('title')}
          </h1>
          <p className="max-w-2xl text-sm text-warn">{t('lead')}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <AiButton onClick={() => void ai.ask()} />
          <Button type="button" className="gap-1.5" onClick={() => void create()}>
            <Plus className="size-4" aria-hidden />
            {t('open')}
          </Button>
        </div>
      </header>
      {error ? <p role="alert" className="text-sm text-bad">{error}</p> : null}
      <div className="grid gap-3 lg:grid-cols-3">
        <section aria-labelledby="project-brief" className="flex flex-col gap-2 rounded-2xl border border-warn/20 bg-surface p-4">
          <h2 id="project-brief" className="text-sm font-semibold text-warn">{t('brief')}</h2>
          <textarea value={brief} onChange={(event) => setBrief(event.target.value)} placeholder={t('briefPlaceholder')} className="min-h-40 w-full resize-y rounded-xl border border-border bg-bg px-3 py-2 text-sm outline-none focus-visible:border-accent" />
        </section>
        <section aria-labelledby="project-board" className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
          <h2 id="project-board" className="text-sm font-semibold text-muted">{t('board')}</h2>
          <ul className="flex flex-col gap-2">
            {tasks.map((task) => (
              <li key={task.id} className="flex items-center gap-2">
                <input type="checkbox" checked={task.done} aria-label={t('done')} onChange={() => setTasks((list) => list.map((item) => (item.id === task.id ? { ...item, done: !item.done } : item)))} />
                <input value={task.text} aria-label={t('task')} onChange={(event) => setTasks((list) => list.map((item) => (item.id === task.id ? { ...item, text: event.target.value } : item)))} placeholder={t('taskPlaceholder')} className="h-10 min-w-0 flex-1 rounded-lg border border-border bg-bg px-2 text-sm" />
              </li>
            ))}
          </ul>
          <Button type="button" variant="secondary" size="sm" onClick={() => setTasks((list) => [...list, { id: crypto.randomUUID(), text: '', done: false }])}>
            {t('addTask')}
          </Button>
        </section>
        <section aria-labelledby="project-links" className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
          <h2 id="project-links" className="text-sm font-semibold text-muted">{t('links')}</h2>
          <form
            className="flex gap-2"
            onSubmit={(event) => {
              event.preventDefault()
              if (!link.trim()) return
              setLinks((list) => [...list, link.trim()])
              setLink('')
            }}
          >
            <input value={link} onChange={(event) => setLink(event.target.value)} aria-label={t('link')} placeholder={t('linkPlaceholder')} className="h-10 min-w-0 flex-1 rounded-lg border border-border bg-bg px-2 text-sm" />
            <Button type="submit" size="sm" variant="secondary">{t('addLink')}</Button>
          </form>
          <ul className="flex flex-col gap-1 text-sm">
            {links.map((item) => (
              <li key={item} className="truncate rounded-lg bg-surface-2 px-2 py-1">{item}</li>
            ))}
          </ul>
        </section>
      </div>
      <AiResultPanel empty={!ai.busy && !ai.result && !ai.error}>
        {ai.busy ? <p className="text-sm text-muted">{t('working')}</p> : null}
        {ai.error ? <p role="alert" className="text-sm text-bad">{ai.error}</p> : null}
        {ai.result ? <p className="whitespace-pre-wrap text-sm leading-6">{ai.result}</p> : null}
      </AiResultPanel>
    </div>
  )
}
