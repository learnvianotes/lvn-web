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
  Mic,
  Wand2,
  ScrollText,
  SearchCheck,
  SpellCheck,
  Sparkles,
  Trash2,
  type LucideIcon,
} from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useId, useState } from 'react'
import { Button } from '@/components/ui/button'
import { LimitNotice } from '@/components/ui/limit-notice'
import { limitMessageFromUserErrors, refusalMessage } from '@/lib/limit-error'
import { Dialog } from '@/components/ui/dialog'
import {
  AiArtifactDocument,
  AiStateDocument,
  ApplyAiChangesDocument,
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
import { AnswerList, AskForm } from './AskAi'

/**
 * AI tasks on a note (lvn-backend ADR-0059): one menu for every task, results beside the note that only their maker
 * sees, and cards kept in one tap — into this note for people who may edit it, otherwise into a new private note.
 * Clean-up (ADR-0063) proposes changes to the note's own words instead, which its editor reviews and applies.
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
  { task: 'QUICK_NOTE', icon: Wand2 },
  { task: 'CLEAN_UP', icon: SpellCheck },
]
/** Work on the person's own words: only for people who may edit the note. */
const EDITORS_ONLY = new Set<AiTask>(['QUICK_NOTE', 'CLEAN_UP'])
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
  /** After clean-up changed some of its cards' words (and left `refused` ones edited since), so the editor can load them */
  onTextMended?: (applied: number, refused: number) => void
}

/**
 * Running AI tasks on a note, for the panel and the note view's dock and tabs (ADR-0076): AI's state and the day's
 * allowance, and `run`, which puts the new result at the top of the note's results.
 */
export function useRunAiTask(noteId: string, enabled = true) {
  const t = useTranslations('ai')
  const state = useQuery(AiStateDocument, { skip: !enabled, fetchPolicy: 'cache-and-network' })
  const [runTask, running] = useMutation(RunAiTaskDocument)
  const [error, setError] = useState<string | null>(null)
  const [limit, setLimit] = useState(false)
  const status = state.data?.aiStatus
  const allowance = state.data?.myAiAllowance
  const spent = allowance?.limitToday != null && allowance.usedToday >= allowance.limitToday
  const run = async (task: AiTask, lang: AiLanguage = 'ENGLISH', cardIds?: string[]) => {
    setError(null)
    setLimit(false)
    const { result, error } = await attempt(() =>
      runTask({
        variables: { input: { noteId, task, language: lang, ...(cardIds ? { cardIds } : {}) } },
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
    const hit = limitMessageFromUserErrors(payload?.userErrors) ?? refusalMessage(error)
    setLimit(!!hit)
    setError(hit ?? problemOf(error, payload, t('runFailed')))
    // The allowance changed, or AI turned out to be off: ask again.
    if (payload?.userErrors.length) void state.refetch()
  }
  /** Unknown (not answered yet, or failed) counts as off: no control is offered that cannot work. */
  const available = !!status?.available
  return { status, allowance, spent, off: status ? !status.available : false, available, run, running: running.loading, error, limit }
}

export function AiPanel({ noteId, open, onClose, canEdit, canFork, hasCode, onAddedToNote, onTextMended }: AiPanelProps) {
  const t = useTranslations('ai')
  const languageId = useId()
  const list = useQuery(NoteAiArtifactsDocument, { variables: { noteId }, skip: !open, fetchPolicy: 'cache-and-network' })
  const ai = useRunAiTask(noteId, open)
  const [language, setLanguage] = useState<AiLanguage>('HINDI')
  const { status, allowance, spent, off, run, error, limit } = ai
  const running = { loading: ai.running }
  const artifacts = list.data?.note?.aiArtifacts ?? []
  const tasks = TASKS.filter(({ task }) => (DERIVATIVE.has(task) ? canFork : task === 'EXPLAIN_CODE' ? hasCode !== false : EDITORS_ONLY.has(task) ? canEdit : true))
  // Its recordings, each transcribed on its own (ADR-0062).
  const recordings = (list.data?.note?.cards.edges ?? []).map((e) => e.node).filter((c) => c.type === 'audio' || c.type === 'video')

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

        <section aria-label={t('askTitle')} className="flex flex-col gap-3">
          <AskForm scope="THIS_NOTE" noteId={noteId} compact offNotice={false} />
          <AnswerList noteId={noteId} compact />
        </section>

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
          {recordings.map((r, i) => (
            <button
              key={r.id}
              type="button"
              disabled={off || spent || running.loading}
              onClick={() => void run('TRANSCRIBE', 'ENGLISH', [r.id])}
              className="flex items-center gap-2 rounded-xl border border-border bg-surface p-3 text-left transition hover:border-accent hover:bg-accent-soft disabled:pointer-events-none disabled:opacity-50"
            >
              <Mic className="size-4 shrink-0 text-accent" aria-hidden />
              <span className="flex flex-col">
                <span className="text-sm font-semibold">{recordings.length === 1 ? t('transcribeOne') : t('transcribeN', { n: i + 1 })}</span>
                <span className="text-xs leading-snug text-muted">{t('hint.TRANSCRIBE')}</span>
              </span>
            </button>
          ))}
          <div className="flex items-center gap-2 rounded-xl border border-border bg-surface p-2 pl-3">
            <Languages className="size-4 shrink-0 text-accent" aria-hidden />
            <label htmlFor={languageId} className="text-sm font-semibold">
              {t('translateInto')}
            </label>
            <select id={languageId} value={language} onChange={(e) => setLanguage(e.target.value as AiLanguage)} className="h-9 min-w-0 flex-1 rounded-lg border border-border bg-bg px-2 text-sm">
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
            limit ? <LimitNotice>{error}</LimitNotice> : (
              <p role="alert" className="text-sm text-red-600 dark:text-red-400">
                {error}
              </p>
            )
          ) : null}
        </section>

        <section aria-label={t('results')} className="flex flex-col gap-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-muted">{t('results')}</h3>
          {list.loading && !list.data ? <p className="text-sm text-muted">{t('loading')}</p> : null}
          {list.data && !artifacts.length ? <p className="text-sm text-muted">{t('noResults')}</p> : null}
          {artifacts.map((a) => (
            <AiResult key={a.id} noteId={noteId} artifact={a} canEdit={canEdit} onRetry={() => void run(a.task, a.language)} onAddedToNote={onAddedToNote} onTextMended={onTextMended} />
          ))}
        </section>
      </div>
    </Dialog>
  )
}

