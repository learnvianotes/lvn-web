'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState, type FormEvent } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import {
  AdminPlansDocument,
  CreateAdminPlanDocument,
  DeleteAdminPlanDocument,
  UpdateAdminPlanDocument,
  type AdminPlanFieldsFragment,
  type GlobalRole,
  type LimitKey,
  type PlanInterval,
} from '@/graphql/generated/graphql'
import { formatBytes, formatDecimal } from '@/features/admin/metrics'
import {
  LIMIT_KEYS,
  canDeactivate,
  currencyIssue,
  deleteChoice,
  entitlementIssues,
  formatPlanPrice,
  isFreePlan,
  majorToMinor,
  minorUnitsText,
  normalizePlanCode,
  planCodeIssue,
  priceMinorIssue,
  type DeleteChoice,
  type EntitlementDraft,
} from '@/features/admin/plans-model'

const SELECT = 'h-11 w-full min-w-0 max-w-full rounded-xl border border-border bg-surface px-3 text-[15px] text-fg'

type Plan = AdminPlanFieldsFragment

export function AdminPlans() {
  const t = useTranslations('adminPlans')
  const { data, error, refetch } = useQuery(AdminPlansDocument, { fetchPolicy: 'cache-and-network' })
  const [editing, setEditing] = useState<Plan | 'new' | null>(null)
  const [removing, setRemoving] = useState<Plan | null>(null)
  if (CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')) return <p className="text-muted">{t('notAllowed')}</p>
  const plans = data?.adminPlans
  if (!plans) return error ? <Alert tone="error">{t('failed')}</Alert> : <p className="text-muted">{t('loading')}</p>
  const per = { month: t('perMonth'), year: t('perYear') }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
          <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
          <p className="text-sm font-medium">{t('priceNote')}</p>
        </div>
        <Button type="button" onClick={() => setEditing('new')}>
          {t('create')}
        </Button>
      </header>
      {plans.length === 0 ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="grid gap-3 [grid-template-columns:repeat(auto-fit,minmax(min(100%,22rem),1fr))]">
        {plans.map((plan) => (
          <li key={plan.id}>
            <article aria-label={plan.name} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold">{plan.name}</h2>
                  <p className="font-mono text-xs text-muted">{plan.code}</p>
                </div>
                <p className="text-xl font-extrabold tracking-tight">{formatPlanPrice(plan.priceMinor, plan.currency, plan.interval, per)}</p>
              </div>
              <p className="flex flex-wrap gap-2 text-xs">
                <span className={plan.active ? 'rounded-full bg-accent-soft px-2 py-0.5 font-medium text-accent' : 'rounded-full bg-surface-2 px-2 py-0.5 text-muted'}>
                  {plan.active ? t('active') : t('inactive')}
                </span>
                <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{t('subscribers', { count: plan.subscriberCount })}</span>
                <span className="rounded-full bg-surface-2 px-2 py-0.5 text-muted">{t(`intervals.${plan.interval}`)}</span>
              </p>
              <div className="grid gap-4 sm:grid-cols-2 sm:[&>*]:min-w-0">
                <div>
                  <h3 className="text-sm font-semibold">{t('features')}</h3>
                  {plan.features.length ? (
                    <ul className="mt-1 list-disc pl-5 text-sm">
                      {plan.features.map((feature) => (
                        <li key={feature}>{feature}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-1 text-sm text-muted">{t('noFeatures')}</p>
                  )}
                </div>
                <div>
                  <h3 className="text-sm font-semibold">{t('limits')}</h3>
                  {plan.entitlements.length ? (
                    <ul className="mt-1 flex flex-col gap-1 text-sm">
                      {plan.entitlements.map((entitlement) => (
                        <li key={`${entitlement.key}-${entitlement.appliesToRole ?? 'any'}`}>
                          {t(`limitKeys.${entitlement.key}`)}: {entitlement.limit == null ? t('unlimited') : formatLimit(entitlement.key, entitlement.limit)}
                          {entitlement.appliesToRole ? ` · ${t(`roles.${entitlement.appliesToRole}`)}` : ''}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="mt-1 text-sm text-muted">{t('noLimits')}</p>
                  )}
                </div>
              </div>
              <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
                <Button type="button" size="sm" variant="secondary" className="h-11 w-full sm:w-auto" aria-label={t('editNamed', { name: plan.name })} onClick={() => setEditing(plan)}>
                  {t('edit')}
                </Button>
                {deleteChoice(plan) === 'blocked' ? (
                  <p className="text-sm text-muted">{t('freeDelete')}</p>
                ) : deleteChoice(plan) === 'deactivate' ? (
                  <>
                    <Button type="button" size="sm" variant="secondary" className="h-11 w-full sm:w-auto" aria-label={t('deactivateNamed', { name: plan.name })} onClick={() => setRemoving(plan)}>
                      {t('deactivate')}
                    </Button>
                    <span className="group relative flex w-full min-w-0 flex-col sm:w-auto">
                      <Button type="button" size="sm" variant="ghost" className="h-11 w-full sm:w-auto" disabled aria-describedby={`plan-delete-${plan.id}`} aria-label={t('deleteNamed', { name: plan.name })}>
                        {t('delete')}
                      </Button>
                      <span id={`plan-delete-${plan.id}`} role="tooltip" className="mt-1 block max-w-full text-xs text-muted sm:pointer-events-none sm:absolute sm:bottom-full sm:right-0 sm:z-10 sm:mb-1 sm:mt-0 sm:w-64 sm:max-w-[70vw] sm:rounded-lg sm:border sm:border-border sm:bg-surface sm:p-2 sm:text-fg sm:opacity-0 sm:shadow sm:group-hover:opacity-100 sm:group-focus-within:opacity-100">
                        {t('hasSubscribers', { count: plan.subscriberCount })}
                      </span>
                    </span>
                  </>
                ) : (
                  <Button type="button" size="sm" variant="ghost" className="h-11 w-full sm:w-auto" aria-label={t('deleteNamed', { name: plan.name })} onClick={() => setRemoving(plan)}>
                    {t('delete')}
                  </Button>
                )}
              </div>
            </article>
          </li>
        ))}
      </ul>
      {editing ? (
        <PlanDialog
          plan={editing === 'new' ? null : editing}
          onClose={() => setEditing(null)}
          onSaved={() => {
            setEditing(null)
            void refetch()
          }}
        />
      ) : null}
      {removing ? (
        <RemoveDialog
          plan={removing}
          onClose={() => setRemoving(null)}
          onDone={() => {
            setRemoving(null)
            void refetch()
          }}
        />
      ) : null}
    </div>
  )
}

function formatLimit(key: LimitKey, limit: string): string {
  if (key === 'STORAGE_BYTES' && /^\d+$/.test(limit)) return formatBytes(limit)
  return formatDecimal(limit)
}

function PlanDialog({ plan, onClose, onSaved }: { plan: Plan | null; onClose: () => void; onSaved: () => void }) {
  const t = useTranslations('adminPlans')
  const [create, creating] = useMutation(CreateAdminPlanDocument)
  const [update, updating] = useMutation(UpdateAdminPlanDocument)
  const [form, setForm] = useState(() => toForm(plan))
  const [errors, setErrors] = useState<Record<string, string>>({})
  const free = plan ? isFreePlan(plan.code) : false
  const set = (patch: Partial<typeof form>) => setForm((current) => ({ ...current, ...patch }))
  const busy = creating.loading || updating.loading

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    const next = collect(form, free)
    if (next.issues) {
      setErrors(Object.fromEntries(Object.entries(next.issues).map(([key, issue]) => [key, t(`issues.${issue}`)])))
      return
    }
    setErrors({})
    try {
      if (!plan) {
        const res = await create({ variables: { input: next.create! } })
        const userError = res.data?.createAdminPlan.userErrors[0]
        if (userError) return setErrors({ [userError.field?.at(-1) ?? 'form']: userError.message })
      } else {
        const res = await update({ variables: { input: { id: plan.id, ...next.update! } } })
        const userError = res.data?.updateAdminPlan.userErrors[0]
        if (userError) return setErrors({ [userError.field?.at(-1) ?? 'form']: userError.message })
      }
      onSaved()
    } catch (err) {
      setErrors({ form: CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed') })
    }
  }

  return (
    <Dialog open onClose={onClose} title={plan ? t('editTitle', { name: plan.name }) : t('createTitle')} wide sheet>
      <form onSubmit={(e) => void submit(e)} className="flex flex-col gap-4">
        <p className="text-sm font-medium">{t('priceNote')}</p>
        {errors.form ? <Alert tone="error">{errors.form}</Alert> : null}
        <div className="grid gap-4 sm:grid-cols-2 sm:[&>*]:min-w-0">
          <Field label={t('code')} error={errors.code} hint={plan ? t('codeLocked') : t('codeHint')}>
            <Input value={form.code} disabled={!!plan} autoCapitalize="characters" maxLength={32} onChange={(e) => set({ code: e.target.value.toUpperCase() })} required={!plan} />
          </Field>
          <Field label={t('name')} error={errors.name}>
            <Input value={form.name} onChange={(e) => set({ name: e.target.value })} required />
          </Field>
          <Field label={t('price')} error={errors.priceMinor ?? errors.price} hint={t('priceHint')}>
            <Input inputMode="decimal" value={form.price} onChange={(e) => set({ price: e.target.value })} />
          </Field>
          <Field label={t('currency')} error={errors.currency}>
            <Input value={form.currency} maxLength={3} autoCapitalize="characters" onChange={(e) => set({ currency: e.target.value.toUpperCase() })} />
          </Field>
          <Field label={t('interval')} error={errors.interval}>
            <select className={SELECT} value={form.interval} onChange={(e) => set({ interval: e.target.value as PlanInterval })}>
              <option value="MONTH">{t('intervals.MONTH')}</option>
              <option value="YEAR">{t('intervals.YEAR')}</option>
              <option value="NONE">{t('intervals.NONE')}</option>
            </select>
          </Field>
          <label className="flex items-center gap-2 self-end text-sm">
            <input type="checkbox" className="size-4 accent-[var(--accent)]" checked={form.active} disabled={free || !canDeactivate({ code: form.code || 'NEW' })} onChange={(e) => set({ active: e.target.checked })} />
            {t('active')}
          </label>
        </div>
        {free ? <p className="text-sm text-muted">{t('freeLocked')}</p> : null}
        <Field label={t('features')} hint={t('featuresHint')} error={errors.features}>
          <textarea value={form.features} onChange={(e) => set({ features: e.target.value })} rows={4} className="w-full rounded-xl border border-border bg-surface px-3 py-2 text-[15px] text-fg" />
        </Field>
        <fieldset className="flex flex-col gap-3">
          <legend className="text-sm font-medium">{t('limits')}</legend>
          <p className="text-xs text-muted">{t('limitsHint')}</p>
          {errors.entitlements ? <p role="alert" className="text-xs font-medium text-red-600 dark:text-red-400">{errors.entitlements}</p> : null}
          {form.entitlements.map((row, index) => (
            <div key={index} className="grid gap-2 xl:grid-cols-[minmax(0,1fr)_8rem_9rem_auto]">
              <select className={SELECT} aria-label={t('limitKey')} value={row.key} onChange={(e) => set({ entitlements: replace(form.entitlements, index, { ...row, key: e.target.value as LimitKey | '' }) })}>
                <option value="">{t('chooseLimit')}</option>
                {LIMIT_KEYS.map((key) => (
                  <option key={key} value={key}>{t(`limitKeys.${key}`)}</option>
                ))}
              </select>
              <Input aria-label={t('limit')} inputMode="decimal" placeholder={t('unlimited')} value={row.limit} onChange={(e) => set({ entitlements: replace(form.entitlements, index, { ...row, limit: e.target.value }) })} />
              <select className={SELECT} aria-label={t('role')} value={row.role} onChange={(e) => set({ entitlements: replace(form.entitlements, index, { ...row, role: e.target.value as GlobalRole | '' }) })}>
                <option value="">{t('anyRole')}</option>
                <option value="STUDENT">{t('roles.STUDENT')}</option>
                <option value="TEACHER">{t('roles.TEACHER')}</option>
                <option value="PLATFORM_ADMIN">{t('roles.PLATFORM_ADMIN')}</option>
              </select>
              <Button type="button" size="sm" variant="ghost" className="h-11 w-full xl:w-auto" aria-label={t('removeLimit', { n: index + 1 })} onClick={() => set({ entitlements: form.entitlements.filter((_, i) => i !== index) })}>
                {t('remove')}
              </Button>
            </div>
          ))}
          <Button type="button" size="sm" variant="secondary" onClick={() => set({ entitlements: [...form.entitlements, { key: '', limit: '', role: '' }] })}>
            {t('addLimit')}
          </Button>
        </fieldset>
        <div className="sticky bottom-0 -mx-4 flex flex-col-reverse gap-2 border-t border-border bg-bg px-4 py-3 sm:-mx-5 sm:flex-row sm:justify-end sm:px-5">
          <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button type="submit" className="h-11 w-full sm:w-auto" disabled={busy}>
            {busy ? t('saving') : t('save')}
          </Button>
        </div>
      </form>
    </Dialog>
  )
}

function RemoveDialog({ plan, onClose, onDone }: { plan: Plan; onClose: () => void; onDone: () => void }) {
  const t = useTranslations('adminPlans')
  const choice: DeleteChoice = deleteChoice(plan)
  const [remove, removing] = useMutation(DeleteAdminPlanDocument)
  const [update, updating] = useMutation(UpdateAdminPlanDocument)
  const [problem, setProblem] = useState<string | null>(null)
  const busy = removing.loading || updating.loading
  const run = async () => {
    setProblem(null)
    try {
      if (choice === 'deactivate') {
        const res = await update({ variables: { input: { id: plan.id, active: false } } })
        const userError = res.data?.updateAdminPlan.userErrors[0]?.message
        if (userError) return setProblem(userError)
      } else if (choice === 'delete') {
        const res = await remove({ variables: { id: plan.id } })
        const userError = res.data?.deleteAdminPlan.userErrors[0]?.message
        if (userError) return setProblem(userError)
      }
      onDone()
    } catch (err) {
      setProblem(CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  return (
    <Dialog open onClose={onClose} title={choice === 'deactivate' ? t('deactivateTitle', { name: plan.name }) : t('deleteTitle', { name: plan.name })} sheet>
      <div className="flex flex-col gap-4">
        <p className="text-sm">{choice === 'deactivate' ? t('hasSubscribers', { count: plan.subscriberCount }) : t('confirmDelete', { name: plan.name })}</p>
        {problem ? <Alert tone="error">{problem}</Alert> : null}
        <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button type="button" className="h-11 w-full sm:w-auto" disabled={busy || choice === 'blocked'} onClick={() => void run()}>
            {choice === 'deactivate' ? t('deactivate') : t('delete')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

type FormState = {
  code: string
  name: string
  price: string
  currency: string
  interval: PlanInterval
  features: string
  active: boolean
  entitlements: EntitlementDraft[]
}

function toForm(plan: Plan | null): FormState {
  if (!plan) return { code: '', name: '', price: '0', currency: 'INR', interval: 'MONTH', features: '', active: true, entitlements: [] }
  return {
    code: plan.code,
    name: plan.name,
    price: minorUnitsText(plan.priceMinor, plan.currency),
    currency: plan.currency,
    interval: plan.interval,
    features: plan.features.join('\n'),
    active: plan.active,
    entitlements: plan.entitlements.map((entitlement) => ({ key: entitlement.key, limit: entitlement.limit ?? '', role: entitlement.appliesToRole ?? '' })),
  }
}

function replace<T>(rows: T[], index: number, row: T): T[] {
  return rows.map((current, i) => (i === index ? row : current))
}

function collect(form: FormState, free: boolean): {
  issues: Record<string, string> | null
  create?: {
    code: string
    name: string
    priceMinor: number
    currency: string
    interval: PlanInterval
    features: string[]
    active: boolean
    entitlements: { key: LimitKey; limit: string | null; appliesToRole: GlobalRole | null }[]
  }
  update?: {
    name: string
    priceMinor: number
    currency: string
    interval: PlanInterval
    features: string[]
    active: boolean
    entitlements: { key: LimitKey; limit: string | null; appliesToRole: GlobalRole | null }[]
  }
} {
  const issues: Record<string, string> = {}
  if (planCodeIssue(form.code)) issues.code = 'code'
  if (!form.name.trim()) issues.name = 'name'
  const currency = form.currency.trim().toUpperCase()
  if (currencyIssue(currency)) issues.currency = 'currency'
  const minor = currencyIssue(currency) ? null : majorToMinor(form.price, currency)
  const priceIssue = priceMinorIssue(minor)
  if (priceIssue) issues.price = priceIssue === 'range' ? 'range' : 'price'
  const entitlementIssue = entitlementIssues(form.entitlements)
  if (entitlementIssue) issues.entitlements = entitlementIssue
  if (Object.keys(issues).length || minor == null) return { issues: { ...issues, ...(minor == null ? { price: issues.price ?? 'price' } : {}) } }
  const shared = {
    name: form.name.trim(),
    priceMinor: minor,
    currency,
    interval: form.interval,
    features: form.features.split('\n').map((line) => line.trim()).filter(Boolean),
    active: free || isFreePlan(form.code) ? true : form.active,
    entitlements: form.entitlements.map((row) => ({
      key: row.key as LimitKey,
      limit: row.limit.trim() ? row.limit.trim() : null,
      appliesToRole: row.role || null,
    })),
  }
  return { issues: null, create: { code: normalizePlanCode(form.code), ...shared }, update: shared }
}
