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
      TestAiConnection: () => ({ testAiConnection: { __typename: 'AiConnectionTestPayload', test: { __typename: 'AiConnectionTest', ok: true, message: 'claude-sonnet-5-5 answered “OK”.', latencyMs: 812, models: ['claude-haiku-5-5', 'claude-sonnet-5-5'] }, ...none } }),
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
  await expect(dialog.getByLabel('Chat model')).toHaveValue('claude-sonnet-5-5')
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
  await expect(card.getByText('2 models listed: claude-haiku-5-5, claude-sonnet-5-5')).toBeVisible()

  await page.getByLabel(/Chats, tasks and Ask AI/).selectOption(CLAUDE)
  await expect.poll(() => calls.find((c) => c.op === 'SetAiDefaults')?.variables).toEqual({ input: { chatConnectionId: CLAUDE, embedConnectionId: null } })
  await expect(card.getByText('Answers chats')).toBeVisible()

  await page.getByLabel('Task', { exact: true }).selectOption('TRANSCRIBE')
  await page.getByLabel('Connection', { exact: true }).selectOption(GEMINI)
  await page.getByLabel('Model', { exact: true }).fill('gemini-3.8-flash')
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
