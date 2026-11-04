import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/** Settings → Data (lvn-backend ADR-0018) on the account page: download everything, import notes. */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const exportRow = (over: object) => ({ __typename: 'DataExport', id: '01920000-0000-7000-8000-00000000d0e1', status: 'PENDING', requestedAt: new Date().toISOString(), readyAt: null, expiresAt: null, sizeBytes: null, downloadUrl: null, ...over })
const importRow = (over: object) => ({ __typename: 'NoteImport', id: '01920000-0000-7000-8000-00000000d0f1', fileName: 'vault.zip', status: 'RUNNING', progress: 40, created: 0, notes: [], skipped: [], error: null, createdAt: new Date().toISOString(), finishedAt: null, ...over })
const none = { userErrors: [] }

test('prepares an archive and offers it for download', async ({ page }) => {
  let state: 'none' | 'pending' | 'ready' = 'none'
  const calls = await mockApi(
    page,
    {
      MyDataExports: () => ({ myDataExports: state === 'none' ? [] : [exportRow(state === 'ready' ? { status: 'READY', sizeBytes: 2_400_000, expiresAt: new Date(Date.now() + 7 * 86_400_000).toISOString(), downloadUrl: 'http://storage.test/export.zip' } : {})] }),
      RequestDataExport: () => {
        state = 'pending'
        setTimeout(() => (state = 'ready'), 1_500)
        return { requestDataExport: { export: exportRow({}), ...none } }
      },
      NoteImports: () => ({ noteImports: [] }),
    },
    viewerExtras,
  )
  await page.goto('/profile')
  // What the Privacy Policy promises the archive holds: the age record and the activity events too.
  await expect(page.getByText(/your account with the age you gave \(or your date of birth, if you gave one\) and the terms you accepted, .* every learning activity event/)).toBeVisible()
  await page.getByRole('button', { name: 'Prepare my archive' }).click()
  await expect(page.getByText('Preparing your archive…')).toBeVisible()
  const download = page.getByRole('link', { name: 'Download' })
  await expect(download).toHaveAttribute('href', 'http://storage.test/export.zip', { timeout: 15_000 })
  await expect(page.getByText(/Your archive is ready \(2\.3 MB\)/)).toBeVisible()
  expect(calls.filter((c) => c.op === 'RequestDataExport')).toHaveLength(1)
})

test('imports a ZIP: upload, progress, then what was made and skipped', async ({ page }) => {
  let state: 'none' | 'running' | 'done' = 'none'
  const puts: string[] = []
  await page.route('http://storage.test/**', async (route) => {
    if (route.request().method() === 'OPTIONS') return route.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT', 'access-control-allow-headers': '*' } })
    puts.push(route.request().headers()['content-type'] ?? '')
    return route.fulfill({ status: 200, headers: { 'access-control-allow-origin': '*' } })
  })
  const calls = await mockApi(
    page,
    {
      MyDataExports: () => ({ myDataExports: [] }),
      NoteImports: () => ({
        noteImports:
          state === 'none'
            ? []
            : [state === 'running' ? importRow({}) : importRow({ status: 'DONE', progress: 100, created: 2, notes: [{ __typename: 'ImportedNote', id: '01920000-0000-7000-8000-00000000a001', title: 'Graph traversal' }, { __typename: 'ImportedNote', id: '01920000-0000-7000-8000-00000000a002', title: 'todo' }], skipped: [{ __typename: 'ImportSkip', path: 'Vault/setup.exe', reason: 'not Markdown, text or a file notes accept' }] })],
      }),
      CreateImportUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: '01920000-0000-7000-8000-00000000f0f1', uploadUrl: 'http://storage.test/put', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'application/zip' }] }, ...none } }),
      CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...none } }),
      ImportNotes: () => {
        state = 'running'
        setTimeout(() => (state = 'done'), 2_500)
        return { importNotes: { noteImport: importRow({}), ...none } }
      },
    },
    viewerExtras,
  )
  await page.goto('/profile')
  await page.getByLabel('Choose a file to import').setInputFiles({ name: 'vault.zip', mimeType: 'application/zip', buffer: Buffer.from('PK\x03\x04') })
  await expect(page.getByText('Importing vault.zip…')).toBeVisible()
  await expect(page.getByText('2 notes imported from vault.zip.')).toBeVisible({ timeout: 15_000 })
  await expect(page.getByRole('link', { name: 'Graph traversal' })).toHaveAttribute('href', '/notes/01920000-0000-7000-8000-00000000a001')
  await page.getByText('1 item was skipped').click()
  await expect(page.getByText('not Markdown, text or a file notes accept')).toBeVisible()
  expect(calls.find((c) => c.op === 'CreateImportUpload')?.variables).toEqual({ input: { fileName: 'vault.zip', mimeType: 'application/zip', sizeBytes: 4, purpose: 'IMPORT' } })
  expect(puts).toEqual(['application/zip'])
})

