import { readFileSync } from 'node:fs'
import { expect, test } from '@playwright/test'
import { E2E_GIT_SHA } from './support/constants'

const { version } = JSON.parse(readFileSync(new URL('../../package.json', import.meta.url), 'utf8')) as { version: string }

test('the running version is on /version and in the footer', async ({ page, request }) => {
  const res = await request.get('/version')
  expect(res.status()).toBe(200)
  expect(res.headers()['content-type']).toMatch(/application\/json/)
  expect(await res.json()).toEqual({ version, commit: E2E_GIT_SHA.slice(0, 12) })
  await page.goto('/')
  await expect(page.getByRole('contentinfo').getByText(`v${version}`, { exact: true })).toBeVisible()
})
