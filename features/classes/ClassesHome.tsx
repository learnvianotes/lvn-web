'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { QueryState } from '@/components/ui/query-state'
import { attempt } from '@/features/groups/shared'
import { AnswerClassroomInviteDocument, CreateClassroomDocument, MyClassroomsDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { ClassCardView, cleanCode } from './shared'

/** /classes (lvn-backend ADR-0046): your classes, invites waiting for you, joining with a code, and starting one. */
export function ClassesHome() {
  const t = useTranslations('classes')
  const router = useRouter()
  const viewer = useQuery(ViewerDocument)
  const { data, loading, error: queryError, refetch } = useQuery(MyClassroomsDocument, { fetchPolicy: 'cache-and-network' })
  const [answer] = useMutation(AnswerClassroomInviteDocument)
  const [creating, setCreating] = useState(false)
  const [code, setCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  // Verified teachers, and teacher applicants who prepare classes while they wait (lvn-backend ADR-0073).
  const teacher = viewer.data?.viewer?.globalRole === 'TEACHER' || viewer.data?.viewer?.teacherStatus === 'PENDING'
  const reply = async (inviteId: string, accept: boolean) => {
    setError(await attempt(() => answer({ variables: { inviteId, accept } }), t('failed')))
    await refetch()
  }

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8">
      <header className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        {teacher ? (
          <Button className="gap-1.5" onClick={() => setCreating(true)}>
            <Plus className="size-4" aria-hidden />
            {t('new')}
          </Button>
        ) : null}
      </header>
      <form
        className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4"
        onSubmit={(e) => {
          e.preventDefault()
          if (cleanCode(code)) router.push(`/classes/join/${encodeURIComponent(cleanCode(code))}?via=code`)
        }}
      >
        <h2 className="font-semibold">{t('joinTitle')}</h2>
        <div className="flex flex-wrap gap-2">
          <label className="min-w-0 flex-1">
            <span className="sr-only">{t('codeLabel')}</span>
            <input value={code} onChange={(e) => setCode(e.target.value)} placeholder={t('codePlaceholder')} autoCapitalize="characters" autoComplete="off" spellCheck={false} maxLength={16} className="h-11 w-full rounded-xl border border-border bg-bg px-3 font-mono uppercase tracking-widest" />
          </label>
          <Button type="submit" disabled={!cleanCode(code)}>
            {t('find')}
          </Button>
        </div>
      </form>
      {data?.myClassroomInvites.length ? (
        <section aria-labelledby="class-invites" className="flex flex-col gap-3">
          <h2 id="class-invites" className="text-sm font-semibold text-muted">
            {t('invites')}
          </h2>
          <ul className="flex flex-col gap-2">
            {data.myClassroomInvites.map((i) => (
              <li key={i.id} className="flex flex-wrap items-center gap-3 rounded-2xl border border-accent/40 bg-accent-soft/40 px-4 py-3">
                <span className="flex min-w-0 flex-1 flex-col">
                  <span className="font-semibold">{i.classroom.name}</span>
                  <span className="text-sm text-muted">{t('invitedBy', { name: i.invitedBy.displayName, role: t(`role.${i.role}`) })}</span>
                </span>
                <Button size="sm" onClick={() => void reply(i.id, true)}>
                  {t('accept')}
                </Button>
                <Button variant="secondary" size="sm" onClick={() => void reply(i.id, false)}>
                  {t('decline')}
                </Button>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <section aria-labelledby="my-classes" className="flex flex-col gap-3">
        <h2 id="my-classes" className="text-sm font-semibold text-muted">
          {t('mine')}
        </h2>
        {data?.myClassrooms.length ? (
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.myClassrooms.map((c) => (
              <li key={c.id}>
                <ClassCardView classroom={c} />
              </li>
            ))}
          </ul>
        ) : data ? (
          <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{teacher ? t('noneYetTeacher') : t('noneYet')}</p>
        ) : (
          <QueryState loading={loading} error={queryError} onRetry={refetch} />
        )}
      </section>
      <CreateClassDialog open={creating} onClose={() => setCreating(false)} />
    </div>
  )
}

function CreateClassDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const t = useTranslations('classes')
  const router = useRouter()
  const [create, creating] = useMutation(CreateClassroomDocument)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const submit = async () => {
    let id: string | undefined
    const problem = await attempt(async () => {
      const res = await create({ variables: { input: { name, description: description || null } } })
      id = res.data?.createClassroom.classroom?.id
      return res
    }, t('failed'))
    if (problem) return setError(problem)
    if (id) router.push(`/classes/${id}`)
  }
  return (
    <Dialog open={open} onClose={onClose} title={t('new')}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(e) => {
          e.preventDefault()
          void submit()
        }}
      >
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-semibold">{t('name')}</span>
          <input value={name} maxLength={80} required onChange={(e) => setName(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-semibold">{t('description')}</span>
          <textarea value={description} maxLength={2000} rows={3} onChange={(e) => setDescription(e.target.value)} className="rounded-xl border border-border bg-surface px-3 py-2" />
        </label>
        {error ? (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        ) : null}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button type="submit" disabled={creating.loading}>
            {t('create')}
          </Button>
        </div>
      </form>
    </Dialog>
  )
}
