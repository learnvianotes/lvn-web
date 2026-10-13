'use client'

import type { Reference } from '@apollo/client'
import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import {
  BookOpenCheck,
  Brain,
  Check,
  CircleHelp,
  CodeXml,
  Copy,
  FilePlus2,
  Languages,
  Layers,
  Lightbulb,
  ListChecks,
  ListTree,
  LoaderCircle,
  NotebookPen,
  Plus,
  RotateCcw,
  ScrollText,
  SearchCheck,
  Sparkles,
  Trash2,
  type LucideIcon,
} from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import {
  AiArtifactDocument,
  AiStateDocument,
  DeleteAiArtifactDocument,
  KeepAiCardsDocument,
  NoteAiArtifactsDocument,
  RunAiTaskDocument,
  type AiArtifactFieldsFragment,
  type AiLanguage,
  type AiTask,
  type KeepCardsInto,
} from '@/graphql/generated/graphql'
import type { CardType } from '@/lib/contracts/domain/enums'
import { cn } from '@/lib/cn'
import { CardView } from '@/features/notes/render/CardView'
import { Markdown } from '@/features/notes/render/Markdown'

/**
 * AI tasks on a note (lvn-backend ADR-0059): one menu for every task, results beside the note that only their maker
 * sees, and cards kept in one tap — into this note for people who may edit it, otherwise into a new private note.
 */

type Artifact = AiArtifactFieldsFragment

const TASKS: { task: AiTask; icon: LucideIcon }[] = [
  { task: 'SUMMARIZE', icon: ScrollText },
  { task: 'KEY_CONCEPTS', icon: Lightbulb },
  { task: 'EXPLAIN_SIMPLY', icon: Brain },
  { task: 'PRACTICE_QUESTIONS', icon: CircleHelp },
  { task: 'FIND_MISTAKES', icon: SearchCheck },
  { task: 'EXPLAIN_CODE', icon: CodeXml },
  { task: 'FLASHCARDS', icon: Layers },
  { task: 'QUIZ', icon: ListChecks },
  { task: 'REVISION_SHEET', icon: BookOpenCheck },
  { task: 'CREATE_NOTES', icon: NotebookPen },
  { task: 'OUTLINE_TO_NOTE', icon: ListTree },
]
/** Make something new from the note, so they need the right to copy it and are always kept as a new note (ADR-0025). */
const DERIVATIVE = new Set<AiTask>(['CREATE_NOTES', 'OUTLINE_TO_NOTE'])
const LANGUAGES: AiLanguage[] = ['HINDI', 'TELUGU', 'ENGLISH']
const POLL_MS = 1500

/** What went wrong, in the server's words: refusals arrive as errors, AI being off or the day's allowance as userErrors. */
function problemOf(error: unknown, payload: { userErrors: { message: string }[] } | null | undefined, fallback: string) {
  if (CombinedGraphQLErrors.is(error)) return error.errors[0]?.message ?? fallback
  return error ? fallback : (payload?.userErrors[0]?.message ?? null)
}

async function attempt<T>(run: () => Promise<T>): Promise<{ result: T | null; error: unknown }> {
  try {
    return { result: await run(), error: null }
  } catch (error) {
    return { result: null, error }
  }
}

export interface AiPanelProps {
  noteId: string
  open: boolean
  onClose: () => void
  /** viewerCan.edit: cards may go into this note */
  canEdit: boolean
  /** viewerCan.fork: CREATE_NOTES and OUTLINE_TO_NOTE */
  canFork: boolean
  /** false hides "Explain the code" for a note without code cards; the editor leaves it unset, since its cards change */
  hasCode?: boolean
  /** After cards were added to this note's draft, so the editor can load them */
  onAddedToNote?: () => void
}

