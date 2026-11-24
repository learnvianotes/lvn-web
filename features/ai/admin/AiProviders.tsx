'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { modelsForUse, pickerModels, presetsAsModels, routeModelUse, type ListedModel } from '@/features/ai/admin/catalog'
import { ModelSelect } from '@/features/ai/admin/ModelSelect'
import type { AiModelUse } from '@/graphql/generated/graphql'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import {
  AiConnectionModelsDocument,
  AiSettingsDocument,
  DeleteAiConnectionDocument,
  DeleteAiTaskRouteDocument,
  SaveAiConnectionDocument,
  SaveAiTaskRouteDocument,
  SetAiDefaultsDocument,
  TestAiConnectionDocument,
  type AiProviderKind,
  type AiSettingsFieldsFragment,
} from '@/graphql/generated/graphql'

type Settings = AiSettingsFieldsFragment
type Connection = Settings['connections'][number]
type Preset = Settings['presets'][number]
type Test = { ok: boolean; message: string; latencyMs: number; models: string[] }

const SELECT = 'h-11 w-full min-w-0 max-w-full rounded-xl border border-border bg-surface px-3 text-[15px] text-fg'
/** Prices travel as millionths of a dollar per million tokens; people read and write dollars per million tokens. */
const toDollars = (micro: number) => (micro ? String(micro / 1_000_000) : '')
const toMicro = (dollars: string) => (dollars.trim() ? Math.round(Number(dollars) * 1_000_000) : 0)

/**
 * Models a saved connection's account lists (lvn-backend Query.aiConnectionModels): all of them, and one picker per use.
 * Asked once per connection and kept for the visit; nothing is asked for a connection not saved yet.
 */
function useAccountCatalog(connectionId: string | null | undefined) {
  const { data, loading } = useQuery(AiConnectionModelsDocument, { variables: { input: { id: connectionId ?? '' } }, skip: !connectionId, fetchPolicy: 'cache-first' })
  return { catalog: data?.aiConnectionModels ?? null, loading: !!connectionId && !data && loading }
}

/** Account picker when the catalog has arrived; preset names until then. Null while the catalog is loading. */
function modelsFor(catalog: { pickers: { use: AiModelUse; models: ListedModel[] }[] } | null, loading: boolean, use: AiModelUse, presets: readonly string[]): ListedModel[] | null {
  if (catalog) return modelsForUse(catalog.pickers, use)
  if (loading) return null
  return presetsAsModels(presets, use)
}

/**
 * The AI providers page (lvn-backend ADR-0065), for platform admins: connections to Claude, ChatGPT, Gemini, an
 * OpenAI-compatible server (a LiteLLM proxy, OpenRouter, vLLM…) or an Ollama, each tested in one click; who answers
 * chats and makes embeddings by default; and tasks sent elsewhere. Keys go in and are never shown again.
 */
