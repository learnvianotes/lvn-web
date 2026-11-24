'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { attempt } from '@/features/groups/shared'
import { NotificationSettingsDocument, UpdateNotificationSettingsDocument, type NotificationCategory, type NotificationSettingsFieldsFragment } from '@/graphql/generated/graphql'

const ZONES = ['Asia/Kolkata', 'Asia/Dubai', 'Asia/Singapore', 'Europe/London', 'Europe/Berlin', 'America/New_York', 'America/Los_Angeles', 'Australia/Sydney', 'UTC']

/**
 * /profile/notifications (lvn-backend ADR-0050): push per kind of notification, emails for class announcements and the
 * weekly digest, and quiet hours. Every change saves at once.
 */
export function NotificationSettings() {
  const t = useTranslations('settings')
  const { data, loading, error, refetch } = useQuery(NotificationSettingsDocument, { fetchPolicy: 'cache-and-network' })
  const [update] = useMutation(UpdateNotificationSettingsDocument)
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const s = data?.notificationSettings
  if (!s) return error && !loading ? <LoadFailed onRetry={refetch} /> : <Loading label={t('loading')} />
  const save = async (input: SettingsInput) => {
    // Shown at once (the switches are the server's state), then replaced by what the API answers.
    const next = applied(s, input)
    const problem = await attempt(
      () =>
        update({
          variables: { input },
          optimisticResponse: { updateNotificationSettings: { settings: next, userErrors: [] } },
          update: (cache, res) => {
            const settings = res.data?.updateNotificationSettings.settings
            if (settings) cache.writeQuery({ query: NotificationSettingsDocument, data: { notificationSettings: settings } })
          },
        }),
      t('failed'),
    )
    setMessage(problem ? { ok: false, text: problem } : { ok: true, text: t('saved') })
  }
  const zones = ZONES.includes(s.timeZone) ? ZONES : [s.timeZone, ...ZONES]
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-8">
      <header>
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-bad'}>
          {message.text}
        </p>
      ) : null}
      <section aria-labelledby="kinds" className="flex flex-col gap-3">
        <h2 id="kinds" className="font-semibold">
          {t('kinds')}
        </h2>
        {!s.pushAvailable ? <p className="rounded-xl bg-surface-2 px-3 py-2 text-xs text-muted">{t('pushOff')}</p> : null}
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted">
              <th className="py-2 font-semibold">{t('kind')}</th>
              <th className="w-24 py-2 text-center font-semibold">{t('push')}</th>
              <th className="w-24 py-2 text-center font-semibold">{t('email')}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {s.categories.map((c) => (
              <CategoryRow key={c.category} row={c} onChange={(input) => void save({ categories: [input] })} />
            ))}
          </tbody>
        </table>
      </section>
      <section aria-labelledby="quiet" className="flex flex-col gap-3">
        <h2 id="quiet" className="font-semibold">
          {t('quiet')}
        </h2>
        <p className="text-sm text-muted">{t('quietHint')}</p>
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-semibold">{t('from')}</span>
            <input type="time" defaultValue={s.quietStart} onBlur={(e) => e.target.value && e.target.value !== s.quietStart && void save({ quietStart: e.target.value })} className="h-10 rounded-xl border border-border bg-surface px-3" />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-semibold">{t('to')}</span>
            <input type="time" defaultValue={s.quietEnd} onBlur={(e) => e.target.value && e.target.value !== s.quietEnd && void save({ quietEnd: e.target.value })} className="h-10 rounded-xl border border-border bg-surface px-3" />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-semibold">{t('timeZone')}</span>
            <select value={s.timeZone} onChange={(e) => void save({ timeZone: e.target.value })} className="h-10 rounded-xl border border-border bg-surface px-3">
              {zones.map((z) => (
                <option key={z} value={z}>
                  {z.replace('_', ' ')}
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>
      <section aria-labelledby="digest" className="flex flex-col gap-2">
        <h2 id="digest" className="font-semibold">
          {t('digest')}
        </h2>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={s.weeklyDigest} onChange={(e) => void save({ weeklyDigest: e.target.checked })} />
          {t('digestLabel')}
        </label>
      </section>
      {/* productEmails defaults to true on the server (lvn-backend). Turning it off leaves the product audience. */}
      <section className="flex flex-col gap-2">
        <h2 id="product-emails" className="font-semibold">
          {t('productEmails')}
        </h2>
        <label className="flex items-start gap-2 text-sm">
          <input name="productEmails" type="checkbox" className="mt-0.5" checked={s.productEmails} aria-labelledby="product-emails" aria-describedby="product-emails-hint" onChange={(e) => void save({ productEmails: e.target.checked })} />
          <span id="product-emails-hint" className="text-muted">
            {t('productEmailsHint')}
          </span>
        </label>
      </section>
      <p className="text-xs text-muted">{t('devices', { count: s.devices })}</p>
    </div>
  )
}

type SettingsInput = { categories?: { category: NotificationCategory; push?: boolean; email?: boolean }[]; quietStart?: string; quietEnd?: string; timeZone?: string; weeklyDigest?: boolean; productEmails?: boolean }

/** What the settings become once the API accepts the change. */
function applied(s: NotificationSettingsFieldsFragment, input: SettingsInput): NotificationSettingsFieldsFragment {
  const changed = new Map((input.categories ?? []).map((c) => [c.category, c]))
  return {
    ...s,
    ...(input.quietStart !== undefined ? { quietStart: input.quietStart } : {}),
    ...(input.quietEnd !== undefined ? { quietEnd: input.quietEnd } : {}),
    ...(input.timeZone !== undefined ? { timeZone: input.timeZone } : {}),
    ...(input.weeklyDigest !== undefined ? { weeklyDigest: input.weeklyDigest } : {}),
    ...(input.productEmails !== undefined ? { productEmails: input.productEmails } : {}),
    categories: s.categories.map((c) => {
      const d = changed.get(c.category)
      return d ? { ...c, ...(d.push !== undefined ? { push: d.push } : {}), ...(d.email !== undefined && c.email !== null ? { email: d.email } : {}) } : c
    }),
  }
}

function CategoryRow({ row, onChange }: { row: NotificationSettingsFieldsFragment['categories'][number]; onChange: (input: { category: NotificationCategory; push?: boolean; email?: boolean }) => void }) {
  const t = useTranslations('settings')
  const label = t(`category.${row.category}`)
  return (
    <tr>
      <td className="py-2.5">{label}</td>
      <td className="text-center">
        <input type="checkbox" aria-label={t('pushFor', { kind: label })} checked={row.push} onChange={(e) => onChange({ category: row.category, push: e.target.checked })} />
      </td>
      <td className="text-center">
        {row.email === null ? (
          <span className="text-xs text-muted" aria-label={t('noEmail')}>
            —
          </span>
        ) : (
          <input type="checkbox" aria-label={t('emailFor', { kind: label })} checked={row.email} onChange={(e) => onChange({ category: row.category, email: e.target.checked })} />
        )}
      </td>
    </tr>
  )
}