export function AiPanel({ noteId, open, onClose, canEdit, canFork, hasCode, onAddedToNote }: AiPanelProps) {
  const t = useTranslations('ai')
  const state = useQuery(AiStateDocument, { skip: !open, fetchPolicy: 'cache-and-network' })
  const list = useQuery(NoteAiArtifactsDocument, { variables: { noteId }, skip: !open, fetchPolicy: 'cache-and-network' })
  const [runTask, running] = useMutation(RunAiTaskDocument)
  const [language, setLanguage] = useState<AiLanguage>('HINDI')
  const [error, setError] = useState<string | null>(null)
  const status = state.data?.aiStatus
  const allowance = state.data?.myAiAllowance
  const spent = allowance?.limitToday != null && allowance.usedToday >= allowance.limitToday
  const off = status ? !status.available : false
  const artifacts = list.data?.note?.aiArtifacts ?? []
  const tasks = TASKS.filter(({ task }) => (DERIVATIVE.has(task) ? canFork : task === 'EXPLAIN_CODE' ? hasCode !== false : true))

  const run = async (task: AiTask, lang: AiLanguage = 'ENGLISH') => {
    setError(null)
    const { result, error } = await attempt(() =>
      runTask({
        variables: { input: { noteId, task, language: lang } },
        update(cache, { data }) {
          const made = data?.runAiTask.artifact
          if (!made) return
          cache.modify({
            id: cache.identify({ __typename: 'Note', id: noteId }),
            fields: { aiArtifacts: (existing, { toReference }) => [toReference({ __typename: 'AiArtifact', id: made.id }), ...(Array.isArray(existing) ? existing : [])] },
          })
        },
      }),
    )
    const payload = result?.data?.runAiTask
    setError(problemOf(error, payload, t('runFailed')))
    // The allowance changed, or AI turned out to be off: ask again.
    if (payload?.userErrors.length) void state.refetch()
  }

  return (
    <Dialog open={open} onClose={onClose} title={t('title')} side>
      <div className="flex flex-col gap-5">
        <p className="text-sm text-muted">{t('lead')}</p>
        {status && !status.available ? (
          <p role="alert" className="rounded-xl border border-amber-500/40 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">
            {t(`unavailable.${status.reason ?? 'NOT_CONFIGURED'}`)}
          </p>
        ) : null}
        {allowance && !off ? <Allowance used={allowance.usedToday} limit={allowance.limitToday} resetsAt={allowance.resetsAt} /> : null}

        <section aria-label={t('tasks')} className="flex flex-col gap-2">
          <div className="grid grid-cols-2 gap-2">
            {tasks.map(({ task, icon: Icon }) => (
              <button
                key={task}
                type="button"
                disabled={off || spent || running.loading}
                onClick={() => void run(task)}
                className="flex flex-col items-start gap-1 rounded-xl border border-border bg-surface p-3 text-left transition hover:border-accent hover:bg-accent-soft disabled:pointer-events-none disabled:opacity-50"
              >
                <span className="flex items-center gap-1.5 text-sm font-semibold">
                  <Icon className="size-4 text-accent" aria-hidden />
                  {t(`task.${task}`)}
                </span>
                <span className="text-xs leading-snug text-muted">{t(`hint.${task}`)}</span>
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 rounded-xl border border-border bg-surface p-2 pl-3">
            <Languages className="size-4 shrink-0 text-accent" aria-hidden />
            <label htmlFor={`ai-language-${noteId}`} className="text-sm font-semibold">
              {t('translateInto')}
            </label>
            <select id={`ai-language-${noteId}`} value={language} onChange={(e) => setLanguage(e.target.value as AiLanguage)} className="h-9 min-w-0 flex-1 rounded-lg border border-border bg-bg px-2 text-sm">
              {LANGUAGES.map((l) => (
                <option key={l} value={l}>
                  {t(`language.${l}`)}
                </option>
              ))}
            </select>
            <Button size="sm" variant="secondary" disabled={off || spent || running.loading} onClick={() => void run('TRANSLATE', language)}>
              {t('translate')}
            </Button>
          </div>
          {error ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          ) : null}
        </section>

        <section aria-label={t('results')} className="flex flex-col gap-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-muted">{t('results')}</h3>
          {list.loading && !list.data ? <p className="text-sm text-muted">{t('loading')}</p> : null}
          {list.data && !artifacts.length ? <p className="text-sm text-muted">{t('noResults')}</p> : null}
          {artifacts.map((a) => (
            <Result key={a.id} noteId={noteId} artifact={a} canEdit={canEdit} onRetry={() => void run(a.task, a.language)} onAddedToNote={onAddedToNote} />
          ))}
        </section>
      </div>
    </Dialog>
  )
}

function Allowance({ used, limit, resetsAt }: { used: number; limit: number | null; resetsAt: string }) {
  const t = useTranslations('ai')
  if (limit == null) return <p className="text-xs text-muted">{t('noLimit')}</p>
  const time = new Date(resetsAt).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })
  const share = limit > 0 ? Math.min(1, used / limit) : 1
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-xs text-muted">
        <span>{share >= 1 ? t('allowanceSpent', { time }) : t('allowance', { percent: Math.round(share * 100) })}</span>
        {share < 1 ? <span>{t('allowanceResets', { time })}</span> : null}
      </div>
      <div role="meter" aria-label={t('allowanceLabel')} aria-valuemin={0} aria-valuemax={limit} aria-valuenow={Math.min(used, limit)} className="h-1.5 overflow-hidden rounded-full bg-surface-2">
        <div className={cn('h-full rounded-full', share >= 1 ? 'bg-red-500' : share >= 0.8 ? 'bg-amber-500' : 'bg-accent')} style={{ width: `${share * 100}%` }} />
      </div>
    </div>
  )
}

