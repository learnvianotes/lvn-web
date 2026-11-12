import { expect, test, type Locator, type Page } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1, type Handler } from './support/notes-api'

/**
 * Long lines in a note's code (a labelled code card and an Output fence) scroll sideways at a phone width,
 * and a focused text field has one border — not an outline stacked on a ring.
 */

const LINE = 'Fraction(int n, int d) : num_(n), den_(d) {} friend std::ostream& operator<<(std::ostream& os, const Fraction& f) { return os << f.num_; }'
const OUTPUT = 'Output: 1/2\n' + LINE

const codeCard = {
  __typename: 'Card',
  id: '01920000-0000-7000-8000-00000000c0c1',
  type: 'code',
  position: 'a2',
  revision: 1,
  content: { language: 'cpp', filename: 'fraction.cpp', code: LINE },
}
const markdownCard = {
  __typename: 'Card',
  id: '01920000-0000-7000-8000-00000000c0c2',
  type: 'markdown',
  position: 'a3',
  revision: 1,
  content: { source: '```\n' + OUTPUT + '\n```' },
}
const withCode = [...cards, codeCard, markdownCard]

const aiState = { aiStatus: { __typename: 'AiStatus', available: false, reason: 'NOT_CONFIGURED' }, myAiAllowance: { __typename: 'AiAllowance', usedToday: 0, limitToday: 200_000, resetsAt: new Date(Date.now() + 3_600_000).toISOString() } }
const quiet: Record<string, Handler> = {
  AiState: () => aiState,
  NoteAiArtifacts: () => ({ note: { __typename: 'Note', id: NOTE_ID, cards: { __typename: 'CardConnection', edges: [] }, aiArtifacts: [] } }),
  NoteInsights: () => ({ note: { __typename: 'Note', id: NOTE_ID, noteProcessingStatus: null, aiInsights: [] } }),
  UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, userErrors: [] } }),
}

async function phone(page: Page) {
  await page.setViewportSize({ width: 390, height: 844 })
}

/** The pre scrolls, the line is not wrapped, and the page itself does not grow sideways. */
async function expectScrollableCode(pre: Locator) {
  await expect(pre).toBeVisible()
  const box = await pre.evaluate((el) => {
    const style = getComputedStyle(el)
    const code = el.querySelector('code')
    const codeStyle = code ? getComputedStyle(code) : null
    const parentHidden = (node: HTMLElement | null): boolean => {
      while (node) {
        if (getComputedStyle(node).overflowX === 'hidden' && node.scrollWidth > node.clientWidth + 1) return true
        node = node.parentElement
      }
      return false
    }
    el.scrollLeft = 80
    return {
      overflowX: style.overflowX,
      whiteSpace: style.whiteSpace,
      codeWhiteSpace: codeStyle?.whiteSpace ?? '',
      touchAction: style.touchAction,
      scrollWidth: el.scrollWidth,
      clientWidth: el.clientWidth,
      scrollLeft: el.scrollLeft,
      clipped: parentHidden(el.parentElement),
      pageWider: document.documentElement.scrollWidth > window.innerWidth + 2,
    }
  })
  expect(box.overflowX).toBe('auto')
  expect(box.whiteSpace).toBe('pre')
  expect(box.codeWhiteSpace).toBe('pre')
  const pans = box.touchAction === 'auto' || box.touchAction === 'manipulation' || (box.touchAction.includes('pan-x') && box.touchAction.includes('pan-y'))
  expect(pans).toBe(true)
  expect(box.scrollWidth).toBeGreaterThan(box.clientWidth)
  expect(box.scrollLeft).toBeGreaterThan(0)
  expect(box.clipped).toBe(false)
  expect(box.pageWider).toBe(false)
}

async function focusChrome(locator: Locator) {
  await locator.focus()
  return locator.evaluate((el) => {
    const style = getComputedStyle(el)
    return { outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth, boxShadow: style.boxShadow }
  })
}

test('a reader can scroll a code card and an Output block at 390px', async ({ page }) => {
  await phone(page)
  await mockApi(page, {
    ...quiet,
    NoteToEdit: () => ({
      note: {
        ...meta({
          viewerAccess: 'READER',
          visibility: 'PUBLIC',
          publishedAt: new Date().toISOString(),
          viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: false },
        }),
        cards: page1(withCode),
      },
    }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const blocks = page.locator('pre.lvn-code-scroll')
  await expect(blocks).toHaveCount(2)
  await expectScrollableCode(blocks.nth(0))
  await expectScrollableCode(blocks.nth(1))
  await expect(blocks.nth(1)).toContainText('Output: 1/2')
})

test('the editor shows the same code card as a sideways scroller', async ({ page }) => {
  await phone(page)
  await mockApi(page, {
    ...quiet,
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(withCode) } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const pre = page.locator('[data-card="codeCard"] pre.lvn-code-scroll')
  await expect(pre).toBeVisible()
  await expectScrollableCode(pre)
  await expect(pre).toContainText('Fraction(int n, int d)')
})

test('a public note scrolls its code card at 390px', async ({ page }) => {
  await phone(page)
  await page.route('**/graphql', (route) => route.fulfill({ json: { data: { refreshSession: null } } }))
  await page.goto('/n/dijkstras-algorithm-01920000-0000-7000-8000-00000000d001')
  const blocks = page.locator('pre.lvn-code-scroll')
  await expect(blocks).toHaveCount(2)
  await expectScrollableCode(blocks.first())
  await expect(blocks.nth(1)).toContainText('Output:')
})

test('the search overlay focuses with one border, not a doubled ring', async ({ page }) => {
  await mockApi(page, { Organise: () => ({ myFolders: [], myTags: [] }), MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }) })
  await page.goto('/notes')
  await page.getByRole('button', { name: /Search notes/ }).click()
  const palette = page.getByRole('dialog', { name: 'Search notes, people, groups and topics' })
  const combobox = palette.getByRole('combobox')
  await expect(combobox).toBeVisible()
  const chrome = await focusChrome(combobox)
  expect(chrome.outlineStyle).toBe('none')
  expect(chrome.boxShadow).toBe('none')
  const labelShadow = await combobox.evaluate((el) => getComputedStyle(el.closest('label')!).boxShadow)
  expect(labelShadow).toBe('none')
})

test('a sign-in field focuses with one border, not an outline or a ring', async ({ page }) => {
  await page.route('**/graphql', async (route) => {
    const body = route.request().postDataJSON() as { query: string; operationName?: string }
    const op = body.operationName ?? (body.query.includes('refreshSession') ? 'Refresh' : '')
    if (op === 'Refresh' || op === 'RefreshSession') {
      return route.fulfill({ json: { data: null, errors: [{ message: 'Session ended', extensions: { code: 'UNAUTHENTICATED' } }] } })
    }
    if (op === 'SignInOptions') {
      return route.fulfill({ json: { data: { signInOptions: { emailPassword: true, google: false, github: false, linkedin: false }, termsVersion: '2026-10-08' } } })
    }
    if (op === 'AccessPolicy') return route.fulfill({ json: { data: { accessPolicy: { __typename: 'AccessPolicy', inviteOnly: false } } } })
    return route.fulfill({ json: { data: null } })
  })
  await page.goto('/sign-in')
  const email = page.getByLabel('Email', { exact: true })
  await expect(email).toBeVisible()
  const field = await focusChrome(email)
  expect(field.outlineStyle).toBe('none')
  expect(field.boxShadow).toBe('none')
  const border = await email.evaluate((el) => getComputedStyle(el).borderTopWidth)
  expect(border).not.toBe('0px')
})
