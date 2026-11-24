import { expect, test, type Page, type Route } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Plans a person can see (contracts 0.70.0): cards for everyone, usage for someone signed in, and no checkout.
 */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const free = {
  __typename: 'PublicPlan',
  id: '01920000-0000-7000-8000-000000000f01',
  code: 'FREE',
  name: 'Free',
  priceMinor: 0,
  currency: 'INR',
  interval: 'NONE',
  features: ['Read public notes'],
  current: true,
  limits: [{ __typename: 'PlanLimit', key: 'NOTES_OWNED', label: 'Notes you can keep', limit: '20' }],
}
const plus = {
  __typename: 'PublicPlan',
  id: '01920000-0000-7000-8000-000000000f02',
  code: 'PLUS',
  name: 'Plus',
  priceMinor: 49900,
  currency: 'INR',
  interval: 'MONTH',
  features: ['AI on your notes', 'Uploads'],
  current: false,
  limits: [
    { __typename: 'PlanLimit', key: 'NOTES_OWNED', label: 'Notes you can keep', limit: null },
    { __typename: 'PlanLimit', key: 'AI_REQUESTS_DAILY', label: 'AI asks a day', limit: '200' },
  ],
}
const plans = () => ({ plans: [free, plus] })
const myPlan = () => ({
  myPlan: {
    __typename: 'MyPlan',
    plan: free,
    usage: [
      { __typename: 'PlanUsage', key: 'NOTES_OWNED', label: 'Notes you can keep', used: '12', limit: '20', resetsAt: null },
      { __typename: 'PlanUsage', key: 'AI_REQUESTS_DAILY', label: 'AI asks a day', used: '7', limit: '20', resetsAt: '2026-10-24T18:30:00.000Z' },
      { __typename: 'PlanUsage', key: 'STORAGE_BYTES', label: 'Storage', used: '0', limit: null, resetsAt: null },
    ],
  },
})

async function signedOut(page: Page) {
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { operationName?: string; query?: string }
    const op = body.operationName ?? ''
    if (op === 'Refresh' || (body.query ?? '').includes('refreshSession')) {
      return route.fulfill({ json: { data: null, errors: [{ message: 'Session ended', extensions: { code: 'UNAUTHENTICATED' } }] } })
    }
    if (op === 'Plans') return route.fulfill({ json: { data: plans() } })
    if (op === 'MyPlan') return route.fulfill({ status: 500, json: { errors: [{ message: 'MyPlan should not be asked while signed out' }] } })
    return route.fulfill({ json: { data: {} } })
  })
}

test('signed-out visitors see the plans and no way to buy one', async ({ page }) => {
  await signedOut(page)
  await page.goto('/plans')
  await expect(page.getByRole('heading', { name: 'Plans', level: 1 })).toBeVisible()
  const freeCard = page.getByRole('article', { name: 'Free' })
  await expect(freeCard).toContainText('Free')
  await expect(freeCard).toContainText('Notes you can keep: 20')
  const plusCard = page.getByRole('article', { name: 'Plus' })
  await expect(plusCard).toContainText(/₹\s?499\/month/)
  await expect(plusCard).toContainText('Unlimited')
  await expect(plusCard).toContainText('AI asks a day: 200')
  await expect(page.getByRole('button', { name: /buy|checkout|subscribe/i })).toHaveCount(0)
  await expect(page.getByRole('link', { name: 'Contact us to change plan' })).toHaveAttribute('href', '/legal/grievance')
  await expect(page.getByRole('link', { name: 'Sign in to see how much of your plan you have used.' })).toHaveAttribute('href', '/sign-in?next=%2Fplans')
  await expect(page.getByRole('region', { name: 'Your plan' })).toHaveCount(0)
})

test('a signed-in person sees their plan, usage, and the current plan highlighted', async ({ page }) => {
  await mockApi(page, { Plans: plans, MyPlan: myPlan }, viewerExtras)
  await page.goto('/plans')
  const yours = page.getByRole('region', { name: 'Your plan' })
  await expect(yours).toContainText('Free')
  await expect(yours.getByRole('meter', { name: 'Notes you can keep' })).toHaveAttribute('aria-valuenow', '12')
  await expect(yours.getByRole('meter', { name: 'Notes you can keep' })).toHaveAttribute('aria-valuemax', '20')
  await expect(yours.getByText('12 / 20')).toBeVisible()
  await expect(yours.getByText(/Resets/)).toBeVisible()
  await expect(yours.getByText('Unlimited').first()).toBeVisible()
  const freeCard = page.getByRole('article', { name: 'Free' })
  await expect(freeCard).toContainText('Current plan')
  await expect(page.getByRole('button', { name: /buy|checkout|subscribe/i })).toHaveCount(0)
})

test('the account page links to plans', async ({ page }) => {
  await mockApi(page, { Plans: plans, MyPlan: myPlan, MyDataExports: () => ({ myDataExports: [] }), NoteImports: () => ({ noteImports: [] }) }, viewerExtras)
  await page.goto('/profile')
  await page.getByRole('link', { name: 'Your plan' }).click()
  await expect(page).toHaveURL(/\/plans$/)
  await expect(page.getByRole('heading', { name: 'Plans', level: 1 })).toBeVisible()
})