export function AiProviders() {
  const t = useTranslations('aiAdmin')
  const format = useFormatter()
  const client = useApolloClient()
  const { data, error } = useQuery(AiSettingsDocument, { fetchPolicy: 'cache-and-network' })
  const [editing, setEditing] = useState<{ kind: AiProviderKind; connection: Connection | null } | null>(null)
  const [tests, setTests] = useState<Record<string, Test | 'running'>>({})
  const [problem, setProblem] = useState<string | null>(null)
  const [testConnection] = useMutation(TestAiConnectionDocument)
  const [deleteConnection] = useMutation(DeleteAiConnectionDocument)
  const [setDefaults, settingDefaults] = useMutation(SetAiDefaultsDocument)
  const [saveConnection, allowing] = useMutation(SaveAiConnectionDocument)

  if (CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')) return <p className="text-muted">{t('notAllowed')}</p>
  const s = data?.aiSettings
  if (!s) return error ? <Alert tone="error">{t('failed')}</Alert> : <p className="text-muted">{t('loading')}</p>

  const show = (next: Settings | null | undefined, userError?: string) => {
    if (userError) setProblem(userError)
    else if (next) {
      setProblem(null)
      client.writeQuery({ query: AiSettingsDocument, data: { aiSettings: next } })
    }
  }
  const presetOf = (kind: AiProviderKind) => s.presets.find((p) => p.kind === kind)!
  const nameOf = (id: string | null, which: 'chat' | 'embed') => {
    const c = id ? s.connections.find((x) => x.id === id) : null
    if (c) return `${c.label} · ${(which === 'chat' ? c.chatModel : c.embedModel) ?? '—'}`
    const model = which === 'chat' ? s.environment.chatModel : s.environment.embedModel
    return s.environment.kind && model ? t('environmentNamed', { model }) : t('nobody')
  }
  const test = async (id: string) => {
    setTests((all) => ({ ...all, [id]: 'running' }))
    const res = await testConnection({ variables: { input: { id } } }).catch(() => null)
    const result = res?.data?.testAiConnection.test
    setTests((all) => ({ ...all, [id]: result ?? { ok: false, message: res?.data?.testAiConnection.userErrors[0]?.message ?? t('failed'), latencyMs: 0, models: [] } }))
  }
  const remove = async (c: Connection) => {
    if (!window.confirm(t('confirmDelete', { name: c.label }))) return
    const res = await deleteConnection({ variables: { input: { id: c.id } } }).catch((e: unknown) => failure(e))
    if (res) show(res.data?.deleteAiConnection.settings, res.data?.deleteAiConnection.userErrors[0]?.message)
  }
  const choose = async (input: { chatConnectionId: string | null; embedConnectionId: string | null }) => {
    const res = await setDefaults({ variables: { input } }).catch((e: unknown) => failure(e))
    if (res) show(res.data?.setAiDefaults.settings, res.data?.setAiDefaults.userErrors[0]?.message)
  }
  /**
   * Connections that answer something here but may not see private notes: with one of them choosing, an owner's AI on
   * their own private note says "AI cannot work on private notes here." (ADR-0065). Saying so is the fix the admin can act on.
   */
  const inUse = new Set([s.chatConnectionId, s.embedConnectionId, ...s.routes.map((r) => r.connectionId)].filter(Boolean))
  const closed = s.connections.filter((c) => c.enabled && !c.mayReceivePrivate && inUse.has(c.id))
  const allowPrivate = async (c: Connection) => {
    if (!window.confirm(t('confirmPrivate', { name: c.label }))) return
    // Everything as it is, with private notes allowed; an empty key keeps the saved one.
    const input = {
      id: c.id,
      kind: c.kind,
      label: c.label,
      baseUrl: c.baseUrl ?? null,
      apiKey: null,
      clearApiKey: false,
      chatModel: c.chatModel ?? null,
      embedModel: c.embedModel ?? null,
      inputMicroUsdPerMTok: c.inputMicroUsdPerMTok,
      outputMicroUsdPerMTok: c.outputMicroUsdPerMTok,
      embedMicroUsdPerMTok: c.embedMicroUsdPerMTok,
      mayReceivePrivate: true,
      enabled: c.enabled,
    }
    const res = await saveConnection({ variables: { input } }).catch((e: unknown) => failure(e))
    if (!res) return
    const userError = res.data?.saveAiConnection.userErrors[0]?.message
    if (userError) return setProblem(userError)
    setProblem(null)
    void client.refetchQueries({ include: [AiSettingsDocument] })
  }
  /** A request that failed outright (offline, a server error): say so instead of doing nothing. */
  const failure = (e: unknown) => {
    setProblem(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    return null
  }

  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>

      {!s.keysCanBeSaved ? <Alert tone="error">{t('noSecret')}</Alert> : null}
      {problem ? <Alert tone="error">{problem}</Alert> : null}
      {closed.length ? (
        <section aria-labelledby="ai-private" className="flex flex-col gap-2 rounded-2xl border border-accent/30 bg-accent-soft p-4 text-sm">
          <h2 id="ai-private" className="font-semibold">{t('privateBlockedTitle')}</h2>
          <p>{t('privateBlocked', { names: closed.map((c) => c.label).join(', ') })}</p>
          <p className="text-muted">{t('privateBlockedHow')}</p>
          <div className="flex flex-wrap gap-2">
            {closed.map((c) => (
              <Button key={c.id} size="sm" variant="secondary" disabled={allowing.loading} onClick={() => void allowPrivate(c)}>
                {t('allowPrivate', { name: c.label })}
              </Button>
            ))}
          </div>
        </section>
      ) : null}

      <section aria-labelledby="ai-now" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
        <h2 id="ai-now" className="text-lg font-semibold">{t('whoAnswers')}</h2>
        <div className="grid gap-4 sm:grid-cols-2 sm:[&>*]:min-w-0">
          <Field label={t('chats')} hint={t('chatsHint')}>
            <select className={SELECT} value={s.chatConnectionId ?? ''} disabled={settingDefaults.loading} onChange={(e) => void choose({ chatConnectionId: e.target.value || null, embedConnectionId: s.embedConnectionId ?? null })}>
              <option value="">{nameOf(null, 'chat')}</option>
              {s.connections.filter((c) => c.chatModel).map((c) => (
                <option key={c.id} value={c.id}>{nameOf(c.id, 'chat')}{c.enabled ? '' : ` (${t('off')})`}</option>
              ))}
            </select>
          </Field>
          <Field label={t('embeddings')} hint={t('embeddingsHint')}>
            <select className={SELECT} value={s.embedConnectionId ?? ''} disabled={settingDefaults.loading} onChange={(e) => void choose({ chatConnectionId: s.chatConnectionId ?? null, embedConnectionId: e.target.value || null })}>
              <option value="">{nameOf(null, 'embed')}</option>
              {s.connections.filter((c) => c.embedModel).map((c) => (
                <option key={c.id} value={c.id}>{nameOf(c.id, 'embed')}{c.enabled ? '' : ` (${t('off')})`}</option>
              ))}
            </select>
          </Field>
        </div>
        <p className="text-sm text-muted">
          {s.monthlyBudgetMicroUsd !== null && s.monthlyBudgetMicroUsd !== undefined
            ? t('spentOf', { spent: format.number(s.spentThisMonthMicroUsd / 1_000_000, { style: 'currency', currency: 'USD' }), budget: format.number(s.monthlyBudgetMicroUsd / 1_000_000, { style: 'currency', currency: 'USD' }) })
            : t('spent', { spent: format.number(s.spentThisMonthMicroUsd / 1_000_000, { style: 'currency', currency: 'USD' }) })}
        </p>
      </section>

      <section aria-labelledby="ai-connections" className="flex flex-col gap-3">
        <h2 id="ai-connections" className="text-lg font-semibold">{t('connections')}</h2>
        {s.connections.length ? null : <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noConnections')}</p>}
        <ul className="flex flex-col gap-3">
          {s.connections.map((c) => {
            const result = tests[c.id]
            return (
              <li key={c.id}>
                <article aria-label={c.label} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-semibold">{c.label}</h3>
                    <span className="text-sm text-muted">{presetOf(c.kind).name}</span>
                    {s.chatConnectionId === c.id ? <Badge>{t('defaultChats')}</Badge> : null}
                    {s.embedConnectionId === c.id ? <Badge>{t('defaultEmbeddings')}</Badge> : null}
                    {c.enabled ? null : <Badge muted>{t('off')}</Badge>}
                    {c.mayReceivePrivate ? <Badge muted>{t('privateOk')}</Badge> : null}
                  </div>
                  <dl className="grid gap-x-4 gap-y-1 text-sm sm:grid-cols-2">
                    <Row term={t('chatModel')} value={c.chatModel ?? '—'} />
                    <Row term={t('embedModel')} value={c.embedModel ?? '—'} />
                    <Row term={t('address')} value={c.baseUrl ?? presetOf(c.kind).defaultBaseUrl ?? '—'} />
                    <Row term={t('key')} value={c.hasKey ? t('keySaved', { hint: c.keyHint ?? '' }) : t('noKey')} />
                  </dl>
                  {result && result !== 'running' ? (
                    <Alert tone={result.ok ? 'success' : 'error'}>
                      <p>{result.message}</p>
                      {result.models.length ? (
                        <details className="mt-1 text-xs">
                          <summary className="cursor-pointer opacity-80">{t('modelsListed', { count: result.models.length })}</summary>
                          <ul aria-label={t('modelsListLabel', { name: c.label })} className="mt-1 max-h-60 overflow-y-auto rounded-lg border border-border bg-surface px-3 py-2 font-mono text-fg">
                            {result.models.map((m) => (
                              <li key={m} className="break-all">{m}</li>
                            ))}
                          </ul>
                        </details>
                      ) : null}
                    </Alert>
                  ) : null}
                  <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap">
                    <Button size="sm" variant="secondary" className="h-11 w-full sm:w-auto" disabled={result === 'running'} onClick={() => void test(c.id)}>
                      {result === 'running' ? t('testing') : t('test')}
                    </Button>
                    <Button size="sm" variant="secondary" className="h-11 w-full sm:w-auto" onClick={() => setEditing({ kind: c.kind, connection: c })} aria-label={t('editNamed', { name: c.label })}>
                      {t('edit')}
                    </Button>
                    <Button size="sm" variant="ghost" className="h-11 w-full sm:w-auto" onClick={() => void remove(c)} aria-label={t('deleteNamed', { name: c.label })}>
                      {t('delete')}
                    </Button>
                  </div>
                </article>
              </li>
            )
          })}
        </ul>
        <div className="flex flex-col gap-2">
          <p className="text-sm font-medium">{t('add')}</p>
          <div className="flex flex-wrap gap-2">
            {s.presets.map((p) => (
              <Button key={p.kind} size="sm" variant="secondary" className="h-auto min-h-11 max-w-full whitespace-normal py-2 text-left" onClick={() => setEditing({ kind: p.kind, connection: null })}>
                {p.name}
              </Button>
            ))}
          </div>
        </div>
      </section>

      <Routes settings={s} onSaved={show} onFailed={failure} />

      {editing ? (
        <ConnectionDialog
          preset={presetOf(editing.kind)}
          connection={editing.connection}
          keysCanBeSaved={s.keysCanBeSaved}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null)
            void client.refetchQueries({ include: [AiSettingsDocument] })
          }}
        />
      ) : null}
    </div>
  )
}