/** Asks for a result until it is READY or FAILED; the answer updates the list through the cache. */
function Poll({ id }: { id: string }) {
  useQuery(AiArtifactDocument, { variables: { id }, pollInterval: POLL_MS, fetchPolicy: 'network-only' })
  return null
}

function Result({ noteId, artifact: a, canEdit, onRetry, onAddedToNote }: { noteId: string; artifact: Artifact; canEdit: boolean; onRetry: () => void; onAddedToNote?: () => void }) {
  const t = useTranslations('ai')
  const [remove, removing] = useMutation(DeleteAiArtifactDocument)
  const [copied, setCopied] = useState(false)
  const pending = a.status === 'QUEUED' || a.status === 'RUNNING'
  const label = a.task === 'TRANSLATE' ? t('translatedInto', { language: t(`language.${a.language}`) }) : t(`task.${a.task}`)

  const drop = async () => {
    await attempt(() =>
      remove({
        variables: { id: a.id },
        update(cache, { data }) {
          if (!data?.deleteAiArtifact.ok) return
          cache.modify({
            id: cache.identify({ __typename: 'Note', id: noteId }),
            fields: { aiArtifacts: (existing, { readField }) => (Array.isArray(existing) ? existing.filter((ref: Reference) => readField('id', ref) !== a.id) : existing) },
          })
          cache.evict({ id: cache.identify({ __typename: 'AiArtifact', id: a.id }) })
        },
      }),
    )
  }
  const copy = async () => {
    await navigator.clipboard?.writeText(a.markdown ?? '').catch(() => undefined)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <article aria-label={label} data-ai-status={a.status} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <header className="flex items-center gap-2">
        <Sparkles className="size-4 shrink-0 text-accent" aria-hidden />
        <h4 className="min-w-0 flex-1 truncate text-sm font-semibold">{label}</h4>
        {a.keptAt ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-accent-soft px-2 py-0.5 text-xs text-accent">
            <Check className="size-3" aria-hidden />
            {t('kept')}
          </span>
        ) : null}
        {a.status === 'READY' && a.markdown ? (
          <Button variant="ghost" size="icon" aria-label={copied ? t('copied') : t('copy')} title={copied ? t('copied') : t('copy')} onClick={() => void copy()}>
            {copied ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}
          </Button>
        ) : null}
        {pending ? null : (
          <Button variant="ghost" size="icon" aria-label={t('delete')} title={t('delete')} disabled={removing.loading} onClick={() => void drop()}>
            <Trash2 className="size-4" aria-hidden />
          </Button>
        )}
      </header>
      {pending ? (
        <p role="status" className="flex items-center gap-2 text-sm text-muted">
          <LoaderCircle className="size-4 animate-spin" aria-hidden />
          {t(`status.${a.status as 'QUEUED' | 'RUNNING'}`)}
          <Poll id={a.id} />
        </p>
      ) : null}
      {a.status === 'FAILED' ? (
        <div className="flex flex-wrap items-center gap-2">
          <p role="alert" className="flex-1 text-sm text-red-600 dark:text-red-400">
            {a.error ?? t('runFailed')}
          </p>
          <Button size="sm" variant="secondary" className="gap-1.5" onClick={onRetry}>
            <RotateCcw className="size-4" aria-hidden />
            {t('retry')}
          </Button>
        </div>
      ) : null}
      {a.status === 'READY' && (a.truncated || a.fromPublishedVersion) ? (
        <p className="text-xs text-muted">{[a.truncated ? t('truncated') : null, a.fromPublishedVersion ? t('fromPublished') : null].filter(Boolean).join(' ')}</p>
      ) : null}
      {a.status === 'READY' && a.markdown != null ? <Markdown source={a.markdown} className="flex flex-col gap-2.5 text-sm leading-relaxed" /> : null}
      {a.status === 'READY' && a.cards ? <KeepCards artifact={a} canEdit={canEdit} onAddedToNote={onAddedToNote} /> : null}
    </article>
  )
}

