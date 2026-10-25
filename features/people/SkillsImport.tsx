'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { Check, Copy, RefreshCw, Trash } from 'lucide-react'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  AddExternalIdentityDocument,
  CheckExternalIdentityDocument,
  DiscardTeacherSkillsDocument,
  MySkillsImportDocument,
  MyTeacherProfileDocument,
  PublishTeacherSkillsDocument,
  RemoveExternalIdentityDocument,
  type ExternalIdentityKind,
  type TeacherSkillFieldsFragment,
} from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

const problemOf = (e: unknown, fallback: string) => (CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? fallback) : fallback)

/**
 * Importing the Skills tab from identifiers the teacher proves are theirs (lvn-backend ADR-0077): add a GitHub account
 * or a page, put the code where it proves it, check; the import arrives as drafts to publish or discard, and imported
 * items on the tab can be taken away. Verified teachers only; others read when it opens to them.
 */
export function SkillsImport({ drafts, imported }: { drafts: TeacherSkillFieldsFragment[]; imported: TeacherSkillFieldsFragment[] }) {
  const t = useTranslations('people.skills.import')
  const tk = useTranslations('people.skills')
  const format = useFormatter()
  const [waiting, setWaiting] = useState(false)
  const { data } = useQuery(MySkillsImportDocument, { fetchPolicy: 'cache-and-network', pollInterval: waiting ? 4_000 : 0 })
  // While an import runs in the background, the drafts are asked for again until they arrive.
  useQuery(MyTeacherProfileDocument, { fetchPolicy: 'network-only', pollInterval: waiting ? 4_000 : 0, skip: !waiting })
  const refetch = { refetchQueries: [MySkillsImportDocument, MyTeacherProfileDocument], awaitRefetchQueries: true }
  const [add, adding] = useMutation(AddExternalIdentityDocument, refetch)
  const [check, checking] = useMutation(CheckExternalIdentityDocument, refetch)
  const [remove] = useMutation(RemoveExternalIdentityDocument, refetch)
  const [publish] = useMutation(PublishTeacherSkillsDocument, refetch)
  const [discard] = useMutation(DiscardTeacherSkillsDocument, refetch)
  const [kind, setKind] = useState<ExternalIdentityKind | ''>('')
  const [value, setValue] = useState('')
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const [copied, setCopied] = useState<string | null>(null)
  const state = data?.mySkillsImport
  if (!state) return null
  if (!state.allowed)
    return (
      <section aria-labelledby="skills-import" className="flex flex-col gap-2 rounded-2xl border border-dashed border-border p-4">
        <h2 id="skills-import" className="text-sm font-semibold">
          {t('title')}
        </h2>
        <p className="text-sm text-muted">{t('notYet')}</p>
      </section>
    )
  const chosen = kind || state.sources[0]!
  const run = async (fn: () => Promise<{ problem?: string | null }>, done?: string) => {
    setMessage(null)
    try {
      const { problem } = await fn()
      setMessage(problem ? { ok: false, text: problem } : done ? { ok: true, text: done } : null)
      return !problem
    } catch (e) {
      setMessage({ ok: false, text: problemOf(e, tk('failed')) })
      return false
    }
  }
  const watch = () => {
    setWaiting(true)
    setTimeout(() => setWaiting(false), 60_000)
  }
  return (
    <section aria-labelledby="skills-import" className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-col gap-1">
        <h2 id="skills-import" className="text-sm font-semibold">
          {t('title')}
        </h2>
        <p className="text-sm text-muted">{t('lead')}</p>
      </div>
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          void run(async () => {
            const res = await add({ variables: { input: { kind: chosen, value } } })
            const problem = res.data?.addExternalIdentity.userErrors[0]?.message
            if (!problem) setValue('')
            return { problem }
          })
        }}
      >
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium">{t('kind')}</span>
          <select value={chosen} onChange={(e) => setKind(e.target.value as ExternalIdentityKind)} className="h-10 rounded-lg border border-border bg-bg px-2">
            {state.sources.map((s) => (
              <option key={s} value={s}>
                {tk(`source.${s}`)}
              </option>
            ))}
          </select>
        </label>
        <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
          <span className="font-medium">{chosen === 'GITHUB' ? t('githubLabel') : t('websiteLabel')}</span>
          <input value={value} onChange={(e) => setValue(e.target.value)} required placeholder={chosen === 'GITHUB' ? 'octocat' : 'https://…'} className="h-10 rounded-lg border border-border bg-bg px-3" />
        </label>
        <Button type="submit" disabled={adding.loading || !value.trim()}>
          {t('add')}
        </Button>
      </form>
      {state.identities.length ? (
        <ul aria-label={t('identities')} className="flex flex-col gap-3">
          {state.identities.map((i) => (
            <li key={i.id} className="flex flex-col gap-2 rounded-xl border border-border bg-bg p-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-semibold">{tk(`source.${i.kind}`)}</span>
                <span className="min-w-0 truncate text-muted">{i.value}</span>
                <span className={cn('rounded-full px-2 py-0.5 text-xs font-semibold', i.verified ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' : 'bg-surface-2 text-muted')}>{i.verified ? t('proven') : t('notProven')}</span>
                <span className="flex-1" />
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  className="gap-1"
                  disabled={checking.loading}
                  onClick={() =>
                    void run(async () => {
                      const res = await check({ variables: { identityId: i.id } })
                      const problem = res.data?.checkExternalIdentity.userErrors[0]?.message
                      if (!problem && res.data?.checkExternalIdentity.identity?.verified) watch()
                      return { problem }
                    }, t('checked'))
                  }
                >
                  <RefreshCw className="size-3.5" aria-hidden />
                  {i.verified ? t('refresh') : t('check')}
                </Button>
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  aria-label={t('remove', { value: i.value })}
                  onClick={() => {
                    if (!window.confirm(t('removeConfirm', { value: i.value }))) return
                    void run(async () => ({ problem: (await remove({ variables: { identityId: i.id } })).data?.removeExternalIdentity.userErrors[0]?.message }))
                  }}
                >
                  <Trash className="size-4" aria-hidden />
                </Button>
              </div>
              {!i.verified ? (
                <div className="flex flex-col gap-1">
                  <p className="text-muted">{i.instructions}</p>
                  <div className="flex items-center gap-2">
                    <code className="rounded bg-surface-2 px-2 py-1 font-mono text-xs">{i.code}</code>
                    <Button
                      type="button"
                      size="sm"
                      variant="ghost"
                      className="gap-1"
                      onClick={() =>
                        void navigator.clipboard?.writeText(i.code).then(
                          () => setCopied(i.id),
                          () => undefined,
                        )
                      }
                    >
                      {copied === i.id ? <Check className="size-3.5" aria-hidden /> : <Copy className="size-3.5" aria-hidden />}
                      {copied === i.id ? t('copied') : t('copy')}
                    </Button>
                  </div>
                </div>
              ) : null}
              {i.lastError ? (
                <p role="alert" className="text-red-600 dark:text-red-400">
                  {i.lastError}
                </p>
              ) : null}
              {i.fetchedAt ? <p className="text-xs text-muted">{t('fetched', { date: format.dateTime(new Date(i.fetchedAt), { day: 'numeric', month: 'short', year: 'numeric' }) })}</p> : null}
            </li>
          ))}
        </ul>
      ) : null}
      {waiting && !drafts.length ? (
        <p role="status" className="text-sm text-muted">
          {t('importing')}
        </p>
      ) : null}
      {drafts.length ? (
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between gap-2">
            <h3 className="text-sm font-semibold">{t('drafts', { count: drafts.length })}</h3>
            <Button type="button" size="sm" onClick={() => void run(async () => ({ problem: (await publish({ variables: { skillIds: drafts.map((d) => d.id) } })).data?.publishTeacherSkills.userErrors[0]?.message }), t('published'))}>
              {t('publishAll')}
            </Button>
          </div>
          <ul aria-label={t('draftsLabel')} className="flex flex-col gap-2">
            {drafts.map((d) => (
              <li key={d.id} className="flex flex-wrap items-center gap-2 rounded-xl border border-dashed border-border px-3 py-2 text-sm">
                <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">{tk(`kind.${d.kind}`)}</span>
                <span className="flex min-w-0 flex-1 flex-col">
                  <span className="font-medium">{d.name}</span>
                  {d.detail ? <span className="text-xs text-muted">{d.detail}</span> : null}
                </span>
                <Button
                  type="button"
                  size="sm"
                  variant="secondary"
                  aria-label={t('publishOne', { name: d.name })}
                  onClick={() => void run(async () => ({ problem: (await publish({ variables: { skillIds: [d.id] } })).data?.publishTeacherSkills.userErrors[0]?.message }))}
                >
                  {t('publish')}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="ghost"
                  aria-label={t('discardOne', { name: d.name })}
                  onClick={() => void run(async () => ({ problem: (await discard({ variables: { skillIds: [d.id] } })).data?.discardTeacherSkills.userErrors[0]?.message }))}
                >
                  {t('discard')}
                </Button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {imported.length ? (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-semibold">{t('onTab')}</h3>
          <ul aria-label={t('onTab')} className="flex flex-col gap-1.5">
            {imported.map((s) => (
              <li key={s.id} className="flex items-center gap-2 text-sm">
                <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">{tk(`kind.${s.kind}`)}</span>
                <span className="min-w-0 flex-1 truncate">{s.name}</span>
                <span className="text-xs text-muted">{tk('from', { source: tk(`source.${s.source}`) })}</span>
                <Button
                  type="button"
                  size="icon"
                  variant="ghost"
                  aria-label={t('takeAway', { name: s.name })}
                  onClick={() => void run(async () => ({ problem: (await discard({ variables: { skillIds: [s.id] } })).data?.discardTeacherSkills.userErrors[0]?.message }))}
                >
                  <Trash className="size-4" aria-hidden />
                </Button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-red-600 dark:text-red-400'}>
          {message.text}
        </p>
      ) : null}
    </section>
  )
}