function Badge({ children, muted }: { children: React.ReactNode; muted?: boolean }) {
  return <span className={muted ? 'rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted' : 'rounded-[10px] bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent'}>{children}</span>
}

function Row({ term, value }: { term: string; value: string }) {
  return (
    <div className="flex min-w-0 gap-2">
      <dt className="shrink-0 text-muted">{term}</dt>
      <dd className="min-w-0 break-all">{value}</dd>
    </div>
  )
}

/** Adding or changing one connection; the key field is write-only. */
function ConnectionDialog({ preset, connection: c, keysCanBeSaved, onClose, onSaved }: { preset: Preset; connection: Connection | null; keysCanBeSaved: boolean; onClose: () => void; onSaved: () => void }) {
  const t = useTranslations('aiAdmin')
  const account = useAccountCatalog(c?.id)
  const chatModels = modelsFor(account.catalog, account.loading, 'CHAT', preset.chatModels)
  const embedModels = modelsFor(account.catalog, account.loading, 'EMBEDDING', preset.embedModels)
  const [save, saving] = useMutation(SaveAiConnectionDocument)
  const [form, setForm] = useState({
    label: c?.label ?? preset.name.split(' (')[0]!,
    baseUrl: c?.baseUrl ?? '',
    apiKey: '',
    clearApiKey: false,
    chatModel: c?.chatModel ?? preset.chatModels[0] ?? '',
    embedModel: c?.embedModel ?? '',
    input: toDollars(c?.inputMicroUsdPerMTok ?? 0),
    output: toDollars(c?.outputMicroUsdPerMTok ?? 0),
    embed: toDollars(c?.embedMicroUsdPerMTok ?? 0),
    mayReceivePrivate: c?.mayReceivePrivate ?? preset.privateByDefault,
    enabled: c?.enabled ?? true,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const set = (patch: Partial<typeof form>) => setForm((f) => ({ ...f, ...patch }))
  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrors({})
    for (const [field, value] of [['input', form.input], ['output', form.output], ['embed', form.embed]] as const) if (value.trim() && !(Number(value) >= 0)) return setErrors({ [field]: t('badPrice') })
    try {
      const res = await save({
        variables: {
          input: {
            id: c?.id ?? null,
            kind: preset.kind,
            label: form.label,
            baseUrl: form.baseUrl.trim() || null,
            apiKey: form.apiKey.trim() || null,
            clearApiKey: form.clearApiKey,
            chatModel: form.chatModel.trim() || null,
            embedModel: preset.canEmbed ? form.embedModel.trim() || null : null,
            inputMicroUsdPerMTok: toMicro(form.input),
            outputMicroUsdPerMTok: toMicro(form.output),
            embedMicroUsdPerMTok: preset.canEmbed ? toMicro(form.embed) : 0,
            mayReceivePrivate: form.mayReceivePrivate,
            enabled: form.enabled,
          },
        },
      })
      const problem = res.data?.saveAiConnection.userErrors[0]
      if (problem) return setErrors({ [problem.field?.at(-1) ?? 'form']: problem.message })
      onSaved()
    } catch (err) {
      setErrors({ form: CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed') })
    }
  }
  const listNote = !c ? t('modelsAfterSave') : account.loading ? t('modelsLoading') : null
  return (
    <Dialog open onClose={onClose} title={c ? t('editTitle', { name: c.label }) : t('addTitle', { name: preset.name })} wide sheet>
      <form onSubmit={(e) => void submit(e)} className="flex flex-col gap-4">
        {errors.form ? <Alert tone="error">{errors.form}</Alert> : null}
        <div className="grid gap-4 sm:grid-cols-2 sm:[&>*]:min-w-0">
          <Field label={t('name')} error={errors.label}>
            <Input value={form.label} maxLength={60} onChange={(e) => set({ label: e.target.value })} required />
          </Field>
          <Field label={t('address')} error={errors.baseUrl} hint={preset.defaultBaseUrl ? t('addressDefault', { url: preset.defaultBaseUrl }) : t('addressNeeded')}>
            <Input value={form.baseUrl} inputMode="url" placeholder={preset.defaultBaseUrl ?? (preset.kind === 'OLLAMA' ? 'http://gpu-host:11434' : 'http://litellm:4000/v1')} onChange={(e) => set({ baseUrl: e.target.value })} />
          </Field>
        </div>
        <Field label={t('apiKey')} error={errors.apiKey} hint={!keysCanBeSaved ? t('noSecretShort') : c?.hasKey ? t('apiKeyKeep', { hint: c.keyHint ?? '' }) : preset.needsKey ? t('apiKeyNeeded') : t('apiKeyOptional')}>
          <Input type="password" autoComplete="off" value={form.apiKey} disabled={!keysCanBeSaved || form.clearApiKey} onChange={(e) => set({ apiKey: e.target.value })} />
        </Field>
        {c?.hasKey ? (
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.clearApiKey} onChange={(e) => set({ clearApiKey: e.target.checked, apiKey: '' })} className="size-4 accent-[var(--accent)]" />
            {t('clearKey')}
          </label>
        ) : null}
        {listNote ? <p className="text-sm text-muted" role="status">{listNote}</p> : null}
        <div className="grid gap-4 sm:grid-cols-2 sm:[&>*]:min-w-0">
          <ModelControl
            label={t('chatModel')}
            error={errors.chatModel}
            hint={modelHint(t, chatModels, Boolean(account.catalog), t('chatModelHint'))}
            models={chatModels}
            value={form.chatModel}
            onChange={(chatModel) => set({ chatModel })}
            searchLabel={t('searchModels', { use: t('uses.CHAT') })}
            typed
          />
          {preset.canEmbed ? (
            pickerModels(embedModels) || !account.catalog ? (
              <ModelControl
                label={t('embedModel')}
                error={errors.embedModel}
                hint={modelHint(t, embedModels, Boolean(account.catalog), t('embedModelHint'))}
                models={embedModels}
                value={form.embedModel}
                onChange={(embedModel) => set({ embedModel })}
                searchLabel={t('searchModels', { use: t('uses.EMBEDDING') })}
                allowEmpty
                typed
              />
            ) : (
              <p className="self-end text-sm text-muted">{t('noEmbeddingModels')}</p>
            )
          ) : (
            <p className="self-end text-sm text-muted">{t('noEmbeddings', { name: preset.name })}</p>
          )}
        </div>
        {account.catalog && account.catalog.all.length ? (
          <details>
            <summary className="cursor-pointer text-sm text-muted">{t('allModels', { count: account.catalog.all.length })}</summary>
            <ul aria-label={t('allModelsList', { name: c?.label ?? preset.name })} className="mt-2 max-h-60 overflow-y-auto rounded-lg border border-border bg-surface px-3 py-2 font-mono text-xs">
              {[...account.catalog.all].sort((a, b) => a.kind.localeCompare(b.kind) || a.id.localeCompare(b.id)).map((model) => (
                <li key={model.id} className="break-all">
                  {model.id} · {t(`kinds.${model.kind}`)} · {model.supports.map((use) => t(`uses.${use}`)).join(', ')}
                </li>
              ))}
            </ul>
          </details>
        ) : null}
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-2 text-sm font-medium">{t('prices')}</legend>
          <div className="grid gap-4 sm:grid-cols-2 sm:[&>*]:min-w-0 lg:grid-cols-3">
            <Field label={t('priceInput')} error={errors.input ?? errors.inputMicroUsdPerMTok}>
              <Input inputMode="decimal" value={form.input} placeholder="0" onChange={(e) => set({ input: e.target.value })} />
            </Field>
            <Field label={t('priceOutput')} error={errors.output ?? errors.outputMicroUsdPerMTok}>
              <Input inputMode="decimal" value={form.output} placeholder="0" onChange={(e) => set({ output: e.target.value })} />
            </Field>
            {preset.canEmbed ? (
              <Field label={t('priceEmbed')} error={errors.embed ?? errors.embedMicroUsdPerMTok}>
                <Input inputMode="decimal" value={form.embed} placeholder="0" onChange={(e) => set({ embed: e.target.value })} />
              </Field>
            ) : null}
          </div>
        </fieldset>
        <label className="flex items-start gap-2 text-sm">
          <input type="checkbox" checked={form.mayReceivePrivate} onChange={(e) => set({ mayReceivePrivate: e.target.checked })} className="mt-0.5 size-4 shrink-0 accent-[var(--accent)]" />
          <span>
            <span className="font-medium">{t('privateLabel')}</span>
            <span className="block text-muted">{t('privateHint')}</span>
          </span>
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={form.enabled} onChange={(e) => set({ enabled: e.target.checked })} className="size-4 accent-[var(--accent)]" />
          {t('enabled')}
        </label>
        {/* Kept in sight on a phone, where the form is longer than the screen. */}
        <div className="sticky -bottom-4 -mx-4 -mb-4 flex flex-col-reverse gap-2 border-t border-border bg-bg px-4 py-3 sm:-mx-5 sm:flex-row sm:justify-end sm:px-5">
          <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button type="submit" className="h-11 w-full sm:w-auto" disabled={saving.loading}>
            {saving.loading ? t('saving') : t('save')}
          </Button>
        </div>
      </form>
    </Dialog>
  )
}

/** A picker bound to one use, or a text field when that picker is empty (a provider that lists nothing). */
function ModelControl({ label, hint, error, models, value, onChange, searchLabel, allowEmpty, typed, required }: { label: string; hint?: string; error?: string; models: ListedModel[] | null; value: string; onChange: (value: string) => void; searchLabel: string; allowEmpty?: boolean; typed?: boolean; required?: boolean }) {
  const offered = pickerModels(models)
  if (models === null) {
    return (
      <Field label={label} hint={hint} error={error}>
        <Input value={value} disabled onChange={() => undefined} />
      </Field>
    )
  }
  if (offered) return <ModelSelect label={label} hint={hint} error={error} models={offered} value={value} onChange={onChange} searchLabel={searchLabel} allowEmpty={allowEmpty} required={required} />
  if (!typed) return null
  return (
    <Field label={label} hint={hint} error={error}>
      <Input value={value} required={required} autoComplete="off" onChange={(e) => onChange(e.target.value)} />
    </Field>
  )
}

function modelHint(t: ReturnType<typeof useTranslations<'aiAdmin'>>, models: ListedModel[] | null, fromAccount: boolean, fallback: string): string {
  if (models === null) return t('modelsLoading')
  if (fromAccount && models.length === 0) return t('typeModel')
  if (fromAccount) return t('modelsForUse', { count: models.length })
  return fallback
}

/** Tasks sent to another connection or model than the default: transcription to Gemini, say. */
function Routes({ settings: s, onSaved, onFailed }: { settings: Settings; onSaved: (next: Settings | null | undefined, problem?: string) => void; onFailed: (e: unknown) => null }) {
  const t = useTranslations('aiAdmin')
  const [saveRoute, saving] = useMutation(SaveAiTaskRouteDocument)
  const [deleteRoute] = useMutation(DeleteAiTaskRouteDocument)
  const [form, setForm] = useState({ task: '', connectionId: '', model: '', input: '', output: '' })
  const labelOf = (id: string | null | undefined) => (id ? (s.connections.find((c) => c.id === id)?.label ?? '—') : t('theDefault'))
  // The models of the connection the task goes to: the chosen one, else the default for chats or for embeddings.
  const via = s.connections.find((c) => c.id === (form.connectionId || (form.task === 'EMBED' ? s.embedConnectionId : s.chatConnectionId)))
  const account = useAccountCatalog(via?.id)
  const viaPreset = via ? s.presets.find((p) => p.kind === via.kind) : undefined
  const use = routeModelUse(form.task)
  const presetIds = use === 'EMBEDDING' ? viaPreset?.embedModels : use === 'CHAT' ? viaPreset?.chatModels : []
  const routeModels = modelsFor(account.catalog, account.loading, use, presetIds ?? [])
  const add = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.model.trim()) return
    const res = await saveRoute({ variables: { input: { task: form.task, connectionId: form.connectionId || null, model: form.model, inputMicroUsdPerMTok: toMicro(form.input), outputMicroUsdPerMTok: toMicro(form.output) } } }).catch(onFailed)
    if (!res) return
    const problem = res.data?.saveAiTaskRoute.userErrors[0]?.message
    onSaved(res.data?.saveAiTaskRoute.settings, problem)
    if (!problem) setForm({ task: '', connectionId: '', model: '', input: '', output: '' })
  }
  return (
    <section aria-labelledby="ai-routes" className="flex flex-col gap-3">
      <h2 id="ai-routes" className="text-lg font-semibold">{t('routes')}</h2>
      <p className="text-sm text-muted">{t('routesLead')}</p>
      {s.routes.length ? (
        <ul className="flex flex-col divide-y divide-border rounded-2xl border border-border bg-surface">
          {s.routes.map((r) => (
            <li key={r.task} className="flex flex-col gap-2 px-4 py-3 text-sm sm:flex-row sm:flex-wrap sm:items-center">
              <span className="font-mono text-xs">{r.task}</span>
              <span aria-hidden className="hidden sm:inline">→</span>
              <span className="min-w-0 break-all">{labelOf(r.connectionId)} · {r.model}</span>
              <Button
                size="sm"
                variant="ghost"
                className="h-11 w-full sm:ml-auto sm:w-auto"
                aria-label={t('removeRoute', { task: r.task })}
                onClick={async () => {
                  const res = await deleteRoute({ variables: { input: { task: r.task } } }).catch(onFailed)
                  if (res) onSaved(res.data?.deleteAiTaskRoute.settings, res.data?.deleteAiTaskRoute.userErrors[0]?.message)
                }}
              >
                {t('remove')}
              </Button>
            </li>
          ))}
        </ul>
      ) : null}
      <form onSubmit={(e) => void add(e)} className="grid gap-3 rounded-2xl border border-border bg-surface p-4 sm:grid-cols-2 sm:[&>*]:min-w-0">
        <Field label={t('task')}>
          <select className={SELECT} value={form.task} required onChange={(e) => setForm((f) => ({ ...f, task: e.target.value }))}>
            <option value="" disabled>
              {t('chooseTask')}
            </option>
            {s.tasks.map((task) => (
              <option key={task} value={task}>{task}</option>
            ))}
          </select>
        </Field>
        <Field label={t('connection')}>
          <select className={SELECT} value={form.connectionId} onChange={(e) => setForm((f) => ({ ...f, connectionId: e.target.value }))}>
            <option value="">{t('theDefault')}</option>
            {s.connections.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
        </Field>
        <div className="sm:col-span-2">
          <ModelControl
            label={t('model')}
            hint={via ? modelHint(t, routeModels, Boolean(account.catalog), '') : undefined}
            models={routeModels}
            value={form.model}
            onChange={(model) => setForm((f) => ({ ...f, model }))}
            searchLabel={t('searchModels', { use: t(`uses.${use}`) })}
            typed
            required
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Field label={t('priceInput')}>
            <Input inputMode="decimal" value={form.input} placeholder="0" onChange={(e) => setForm((f) => ({ ...f, input: e.target.value }))} />
          </Field>
          <Field label={t('priceOutput')}>
            <Input inputMode="decimal" value={form.output} placeholder="0" onChange={(e) => setForm((f) => ({ ...f, output: e.target.value }))} />
          </Field>
        </div>
        <div className="sm:col-span-2">
          <Button type="submit" variant="secondary" disabled={saving.loading}>
            {t('addRoute')}
          </Button>
        </div>
      </form>
    </section>
  )
}
