import { expect, test } from '@playwright/test'
import { TERMS_VERSION } from '../../features/legal/documents'
import { mockApi } from './support/notes-api'

/** §15.2: the Terms, Privacy Policy and content licence — readable, linked where people accept them, accepted again on change. */

test('the three documents are public, versioned and linked from every page', async ({ page }) => {
  await page.goto('/legal/terms')
  await expect(page.getByRole('heading', { level: 1, name: 'Terms of Service' })).toBeVisible()
  await expect(page.getByText(`Version ${TERMS_VERSION}`)).toBeVisible()
  await expect(page.getByRole('note')).toContainText('Draft for review')
  await page.getByRole('navigation', { name: 'Legal' }).first().getByRole('link', { name: 'Privacy Policy' }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Privacy Policy' })).toBeVisible()
  await page.goto('/legal/content-licence')
  await expect(page.getByRole('heading', { level: 1, name: 'Content licence' })).toBeVisible()
  // The footer of every page.
  await page.goto('/')
  await expect(page.getByRole('contentinfo').getByRole('link', { name: 'Terms of Service' })).toHaveAttribute('href', '/legal/terms')
})

test('sign-up links the documents it asks people to accept', async ({ page }) => {
  await page.route('**/graphql', (route) => route.fulfill({ json: { data: { signInOptions: { emailPassword: true, google: false, github: false, linkedin: false }, termsVersion: TERMS_VERSION } } }))
  await page.goto('/sign-up')
  const consent = page.locator('label').filter({ has: page.getByRole('checkbox') })
  await expect(consent.getByRole('link', { name: 'Terms' })).toHaveAttribute('href', '/legal/terms')
  await expect(consent.getByRole('link', { name: 'Privacy Policy' })).toHaveAttribute('href', '/legal/privacy')
  await expect(consent.getByRole('link', { name: 'licence' })).toHaveAttribute('href', '/legal/content-licence')
})

test('after a new version, signed-in pages wait until it is accepted', async ({ page }) => {
  let accepted = false
  const calls = await mockApi(page, {
    TermsStatus: () => ({ termsVersion: TERMS_VERSION, viewer: { __typename: 'User', id: '01920000-0000-7000-8000-00000000aaaa', termsAccepted: accepted } }),
    AcceptTerms: () => {
      accepted = true
      return { acceptTerms: { ok: true, userErrors: [] } }
    },
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
  })
  await page.goto('/notes')
  const gate = page.getByRole('dialog', { name: 'We have updated our terms' })
  await expect(gate).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(gate).toBeVisible()
  await expect(gate.getByRole('button', { name: 'Close' })).toHaveCount(0)
  await gate.getByRole('button', { name: 'Accept and continue' }).click()
  await expect(gate).toBeHidden()
  expect(calls.find((c) => c.op === 'AcceptTerms')?.variables).toEqual({ version: TERMS_VERSION })
})