export function Allowance({ used, limit, resetsAt }: { used: number; limit: number | null; resetsAt: string }) {
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

export function AiResult({ noteId, artifact: a, canEdit, onRetry, onAddedToNote, onTextMended }: { noteId: string; artifact: Artifact; canEdit: boolean; onRetry: () => void; onAddedToNote?: () => void; onTextMended?: AiPanelProps['onTextMended'] }) {
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
      {a.status === 'READY' && a.changes ? <ApplyChanges artifact={a} onChanged={onTextMended} /> : null}
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

/**
 * Clean-up's changes (ADR-0063): each card's words before and after, chosen by default, applied through the normal
 * save. A card edited since keeps its words, and the person is told.
 */
function ApplyChanges({ artifact: a, onChanged }: { artifact: Artifact; onChanged?: AiPanelProps['onTextMended'] }) {
  const t = useTranslations('ai.cleanUp')
  const changes = a.changes ?? []
  const open = changes.filter((c) => !c.applied)
  const [chosen, setChosen] = useState<ReadonlySet<string>>(() => new Set(open.map((c) => c.cardId)))
  const [apply, applying] = useMutation(ApplyAiChangesDocument)
  const [outcome, setOutcome] = useState<{ applied: number; refused: number } | null>(null)
  const [error, setError] = useState<string | null>(null)

  if (!changes.length) return <p className="text-sm text-muted">{t('nothing')}</p>

  const toggle = (id: string) =>
    setChosen((s) => {
      const next = new Set(s)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  const save = async () => {
    setError(null)
    setOutcome(null)
    const cardIds = open.filter((c) => chosen.has(c.cardId)).map((c) => c.cardId)
    const { result, error } = await attempt(() =>
      apply({
        variables: { input: { artifactId: a.id, cardIds } },
        update(cache, { data }) {
          const applied = data?.applyAiChanges.applied ?? []
          if (!applied.length) return
          cache.modify({
            id: cache.identify({ __typename: 'AiArtifact', id: a.id }),
            fields: {
              changes: (existing) => (Array.isArray(existing) ? existing.map((c: { cardId: string; applied: boolean }) => (applied.includes(c.cardId) ? { ...c, applied: true } : c)) : existing),
              keptAt: () => new Date().toISOString(),
            },
          })
        },
      }),
    )
    const payload = result?.data?.applyAiChanges
    if (payload && !payload.userErrors.length) {
      // What was sent is settled: applied, or refused for a card edited since (sending it again changes nothing).
      setChosen((s) => new Set([...s].filter((id) => !cardIds.includes(id))))
      const refused = cardIds.length - payload.applied.length
      setOutcome({ applied: payload.applied.length, refused })
      if (payload.applied.length) onChanged?.(payload.applied.length, refused)
    }
    setError(problemOf(error, payload, t('failed')))
  }

  return (
    <div className="flex flex-col gap-3">
      <p className="text-xs text-muted">{t('lead')}</p>
      <ol className="flex flex-col gap-2">
        {changes.map((c, i) => (
          <li key={c.cardId} className={cn('flex gap-3 rounded-xl border p-3 transition', c.applied || chosen.has(c.cardId) ? 'border-accent/40 bg-bg' : 'border-border bg-surface-2 opacity-60')}>
            {c.applied ? (
              <Check className="mt-1 size-4 shrink-0 text-accent" aria-label={t('applied')} />
            ) : (
              <input type="checkbox" checked={chosen.has(c.cardId)} onChange={() => toggle(c.cardId)} aria-label={t('pick', { n: i + 1 })} className="mt-1 size-4 shrink-0 accent-[var(--accent)]" />
            )}
            <div className="flex min-w-0 flex-1 flex-col gap-1 text-sm">
              <p className="whitespace-pre-wrap break-words text-muted line-through decoration-red-500/60">
                <span className="sr-only">{t('before')}: </span>
                {c.before}
              </p>
              <p className="whitespace-pre-wrap break-words">
                <span className="sr-only">{t('after')}: </span>
                {c.after}
              </p>
            </div>
          </li>
        ))}
      </ol>
      {open.length ? (
        <div className="flex flex-wrap gap-2">
          <Button size="sm" className="gap-1.5" disabled={!open.some((c) => chosen.has(c.cardId)) || applying.loading} onClick={() => void save()}>
            <SpellCheck className="size-4" aria-hidden />
            {t('apply', { n: open.filter((c) => chosen.has(c.cardId)).length })}
          </Button>
        </div>
      ) : null}
      {outcome ? (
        <p role="status" className="text-sm font-medium text-accent">
          {t('done', { n: outcome.applied })}
          {outcome.refused ? ` ${t('refused', { n: outcome.refused })}` : ''}
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

/** The account page's view of AI (P5b): whether it answers, and how much of today's allowance is used. */
export function AiAccountSection({ className }: { className?: string }) {
  const t = useTranslations('ai')
  const { data } = useQuery(AiStateDocument, { fetchPolicy: 'cache-and-network' })
  if (!data) return null
  const { aiStatus: status, myAiAllowance: allowance } = data
  return (
    <section className={className} aria-labelledby="ai-allowance">
      <h2 id="ai-allowance" className="flex items-center gap-2 text-lg font-semibold">
        <Sparkles className="size-4 text-accent" aria-hidden />
        {t('account.title')}
      </h2>
      <p className="text-sm text-muted">{t('account.lead')}</p>
      {status.available ? <Allowance used={allowance.usedToday} limit={allowance.limitToday} resetsAt={allowance.resetsAt} /> : <p className="text-sm">{t(`unavailable.${status.reason ?? 'NOT_CONFIGURED'}`)}</p>}
    </section>
  )
}
