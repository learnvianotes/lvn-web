import { expect, test, type Route } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * The AI providers page (lvn-backend ADR-0065): a platform admin adds Claude with its key (never shown again), tests
 * it, makes it answer chats, sends transcription elsewhere, and deletes a connection; others are turned away; a server
 * without AI_KEYS_SECRET says keys cannot be saved.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const CLAUDE = '01920000-0000-7000-8000-0000000a1c01'
const GEMINI = '01920000-0000-7000-8000-0000000a1c02'
const none = { userErrors: [] }
const preset = (kind: string, name: string, over: Record<string, unknown> = {}) => ({ __typename: 'AiProviderPreset', kind, name, defaultBaseUrl: null, needsKey: true, canEmbed: true, canHear: true, privateByDefault: false, chatModels: [], embedModels: [], ...over })
const presets = [
  preset('ANTHROPIC', 'Claude (Anthropic)', { defaultBaseUrl: 'https://api.anthropic.com', canEmbed: false, canHear: false, chatModels: ['claude-sonnet-5-5', 'claude-haiku-5-5'] }),
  preset('OPENAI', 'ChatGPT (OpenAI)', { defaultBaseUrl: 'https://api.openai.com/v1', chatModels: ['gpt-5-mini'], embedModels: ['text-embedding-3-small'] }),
  preset('GEMINI', 'Gemini (Google)', { defaultBaseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai', chatModels: ['gemini-3.8-flash'], embedModels: ['gemini-embedding-001'] }),
  preset('OPENAI_COMPATIBLE', 'Custom (OpenAI-compatible: LiteLLM proxy, OpenRouter, vLLM…)', { needsKey: false }),
  preset('OLLAMA', 'Ollama', { needsKey: false, privateByDefault: true, chatModels: ['gemma4'], embedModels: ['embeddinggemma'] }),
]
// More models than any list used to show (it stopped at 12), as Anthropic's /v1/models gives them.
const CLAUDE_MODELS = Array.from({ length: 30 }, (_, i) => `claude-model-${String(i).padStart(2, '0')}`)
const listed = (id: string, kind: string, supports: string[]) => ({ __typename: 'AiListedModel', id, kind, supports })
const GEMINI_CHAT = [listed('gemini-2.5-pro', 'CHAT', ['CHAT']), listed('gemini-3.8-flash', 'CHAT', ['CHAT', 'TRANSCRIBE'])]
const GEMINI_EMBED = [listed('gemini-embedding-001', 'EMBEDDING', ['EMBEDDING']), listed('text-embedding-004', 'EMBEDDING', ['EMBEDDING'])]
const GEMINI_TTS = [listed('gemini-2.5-flash-tts', 'TTS', ['TTS'])]
const catalog = (all: ReturnType<typeof listed>[], pickers: [string, ReturnType<typeof listed>[]][]) => ({
  __typename: 'AiConnectionModels',
  all,
  pickers: pickers.map(([use, models]) => ({ __typename: 'AiModelPicker', use, models })),
})
const GEMINI_CATALOG = catalog([...GEMINI_CHAT, ...GEMINI_EMBED, ...GEMINI_TTS], [
  ['CHAT', GEMINI_CHAT],
  ['EMBEDDING', GEMINI_EMBED],
  ['TRANSCRIBE', [GEMINI_CHAT[1]!]],
  ['IMAGE', []],
  ['TTS', GEMINI_TTS],
  ['AUDIO', []],
  ['REALTIME', []],
  ['MODERATION', []],
])
const CLAUDE_LISTED = CLAUDE_MODELS.map((id) => listed(id, 'CHAT', ['CHAT']))
const CLAUDE_CATALOG = catalog(CLAUDE_LISTED, [
  ['CHAT', CLAUDE_LISTED],
  ['EMBEDDING', []],
  ['TRANSCRIBE', []],
  ['IMAGE', []],
  ['TTS', []],
  ['AUDIO', []],
  ['REALTIME', []],
  ['MODERATION', []],
])
const accountModels = (v: Record<string, unknown>) => ({ aiConnectionModels: (v.input as { id: string }).id === CLAUDE ? CLAUDE_CATALOG : GEMINI_CATALOG })
/** The values a model select offers, ignoring the empty "choose" row. */
const offered = (input: import('@playwright/test').Locator) => input.locator('option').evaluateAll((opts) => opts.map((o) => (o as HTMLOptionElement).value).filter(Boolean))
const connection = (over: Record<string, unknown>) => ({ __typename: 'AiConnection', baseUrl: null, hasKey: true, keyHint: null, mayReceivePrivate: false, enabled: true, chatModel: null, embedModel: null, inputMicroUsdPerMTok: 0, outputMicroUsdPerMTok: 0, embedMicroUsdPerMTok: 0, updatedAt: '2026-10-13T10:00:00.000Z', ...over })
const settings = (over: Record<string, unknown> = {}) => ({
  __typename: 'AiSettings',
  connections: [] as unknown[],
  chatConnectionId: null as string | null,
  embedConnectionId: null as string | null,
  environment: { __typename: 'AiEnvironmentProvider', kind: 'OLLAMA', chatModel: 'gemma4', embedModel: 'embeddinggemma' },
  routes: [] as unknown[],
  tasks: ['SUMMARIZE', 'QUIZ', 'TRANSCRIBE', 'ASK', 'EMBED'],
  presets,
  keysCanBeSaved: true,
  spentThisMonthMicroUsd: 1_250_000,
  monthlyBudgetMicroUsd: 50_000_000,
  ...over,
})

test('a platform admin adds Claude, tests it, makes it answer, sends transcription to Gemini and deletes a connection', async ({ page }) => {
  const state = settings({ connections: [connection({ id: GEMINI, kind: 'GEMINI', label: 'Gemini', keyHint: 'x9Qa', chatModel: 'gemini-3.8-flash', embedModel: 'gemini-embedding-001' })] })
  const calls = await mockApi(
    page,
    {
      AiSettings: () => ({ aiSettings: state }),
      SaveAiConnection: (v) => {
        const input = v.input as Record<string, unknown>
        const saved = connection({ id: CLAUDE, kind: input.kind, label: input.label, chatModel: input.chatModel, hasKey: true, keyHint: String(input.apiKey).slice(-4), inputMicroUsdPerMTok: input.inputMicroUsdPerMTok, outputMicroUsdPerMTok: input.outputMicroUsdPerMTok })
        state.connections = [...state.connections, saved]
        return { saveAiConnection: { __typename: 'AiConnectionPayload', connection: saved, ...none } }
      },
      AiConnectionModels: accountModels,
      TestAiConnection: () => ({ testAiConnection: { __typename: 'AiConnectionTestPayload', test: { __typename: 'AiConnectionTest', ok: true, message: 'claude-sonnet-5-5 answered “OK”.', latencyMs: 812, models: CLAUDE_MODELS }, ...none } }),
      SetAiDefaults: (v) => {
        Object.assign(state, v.input as object)
        return { setAiDefaults: { __typename: 'AiSettingsPayload', settings: state, ...none } }
      },
      SaveAiTaskRoute: (v) => {
        state.routes = [{ __typename: 'AiTaskRoute', inputMicroUsdPerMTok: 0, outputMicroUsdPerMTok: 0, ...(v.input as object) }]
        return { saveAiTaskRoute: { __typename: 'AiSettingsPayload', settings: state, ...none } }
      },
      DeleteAiConnection: (v) => {
        state.connections = state.connections.filter((c) => (c as { id: string }).id !== (v.input as { id: string }).id)
        state.routes = []
        return { deleteAiConnection: { __typename: 'AiSettingsPayload', settings: state, ...none } }
      },
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/profile')
  await page.getByRole('link', { name: /AI providers/ }).click()
  await expect(page).toHaveURL(/\/admin\/ai$/)
  await expect(page.getByRole('heading', { name: 'AI providers' })).toBeVisible()
  await expect(page.getByText('Spent this month: $1.25 of the $50.00 budget.')).toBeVisible()
  await expect(page.getByLabel(/Chats, tasks and Ask AI/)).toHaveValue('')

  await page.getByRole('button', { name: 'Claude (Anthropic)' }).click()
  const dialog = page.getByRole('dialog', { name: 'Add Claude (Anthropic)' })
  await expect(dialog.getByLabel('Chat model', { exact: true })).toHaveValue('claude-sonnet-5-5')
  await expect(dialog.getByText('Claude (Anthropic) makes no embeddings.')).toBeVisible()
  await expect(dialog.getByLabel(/Private notes may go to it/)).not.toBeChecked()
  await dialog.getByLabel('API key').fill('sk-ant-secret-7777')
  await dialog.getByLabel('Input', { exact: true }).fill('3')
  await dialog.getByLabel('Output', { exact: true }).fill('15')
  await dialog.getByRole('button', { name: 'Save' }).click()
  await expect(dialog).toBeHidden()
  expect(calls.find((c) => c.op === 'SaveAiConnection')!.variables.input).toMatchObject({ kind: 'ANTHROPIC', label: 'Claude', apiKey: 'sk-ant-secret-7777', chatModel: 'claude-sonnet-5-5', embedModel: null, inputMicroUsdPerMTok: 3_000_000, outputMicroUsdPerMTok: 15_000_000, mayReceivePrivate: false, enabled: true })
  const card = page.getByRole('article', { name: 'Claude' })
  await expect(card.getByText('saved, ending 7777')).toBeVisible()
  await expect(page.getByText('sk-ant-secret-7777')).toHaveCount(0)

  await card.getByRole('button', { name: 'Test' }).click()
  await expect(card.getByText('claude-sonnet-5-5 answered “OK”.')).toBeVisible()
  // Every model the test lists, not the first 12.
  await card.getByText('30 models listed').click()
  const listed = card.getByRole('list', { name: 'Models Claude lists' }).getByRole('listitem')
  await expect(listed).toHaveCount(30)
  await expect(listed.last()).toHaveText('claude-model-29')

  await page.getByLabel(/Chats, tasks and Ask AI/).selectOption(CLAUDE)
  await expect.poll(() => calls.find((c) => c.op === 'SetAiDefaults')?.variables).toEqual({ input: { chatConnectionId: CLAUDE, embedConnectionId: null } })
  await expect(card.getByText('Answers chats')).toBeVisible()

  await page.getByLabel('Task', { exact: true }).selectOption('TRANSCRIBE')
  await page.getByLabel('Connection', { exact: true }).selectOption(GEMINI)
  // Transcription offers only models that support it. Embeddings and speech stay out.
  const model = page.getByLabel('Model', { exact: true })
  await expect.poll(() => offered(model)).toEqual(['gemini-3.8-flash'])
  await model.selectOption('gemini-3.8-flash')
  await page.getByRole('button', { name: 'Send this task there' }).click()
  const route = page.getByRole('listitem').filter({ hasText: 'TRANSCRIBE' })
  await expect(route).toContainText('Gemini · gemini-3.8-flash')
  expect(calls.find((c) => c.op === 'SaveAiTaskRoute')!.variables.input).toMatchObject({ task: 'TRANSCRIBE', connectionId: GEMINI, model: 'gemini-3.8-flash' })

  page.once('dialog', (d) => void d.accept())
  await page.getByRole('button', { name: 'Delete Gemini' }).click()
  await expect(page.getByRole('article', { name: 'Gemini' })).toHaveCount(0)
  await expect(route).toHaveCount(0)
})

test('only platform admins see the page; a server without AI_KEYS_SECRET says keys cannot be saved', async ({ page }) => {
  await mockApi(page, { AiSettings: () => ({ aiSettings: settings({ keysCanBeSaved: false }) }) }, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/admin/ai')
  await expect(page.getByText(/AI_KEYS_SECRET is not set on this server/)).toBeVisible()
  await page.getByRole('button', { name: 'ChatGPT (OpenAI)' }).click()
  await expect(page.getByRole('dialog').getByLabel('API key')).toBeDisabled()
})

test('others are turned away', async ({ page }) => {
  await mockApi(page, {}, viewerExtras)
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { operationName?: string }
    if (body.operationName !== 'AiSettings') return route.fallback()
    return route.fulfill({ json: { data: null, errors: [{ message: 'Only platform admins choose AI providers.', extensions: { code: 'FORBIDDEN' } }] } })
  })
  await page.goto('/admin/ai')
  await expect(page.getByText('Only platform admins choose AI providers.')).toBeVisible()
  await page.goto('/profile')
  await expect(page.getByRole('link', { name: /AI providers/ })).toHaveCount(0)
})

test('editing a connection offers every model its account has, in the chat and the embedding fields', async ({ page }) => {
  const state = settings({ connections: [connection({ id: GEMINI, kind: 'GEMINI', label: 'Gemini', keyHint: 'x9Qa', chatModel: 'gemini-3.8-flash', embedModel: 'gemini-embedding-001' })] })
  const calls = await mockApi(page, { AiSettings: () => ({ aiSettings: state }), AiConnectionModels: accountModels }, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/admin/ai')
  // Not tested in this visit: the dialog asks for the account's models itself.
  await page.getByRole('button', { name: 'Edit Gemini' }).click()
  const dialog = page.getByRole('dialog', { name: 'Edit Gemini' })
  await expect(dialog.getByText('2 models support this')).toHaveCount(2)
  expect(calls.find((c) => c.op === 'AiConnectionModels')!.variables).toEqual({ input: { id: GEMINI } })
  const chat = dialog.getByLabel('Chat model', { exact: true })
  const embed = dialog.getByLabel('Embedding model', { exact: true })
  await expect.poll(() => offered(chat)).toEqual(['gemini-2.5-pro', 'gemini-3.8-flash'])
  await expect.poll(() => offered(embed)).toEqual(['gemini-embedding-001', 'text-embedding-004'])
  await dialog.getByRole('searchbox', { name: 'Search chat models' }).fill('pro')
  await expect.poll(() => offered(chat)).toEqual(['gemini-2.5-pro'])
  await dialog.getByRole('searchbox', { name: 'Search chat models' }).fill('')
  await dialog.getByText('All models this provider lists (5)').click()
  await expect(dialog.getByRole('list', { name: 'All models Gemini lists' })).toContainText('gemini-2.5-flash-tts')
  await expect(dialog.getByRole('searchbox', { name: 'Search image models' })).toHaveCount(0)
  await expect(dialog.getByRole('searchbox', { name: 'Search speech models' })).toHaveCount(0)
  await dialog.getByRole('button', { name: 'Cancel' }).click()
  // A new connection has no account to ask yet, and says so.
  await page.getByRole('button', { name: 'ChatGPT (OpenAI)' }).click()
  await expect(page.getByRole('dialog').getByText('Save the connection to choose from every model its account has.')).toBeVisible()
})

test('a change that fails outright says so', async ({ page }) => {
  const state = settings({ connections: [connection({ id: GEMINI, kind: 'GEMINI', label: 'Gemini', chatModel: 'gemini-3.8-flash' })] })
  await mockApi(page, { AiSettings: () => ({ aiSettings: state }) }, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/admin/ai')
  // SetAiDefaults is not mocked: the API answers 500.
  await page.getByLabel(/Chats, tasks and Ask AI/).selectOption(GEMINI)
  await expect(page.getByText('Something went wrong. Try again.')).toBeVisible()
})

test('says why AI does not work on private notes, and lets the admin allow them for the connection that answers', async ({ page }) => {
  const claude = connection({ id: CLAUDE, kind: 'ANTHROPIC', label: 'Claude', keyHint: '7777', chatModel: 'claude-sonnet-5-5', inputMicroUsdPerMTok: 3_000_000, outputMicroUsdPerMTok: 15_000_000 })
  let state = settings({ connections: [claude, connection({ id: GEMINI, kind: 'GEMINI', label: 'Gemini', chatModel: 'gemini-3.8-flash' })], chatConnectionId: CLAUDE })
  const calls = await mockApi(
    page,
    {
      AiSettings: () => ({ aiSettings: state }),
      SaveAiConnection: (v) => {
        const input = v.input as Record<string, unknown>
        const saved = { ...claude, mayReceivePrivate: input.mayReceivePrivate }
        state = settings({ ...state, connections: [saved, state.connections[1]] })
        return { saveAiConnection: { __typename: 'AiConnectionPayload', connection: saved, ...none } }
      },
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/ai')
  const notice = page.getByRole('region', { name: 'AI does not work on private notes yet' })
  // Only the connection that answers is named; Gemini answers nothing here.
  await expect(notice).toContainText('Claude may not see private notes')
  await expect(notice.getByRole('button')).toHaveCount(1)
  page.once('dialog', (d) => void d.accept())
  await notice.getByRole('button', { name: 'Allow private notes for Claude' }).click()
  await expect(notice).toBeHidden()
  // The connection is saved as it was, with private notes allowed and its key kept.
  expect(calls.find((c) => c.op === 'SaveAiConnection')!.variables.input).toEqual({
    id: CLAUDE, kind: 'ANTHROPIC', label: 'Claude', baseUrl: null, apiKey: null, clearApiKey: false, chatModel: 'claude-sonnet-5-5', embedModel: null,
    inputMicroUsdPerMTok: 3_000_000, outputMicroUsdPerMTok: 15_000_000, embedMicroUsdPerMTok: 0, mayReceivePrivate: true, enabled: true,
  })
  await expect(page.getByRole('article', { name: 'Claude' }).getByText('May see private notes')).toBeVisible()
})

test('a model the provider does not offer for that use is rejected, and an empty picker stays hidden', async ({ page }) => {
  const local = '01920000-0000-7000-8000-0000000a1c03'
  const state = settings({
    connections: [
      connection({ id: GEMINI, kind: 'GEMINI', label: 'Gemini', keyHint: 'x9Qa', chatModel: 'retired-model', embedModel: 'gemini-embedding-001' }),
      connection({ id: local, kind: 'OLLAMA', label: 'Local', chatModel: 'gemma4', embedModel: null, hasKey: false }),
    ],
  })
  await mockApi(
    page,
    {
      AiSettings: () => ({ aiSettings: state }),
      AiConnectionModels: (v) => ({ aiConnectionModels: (v.input as { id: string }).id === local ? catalog([listed('gemma4', 'CHAT', ['CHAT'])], [['CHAT', [listed('gemma4', 'CHAT', ['CHAT'])]], ['EMBEDDING', []]]) : GEMINI_CATALOG }),
      SaveAiConnection: () => ({ saveAiConnection: { __typename: 'AiConnectionPayload', connection: null, userErrors: [{ __typename: 'UserError', code: 'VALIDATION', field: ['input', 'chatModel'], message: 'That model is not offered for chat.' }] } }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/ai')
  await page.getByRole('button', { name: 'Edit Gemini' }).click()
  const dialog = page.getByRole('dialog', { name: 'Edit Gemini' })
  await expect(dialog.getByLabel('Chat model', { exact: true })).toContainText('retired-model (not offered for this)')
  await dialog.getByLabel('Name').fill('Gemini west')
  await dialog.getByRole('button', { name: 'Save' }).click()
  await expect(dialog.getByText('That model is not offered for chat.')).toBeVisible()
  await dialog.getByRole('button', { name: 'Cancel' }).click()

  await page.getByRole('button', { name: 'Edit Local' }).click()
  const localDialog = page.getByRole('dialog', { name: 'Edit Local' })
  await expect(localDialog.getByText('This provider lists no embedding models.')).toBeVisible()
  await expect(localDialog.getByLabel('Embedding model')).toHaveCount(0)
})

test('nothing is saved when the admin does not confirm allowing private notes', async ({ page }) => {
  const state = settings({ connections: [connection({ id: CLAUDE, kind: 'ANTHROPIC', label: 'Claude', chatModel: 'claude-sonnet-5-5' })], chatConnectionId: CLAUDE })
  const calls = await mockApi(page, { AiSettings: () => ({ aiSettings: state }) }, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/admin/ai')
  page.once('dialog', (d) => void d.dismiss())
  await page.getByRole('button', { name: 'Allow private notes for Claude' }).click()
  await expect(page.getByRole('region', { name: 'AI does not work on private notes yet' })).toBeVisible()
  expect(calls.some((c) => c.op === 'SaveAiConnection')).toBe(false)
})
