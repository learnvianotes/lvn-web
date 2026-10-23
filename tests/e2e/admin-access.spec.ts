import { expect, test, type Page } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Beta access (contracts 0.69.0) against a mocked API: the allowlist, its guards, and the invite-only switch.
 */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const constraints = { __typename: 'AdminSettingConstraints', min: null, max: null, maxLength: null, pattern: null, nullable: false }
const none = { userErrors: [] }
const problem = (message: string) => ({ __typename: 'UserError', code: 'FORBIDDEN', field: null, message })

type Entry = {
  __typename: 'AccessAllowlistEntry'
  id: string
  email: string
  role: string
  note: string | null
  hasAccount: boolean
  addedByEmail: string | null
  createdAt: string
}

const seed = (): Entry[] => [
  { __typename: 'AccessAllowlistEntry', id: '01920000-0000-7000-8000-000000000a01', email: 'asha@example.com', role: 'PLATFORM_ADMIN', note: 'Owner', hasAccount: true, addedByEmail: null, createdAt: '2026-10-01T00:00:00.000Z' },
  { __typename: 'AccessAllowlistEntry', id: '01920000-0000-7000-8000-000000000a02', email: 'other-admin@example.com', role: 'PLATFORM_ADMIN', note: null, hasAccount: true, addedByEmail: 'asha@example.com', createdAt: '2026-10-02T00:00:00.000Z' },
  { __typename: 'AccessAllowlistEntry', id: '01920000-0000-7000-8000-000000000a03', email: 'student@college.edu', role: 'STUDENT', note: 'Class of 2026', hasAccount: false, addedByEmail: 'asha@example.com', createdAt: '2026-10-03T00:00:00.000Z' },
]

let entries: Entry[] = seed()
let allowlistOn = true

function guard(entry: Entry, nextRole?: string) {
  const dropping = nextRole === undefined || nextRole !== 'PLATFORM_ADMIN'
  const admins = entries.filter((item) => item.role === 'PLATFORM_ADMIN')
  if (entry.role === 'PLATFORM_ADMIN' && dropping && admins.length === 1) return problem("You can't remove the last platform admin.")
  if (entry.email === 'asha@example.com' && dropping) return problem("You can't remove or change your own access.")
  return null
}