test('asks before importing the same file again', async ({ page }) => {
  let confirmed = false
  const calls = await mockApi(
    page,
    {
      MyDataExports: () => ({ myDataExports: [] }),
      NoteImports: () => ({ noteImports: [importRow(confirmed ? { status: 'DONE', progress: 100, created: 1 } : { status: 'NEEDS_CONFIRMATION' })] }),
      ConfirmNoteImport: () => {
        confirmed = true
        return { confirmNoteImport: { noteImport: importRow({ status: 'PENDING' }), ...none } }
      },
    },
    viewerExtras,
  )
  await page.goto('/profile')
  await expect(page.getByText('You imported vault.zip before. Import it again?')).toBeVisible()
  await page.getByRole('button', { name: 'Import again' }).click()
  await expect(page.getByText('1 note imported from vault.zip.')).toBeVisible()
  expect(calls.find((c) => c.op === 'ConfirmNoteImport')?.variables).toEqual({ id: '01920000-0000-7000-8000-00000000d0f1' })
})

test('deletes the account 14 days after asking, with the date on every page and a way to keep it (lvn-backend ADR-0088)', async ({ page }) => {
  // The viewer the mock answers with, changed as the person asks and cancels.
  const viewer: Record<string, unknown> = { ...viewerExtras, deletionScheduledFor: null }
  const due = new Date(Date.now() + 14 * 86_400_000).toISOString()
  const calls = await mockApi(
    page,
    {
      MyDataExports: () => ({ myDataExports: [] }),
      NoteImports: () => ({ noteImports: [] }),
      RequestAccountDeletion: (v) => {
        const input = v.input as { confirm: string; password: string | null }
        if (input.password !== 'my passphrase') return { requestAccountDeletion: { deletionScheduledFor: null, userErrors: [{ __typename: 'UserError', field: ['input', 'password'], message: 'That password is not right.' }] } }
        viewer.deletionScheduledFor = due
        return { requestAccountDeletion: { deletionScheduledFor: due, ...none } }
      },
      CancelAccountDeletion: () => {
        viewer.deletionScheduledFor = null
        return { cancelAccountDeletion: { deletionScheduledFor: null, userErrors: [] } }
      },
      Organise: () => ({ myFolders: [], myTags: [] }),
      MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    },
    viewer,
  )
  await page.goto('/profile')
  const section = page.getByRole('region', { name: 'Delete your account' })
  const submit = section.getByRole('button', { name: 'Delete my account' })
  await expect(submit).toBeDisabled()
  await section.getByLabel('Your password').fill('wrong')
  await section.getByLabel('Type DELETE to confirm').fill('delete')
  await submit.click()
  await expect(section.getByRole('alert')).toHaveText('That password is not right.')
  await section.getByLabel('Your password').fill('my passphrase')
  await submit.click()
  const date = new Date(due).toLocaleDateString('en', { day: 'numeric', month: 'long', year: 'numeric' })
  await expect(section.getByRole('status')).toContainText(date)
  expect(calls.filter((c) => c.op === 'RequestAccountDeletion').map((c) => c.variables.input)).toEqual([{ password: 'wrong', confirm: 'delete' }, { password: 'my passphrase', confirm: 'delete' }])

  // Every page says when, with a way to keep the account.
  await page.goto('/notes')
  const banner = page.getByRole('alert').filter({ hasText: 'Your account will be deleted on' })
  await expect(banner).toContainText(date)
  await banner.getByRole('button', { name: 'Keep my account' }).click()
  await expect(banner).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'CancelAccountDeletion')).toHaveLength(1)
})
