import { readFileSync } from 'node:fs'
import { expect, test } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

/**
 * Saved notes and Bookmarks (lvn-backend ADR-0076): a reader saves a note and takes it off again; Bookmarks lists the
 * saved notes and resources, each section with a way to find more when empty, and more notes on demand; a visitor of
 * a public note is asked to sign in to save it.
 */
const FRIEND = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }
const readerNote = () => ({
  note: { ...meta({ viewerAccess: 'READER', owner: FRIEND, visibility: 'PUBLIC', publishedAt: new Date().toISOString(), viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true } }), cards: page1(cards) },
})
const savedNote = (id: string, title: string) => ({ __typename: 'Note', id, title, excerpt: `About ${title.toLowerCase()}`, kind: 'NOTE', slug: title.toLowerCase(), visibility: 'PUBLIC', publishedAt: new Date().toISOString(), owner: FRIEND })
const connection = (nodes: unknown[], next: string | null = null) => ({ __typename: 'NoteConnection', edges: nodes.map((node) => ({ __typename: 'NoteEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: !!next, endCursor: next } })

test('a reader saves a note to their Bookmarks, and takes it off again', async ({ page }) => {
  let saved = false
  const calls = await mockApi(page, {
    NoteToEdit: readerNote,
    NoteSaved: () => ({ note: { __typename: 'Note', id: NOTE_ID, viewerSaved: saved } }),
    SaveNote: () => ((saved = true), { saveNote: { __typename: 'NotePayload', note: { __typename: 'Note', id: NOTE_ID, viewerSaved: true }, userErrors: [] } }),
    UnsaveNote: () => ((saved = false), { unsaveNote: { __typename: 'NotePayload', note: { __typename: 'Note', id: NOTE_ID, viewerSaved: false }, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const save = page.getByRole('button', { name: 'Save', exact: true })
  await expect(save).toHaveAttribute('aria-pressed', 'false')
  await save.click()
  const saved_ = page.getByRole('button', { name: 'Saved', exact: true })
  await expect(saved_).toHaveAttribute('aria-pressed', 'true')
  expect(calls.find((c) => c.op === 'SaveNote')?.variables).toEqual({ noteId: NOTE_ID })
  await saved_.click()
  await expect(page.getByRole('button', { name: 'Save', exact: true })).toHaveAttribute('aria-pressed', 'false')
  expect(calls.find((c) => c.op === 'UnsaveNote')?.variables).toEqual({ noteId: NOTE_ID })
})

test('Bookmarks lists saved notes and resources; more notes on demand; each opens', async ({ page }) => {
  const A = '01920000-0000-7000-8000-00000000a0a1'
  const B = '01920000-0000-7000-8000-00000000a0a2'
  const calls = await mockApi(page, {
    SavedNotes: (v) => ({ savedNotes: v.after ? connection([savedNote(B, 'Tries')]) : connection([savedNote(A, 'Heaps')], 'next') }),
    SavedResources: () => ({ savedResources: page1([]) }),
  })
  await page.goto('/saved')
  await expect(page.getByRole('heading', { name: 'Bookmarks', level: 1 })).toBeVisible()
  const notes = page.getByRole('region', { name: 'Notes' })
  await expect(notes.getByRole('link', { name: /Heaps/ })).toHaveAttribute('href', `/notes/${A}`)
  await notes.getByRole('button', { name: 'Show more' }).click()
  await expect(notes.getByRole('link', { name: /Tries/ })).toHaveAttribute('href', `/notes/${B}`)
  await expect(notes.getByRole('button', { name: 'Show more' })).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'SavedNotes').at(-1)?.variables).toMatchObject({ after: 'next' })
  // An empty section offers a way to find something to save.
  await expect(page.getByRole('region', { name: 'Resources' }).getByRole('link', { name: 'Browse resources' })).toHaveAttribute('href', '/resources')
})

test('with nothing saved, Bookmarks leads to notes and resources to find', async ({ page }) => {
  await mockApi(page, { SavedNotes: () => ({ savedNotes: connection([]) }), SavedResources: () => ({ savedResources: page1([]) }) })
  await page.goto('/saved')
  await expect(page.getByRole('region', { name: 'Notes' }).getByRole('link', { name: 'Find notes' })).toHaveAttribute('href', '/search')
  await expect(page.getByRole('region', { name: 'Resources' }).getByRole('link', { name: 'Browse resources' })).toHaveAttribute('href', '/resources')
})

test('a visitor of a public note is asked to sign in to save it, and comes back to it', async ({ page }) => {
  type Fixture = { id: string; slug: string }
  const note = (JSON.parse(readFileSync(new URL('./support/public-notes.json', import.meta.url), 'utf8')) as { notes: Fixture[] }).notes[0]!
  const path = `/n/${note.slug}-${note.id}`
  await page.goto(path)
  await expect(page.getByRole('link', { name: 'Save' })).toHaveAttribute('href', `/sign-in?next=${encodeURIComponent(path)}`)
})