async function accessApi(page: Page) {
  entries = seed()
  allowlistOn = true
  return mockApi(
    page,
    {
      AdminAccessAllowlist: (v) => {
        const search = String(v.search ?? '').toLowerCase()
        const list = search ? entries.filter((entry) => entry.email.includes(search)) : entries
        return { adminAccessAllowlist: list }
      },
      AddAccessAllowlistEntry: (v) => {
        const input = v.input as { email: string; role: string; note?: string | null }
        if (entries.some((entry) => entry.email === input.email)) {
          return { addAccessAllowlistEntry: { __typename: 'AccessAllowlistPayload', entry: null, userErrors: [{ __typename: 'UserError', code: 'CONFLICT', field: ['input', 'email'], message: 'That email is already on the list.' }] } }
        }
        const entry: Entry = {
          __typename: 'AccessAllowlistEntry',
          id: `01920000-0000-7000-8000-000000000a${entries.length + 1}`,
          email: input.email,
          role: input.role,
          note: input.note ?? null,
          hasAccount: false,
          addedByEmail: 'asha@example.com',
          createdAt: '2026-10-23T00:00:00.000Z',
        }
        entries = [...entries, entry]
        return { addAccessAllowlistEntry: { __typename: 'AccessAllowlistPayload', entry, ...none } }
      },
      UpdateAccessAllowlistEntry: (v) => {
        const input = v.input as { id: string; role?: string }
        const entry = entries.find((item) => item.id === input.id)
        if (!entry) return { updateAccessAllowlistEntry: { __typename: 'AccessAllowlistPayload', entry: null, userErrors: [problem('Not on the list.')] } }
        const blocked = input.role ? guard(entry, input.role) : null
        if (blocked) return { updateAccessAllowlistEntry: { __typename: 'AccessAllowlistPayload', entry: null, userErrors: [blocked] } }
        entries = entries.map((item) => (item.id === entry.id ? { ...item, role: input.role ?? item.role } : item))
        return { updateAccessAllowlistEntry: { __typename: 'AccessAllowlistPayload', entry: entries.find((item) => item.id === entry.id), ...none } }
      },
      RemoveAccessAllowlistEntry: (v) => {
        const entry = entries.find((item) => item.id === v.id)
        if (!entry) return { removeAccessAllowlistEntry: { __typename: 'OkPayload', ok: false, userErrors: [problem('Not on the list.')] } }
        const blocked = guard(entry)
        if (blocked) return { removeAccessAllowlistEntry: { __typename: 'OkPayload', ok: false, userErrors: [blocked] } }
        entries = entries.filter((item) => item.id !== entry.id)
        return { removeAccessAllowlistEntry: { __typename: 'OkPayload', ok: true, ...none } }
      },
      AdminSettings: () => ({
        adminSettings: [
          {
            __typename: 'AdminSetting',
            key: 'access_allowlist_enabled',
            type: 'BOOLEAN',
            category: 'auth',
            description: 'Only listed emails can sign in.',
            value: allowlistOn ? 'true' : 'false',
            overridden: allowlistOn,
            updatedAt: '2026-10-01T00:00:00.000Z',
            constraints,
          },
        ],
      }),
      UpdateAdminSetting: (v) => {
        const input = v.input as { key: string; value: string }
        if (input.key === 'access_allowlist_enabled') allowlistOn = input.value === 'true'
        return {
          updateAdminSetting: {
            __typename: 'AdminSettingPayload',
            setting: {
              __typename: 'AdminSetting',
              key: input.key,
              type: 'BOOLEAN',
              category: 'auth',
              description: 'Only listed emails can sign in.',
              value: input.value,
              overridden: true,
              updatedAt: '2026-10-23T00:00:00.000Z',
              constraints,
            },
            ...none,
          },
        }
      },
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
}

test('an admin lists, searches, adds, changes and removes beta emails, and the guards hold', async ({ page }) => {
  const calls = await accessApi(page)
  await page.goto('/admin/access')
  await expect(page.getByRole('heading', { name: 'Beta access', level: 1 })).toBeVisible()
  await expect(page.getByRole('switch', { name: 'Invite-only beta' })).toHaveAttribute('aria-checked', 'true')
  await expect(page.getByRole('link', { name: 'Open in configuration' })).toHaveAttribute('href', '/admin/settings#auth')
  await expect(page.getByRole('article', { name: 'asha@example.com' })).toContainText('Has an account')
  await expect(page.getByRole('article', { name: 'student@college.edu' })).toContainText('No account yet')
  await expect(page.getByRole('article', { name: 'student@college.edu' })).toContainText('Class of 2026')

  await page.getByLabel('Search emails').fill('student')
  await expect(page.getByRole('article', { name: 'asha@example.com' })).toHaveCount(0)
  await expect(page.getByRole('article', { name: 'student@college.edu' })).toBeVisible()
  await page.getByLabel('Search emails').fill('')
  await expect(page.getByRole('article', { name: 'asha@example.com' })).toBeVisible()

  await page.getByLabel('Email addresses').fill('not-an-email')
  await page.getByRole('button', { name: 'Add', exact: true }).click()
  await expect(page.getByRole('alert').filter({ hasText: 'not-an-email' })).toBeVisible()
  expect(calls.some((call) => call.op === 'AddAccessAllowlistEntry')).toBe(false)

  await page.getByLabel('Email addresses').fill('new@college.edu, second@college.edu')
  await page.getByLabel('Role', { exact: true }).selectOption('TEACHER')
  await page.getByLabel('Note', { exact: true }).fill('Invited together')
  await page.getByRole('button', { name: 'Add', exact: true }).click()
  await expect(page.getByRole('article', { name: 'new@college.edu' })).toBeVisible()
  await expect(page.getByRole('article', { name: 'second@college.edu' })).toBeVisible()
  expect(calls.filter((call) => call.op === 'AddAccessAllowlistEntry')).toHaveLength(2)

  await page.getByLabel('Email addresses').fill('new@college.edu')
  await page.getByRole('button', { name: 'Add', exact: true }).click()
  await expect(page.getByRole('alert').filter({ hasText: 'already on the list' })).toBeVisible()

  const student = page.getByRole('article', { name: 'student@college.edu' })
  await student.getByLabel('Role for student@college.edu').selectOption('TEACHER')
  await expect.poll(() => calls.find((call) => call.op === 'UpdateAccessAllowlistEntry')?.variables.input).toMatchObject({ id: '01920000-0000-7000-8000-000000000a03', role: 'TEACHER' })
  await expect(student.getByLabel('Role for student@college.edu')).toHaveValue('TEACHER')

  await student.getByRole('button', { name: 'Remove student@college.edu' }).click()
  const confirm = page.getByRole('dialog', { name: 'Remove student@college.edu' })
  await expect(confirm).toContainText('student@college.edu')
  await confirm.getByRole('button', { name: 'Remove', exact: true }).click()
  await expect(page.getByRole('article', { name: 'student@college.edu' })).toHaveCount(0)

  const self = page.getByRole('article', { name: 'asha@example.com' })
  await self.getByRole('button', { name: 'Remove asha@example.com' }).click()
  await page.getByRole('dialog', { name: 'Remove asha@example.com' }).getByRole('button', { name: 'Remove', exact: true }).click()
  await expect(page.getByRole('alert').filter({ hasText: "can't remove or change your own access" })).toBeVisible()
  await page.getByRole('dialog', { name: 'Remove asha@example.com' }).getByRole('button', { name: 'Cancel' }).click()

  await self.getByLabel('Role for asha@example.com').selectOption('STUDENT')
  await expect(page.getByRole('alert').filter({ hasText: "can't remove or change your own access" })).toBeVisible()
  await expect(self.getByLabel('Role for asha@example.com')).toHaveValue('PLATFORM_ADMIN')

  await page.getByRole('article', { name: 'other-admin@example.com' }).getByRole('button', { name: 'Remove other-admin@example.com' }).click()
  await page.getByRole('dialog', { name: 'Remove other-admin@example.com' }).getByRole('button', { name: 'Remove', exact: true }).click()
  await expect(page.getByRole('article', { name: 'other-admin@example.com' })).toHaveCount(0)
  await self.getByRole('button', { name: 'Remove asha@example.com' }).click()
  await page.getByRole('dialog', { name: 'Remove asha@example.com' }).getByRole('button', { name: 'Remove', exact: true }).click()
  await expect(page.getByRole('alert').filter({ hasText: "can't remove the last platform admin" })).toBeVisible()
  await page.getByRole('dialog', { name: 'Remove asha@example.com' }).getByRole('button', { name: 'Cancel' }).click()

  await page.getByRole('switch', { name: 'Invite-only beta' }).click()
  const setting = page.getByRole('dialog', { name: 'Change beta access' })
  await expect(setting).toContainText('Turn the allowlist off?')
  await setting.getByRole('button', { name: 'Save' }).click()
  await expect(page.getByRole('switch', { name: 'Invite-only beta' })).toHaveAttribute('aria-checked', 'false')
  expect(calls.some((call) => call.op === 'UpdateAdminSetting' && (call.variables.input as { value: string }).value === 'false')).toBe(true)
})
