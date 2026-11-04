import { expect, test } from '@playwright/test'
import { TERMS_VERSION } from '../../features/legal/documents'
import { mockApi } from './support/notes-api'

/**
 * §15.2: the Terms, Privacy Policy, content licence and Grievance page — readable, linked where people accept them,
 * accepted again on change.
 */

test('the three documents are public, versioned and linked from every page', async ({ page }) => {
  await page.goto('/legal/terms')
  await expect(page.getByRole('heading', { level: 1, name: 'Terms of Service' })).toBeVisible()
  // The version in effect is the API's (tests/e2e/support/ssr-api.mjs answers 2026-10-08), not this build's newest.
  expect(TERMS_VERSION).not.toBe('2026-10-08')
  await expect(page.getByText('Version 2026-10-08')).toBeVisible()
  await expect(page.getByRole('note')).toContainText('Draft for review')
  await page.getByRole('navigation', { name: 'Legal' }).first().getByRole('link', { name: 'Privacy Policy' }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Privacy Policy' })).toBeVisible()
  await page.goto('/legal/content-licence')
  await expect(page.getByRole('heading', { level: 1, name: 'Content licence' })).toBeVisible()
  // The footer of every page.
  await page.goto('/')
  await expect(page.getByRole('contentinfo').getByRole('link', { name: 'Terms of Service' })).toHaveAttribute('href', '/legal/terms')
})

test('the Grievance page names the officer and commits to 24 hours, 7 days and 36 hours', async ({ page }) => {
  await page.goto('/legal/grievance')
  await expect(page.getByRole('heading', { level: 1, name: 'Grievance Redressal' })).toBeVisible()
  await expect(page.getByText('within 24 hours of receiving your complaint')).toBeVisible()
  await expect(page.getByText('within 7 days, with our reasons')).toBeVisible()
  await expect(page.getByText('we act within 36 hours')).toBeVisible()
  // config/legal.ts is filled in: the officer and the mailbox are named, and no gap is left on the page.
  await expect(page.getByRole('note')).not.toContainText('Still to be filled in')
  await expect(page.locator('mark')).toHaveCount(0)
  await expect(page.getByText('LearnViaNotes Admin', { exact: true })).toBeVisible()
  await expect(page.getByRole('link', { name: 'learnvianotes@gmail.com' })).toHaveAttribute('href', 'mailto:learnvianotes@gmail.com')
  await expect(page.getByRole('contentinfo').getByRole('link', { name: 'Grievance Redressal' })).toHaveAttribute('href', '/legal/grievance')
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