function KeepCards({ artifact: a, canEdit, onAddedToNote }: { artifact: Artifact; canEdit: boolean; onAddedToNote?: () => void }) {
  const t = useTranslations('ai')
  const cards = a.cards ?? []
  const [chosen, setChosen] = useState<ReadonlySet<number>>(() => new Set(cards.map((_, i) => i)))
  const [keep, keeping] = useMutation(KeepAiCardsDocument)
  const [done, setDone] = useState<{ into: KeepCardsInto; noteId: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const intoThisNote = canEdit && !DERIVATIVE.has(a.task)

  if (!cards.length) return <p className="text-sm text-muted">{t('nothingUsable')}</p>

  const toggle = (i: number) =>
    setChosen((s) => {
      const next = new Set(s)
      if (next.has(i)) next.delete(i)
      else next.add(i)
      return next
    })
  const save = async (into: KeepCardsInto) => {
    setError(null)
    setDone(null)
    const { result, error } = await attempt(() =>
      keep({
        variables: { input: { artifactId: a.id, cardIndexes: [...chosen].sort((x, y) => x - y), into } },
        update(cache, { data }) {
          if (data?.keepAiCards.noteId) cache.modify({ id: cache.identify({ __typename: 'AiArtifact', id: a.id }), fields: { keptAt: () => new Date().toISOString() } })
        },
      }),
    )
    const payload = result?.data?.keepAiCards
    if (payload?.noteId) {
      setDone({ into, noteId: payload.noteId })
      if (into === 'NOTE') onAddedToNote?.()
    }
    setError(problemOf(error, payload, t('keepFailed')))
  }

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-muted">{DERIVATIVE.has(a.task) ? t('keepAsCopyLead') : t('keepLead')}</p>
      <ol className="flex flex-col gap-2">
        {cards.map((c, i) => (
          <li key={i} className={cn('flex gap-3 rounded-xl border p-3 transition', chosen.has(i) ? 'border-accent/40 bg-bg' : 'border-border bg-surface-2 opacity-60')}>
            <input type="checkbox" checked={chosen.has(i)} onChange={() => toggle(i)} aria-label={t('pick', { n: i + 1 })} className="mt-1 size-4 shrink-0 accent-[var(--accent)]" />
            <div className="min-w-0 flex-1 text-sm">
              <CardView id={`${a.id}-${i}`} type={c.type as CardType} content={c.content} />
            </div>
          </li>
        ))}
      </ol>
      <div className="flex flex-wrap gap-2">
        {intoThisNote ? (
          <Button size="sm" className="gap-1.5" disabled={!chosen.size || keeping.loading} onClick={() => void save('NOTE')}>
            <Plus className="size-4" aria-hidden />
            {t('addToNote', { n: chosen.size })}
          </Button>
        ) : null}
        <Button size="sm" variant={intoThisNote ? 'secondary' : 'primary'} className="gap-1.5" disabled={!chosen.size || keeping.loading} onClick={() => void save('NEW_NOTE')}>
          <FilePlus2 className="size-4" aria-hidden />
          {t('saveAsNote', { n: chosen.size })}
        </Button>
      </div>
      {done ? (
        <p role="status" className="text-sm font-medium text-accent">
          {done.into === 'NOTE' ? (
            t('addedToNote')
          ) : (
            <>
              {t('savedAsNote')}{' '}
              <Link href={`/notes/${done.noteId}`} className="underline underline-offset-2">
                {t('openNote')}
              </Link>
            </>
          )}
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </div>
  )
}

/** The button that opens the panel, the same in the editor and the reader. */
export function AiButton({ onClick, className }: { onClick: () => void; className?: string }) {
  const t = useTranslations('ai')
  return (
    <Button variant="secondary" size="sm" className={cn('gap-1.5', className)} aria-label={t('title')} onClick={onClick}>
      <Sparkles className="size-4 text-accent" aria-hidden />
      <span className="hidden sm:inline">{t('button')}</span>
    </Button>
  )
}
