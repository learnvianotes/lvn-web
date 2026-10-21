import { expect, test } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

/**
 * Uploads off (lvn-backend ADR-0097, the launch): nothing that would upload a file is offered — no Upload or Read a
 * PDF, no notes from photos, no picture, video, audio or file cards, no voice notes, no import — while writing notes,
 * cards and code works as before.
 */

const off = { UploadsEnabled: () => ({ uploadsEnabled: false }) }
const exportRow = { MyDataExports: () => ({ myDataExports: [] }), NoteImports: () => ({ noteImports: [] }) }

test('the notes page and the sidebar offer no uploads, and New note still works', async ({ page }) => {
  await mockApi(page, {
    ...off,
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
  })
  await page.setViewportSize({ width: 1280, height: 900 })
  await page.goto('/notes')
  await expect(page.getByText('Start your first note')).toBeVisible()
  await expect(page.getByRole('button', { name: 'New note' }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: 'Read a PDF' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Notes from photos' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Upload a PDF' })).toHaveCount(0)
})

test('the editor adds only cards that need no file, and no voice note', async ({ page }) => {
  await mockApi(page, { ...off, NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }) })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  await page.getByRole('button', { name: 'Add a card', exact: true }).last().click()
  await expect(page.getByRole('button', { name: /^Code/ }).first()).toBeVisible()
  for (const kind of [/^Image/, /^Video/, /^Audio/, /^File/, /Record a voice note/]) {
    await expect(page.getByRole('button', { name: kind })).toHaveCount(0)
  }
})

test('Your data downloads everything, and offers no import', async ({ page }) => {
  await mockApi(page, { ...off, ...exportRow }, { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } })
  await page.goto('/profile')
  await expect(page.getByRole('button', { name: 'Prepare my archive' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Import notes' })).toHaveCount(0)
})

test('verification offers asking a teacher only, and its lead does not mention documents', async ({ page }) => {
  await mockApi(page, { ...off, ...exportRow, MyVerificationRequests: () => ({ myVerificationRequests: [] }) }, {
    profile: null,
    legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null },
    verified: false,
    verificationMethod: null,
  })
  await page.goto('/profile')
  await expect(page.getByRole('button', { name: 'Ask a teacher' })).toBeVisible()
  await expect(page.getByText('No college email? Ask a teacher who knows you to vouch for you.', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Send proof of study' })).toHaveCount(0)
})

test('with uploads on, the same places offer them (development, and once turned on)', async ({ page }) => {
  await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
  })
  await page.setViewportSize({ width: 1280, height: 900 })
  await page.goto('/notes')
  await expect(page.getByRole('button', { name: 'Read a PDF' }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: 'Notes from photos' }).first()).toBeVisible()
})
