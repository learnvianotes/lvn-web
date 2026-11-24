'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { Alert } from '@/components/ui/alert'
import { formatDecimal } from '@/features/admin/metrics'
import { formatResetsAt, publicPlanPrice, usageRatio, usageText } from '@/features/plans/model'
import { MyPlanDocument, PlansDocument, type PublicPlanFieldsFragment } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { useSession } from '@/state/session'

type Plan = PublicPlanFieldsFragment

export function PlansPage() {
  const t = useTranslations('plans')
  const signedIn = useSession((state) => state.status === 'signed-in')
  const plans = useQuery(PlansDocument, { fetchPolicy: 'cache-and-network' })
  const mine = useQuery(MyPlanDocument, { skip: !signedIn, fetchPolicy: 'cache-and-network' })
  const per = { month: t('perMonth'), year: t('perYear') }
  const list = plans.data?.plans
  const myPlan = mine.data?.myPlan

  return (
    <div className="mx-auto flex w-full min-w-0 max-w-5xl flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight sm:text-3xl">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
      </header>

      {signedIn && myPlan ? (
        <section aria-label={t('yours')} className="flex flex-col gap-4 rounded-2xl border border-accent/40 bg-accent-soft/40 p-4 sm:p-5">
          <div className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold">{t('yours')}</h2>
              <p className="text-sm text-muted">{myPlan.plan.name}</p>
            </div>
            <p className="text-xl font-semibold tracking-tight">{publicPlanPrice(myPlan.plan.priceMinor, myPlan.plan.currency, myPlan.plan.interval, per, t('free'))}</p>
          </div>
          {myPlan.usage.length ? (
            <ul className="flex flex-col gap-3">
              {myPlan.usage.map((item) => {
                const ratio = usageRatio(item.used, item.limit)
                return (
                  <li key={item.key} className="flex flex-col gap-1.5">
                    <div className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
                      <span className="font-medium">{item.label}</span>
                      <span className="text-muted">{usageText(item.used, item.limit, t('unlimited'))}</span>
                    </div>
                    {ratio == null ? (
                      <p className="text-xs text-muted">{t('unlimited')}</p>
                    ) : (
                      <div
                        role="meter"
                        aria-label={item.label}
                        aria-valuemin={0}
                        aria-valuemax={Number(item.limit)}
                        aria-valuenow={Math.min(Number(item.used), Number(item.limit))}
                        aria-valuetext={usageText(item.used, item.limit, t('unlimited'))}
                        className="h-2 overflow-hidden rounded-full bg-surface-2"
                      >
                        <div className={cn('h-full rounded-full', ratio >= 1 ? 'bg-amber-600' : 'bg-accent')} style={{ width: `${Math.round(ratio * 100)}%` }} />
                      </div>
                    )}
                    {item.resetsAt ? <p className="text-xs text-muted">{t('resets', { when: formatResetsAt(item.resetsAt) })}</p> : null}
                  </li>
                )
              })}
            </ul>
          ) : (
            <p className="text-sm text-muted">{t('noUsage')}</p>
          )}
        </section>
      ) : signedIn && mine.error ? (
        <Alert tone="error">{t('yoursFailed')}</Alert>
      ) : !signedIn ? (
        <p className="text-sm text-muted">
          <Link href="/sign-in?next=%2Fplans" className="font-medium text-accent hover:underline">
            {t('signIn')}
          </Link>
        </p>
      ) : null}

      {list ? (
        list.length ? (
          <ul className="grid gap-4 [grid-template-columns:repeat(auto-fit,minmax(min(100%,17rem),1fr))]">
            {list.map((plan) => (
              <li key={plan.id}>
                <PlanCard plan={plan} per={per} />
              </li>
            ))}
          </ul>
        ) : (
          <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p>
        )
      ) : plans.error ? (
        <Alert tone="error">{t('failed')}</Alert>
      ) : (
        <p className="text-muted">{t('loading')}</p>
      )}

      <p className="text-sm text-muted">
        <Link href="/legal/grievance" className="font-medium text-accent hover:underline">
          {t('contact')}
        </Link>
      </p>
    </div>
  )
}

function PlanCard({ plan, per }: { plan: Plan; per: { month: string; year: string } }) {
  const t = useTranslations('plans')
  return (
    <article aria-label={plan.name} className={cn('flex h-full flex-col gap-4 rounded-2xl border bg-surface p-4 sm:p-5', plan.current ? 'border-accent ring-2 ring-accent/30' : 'border-border')}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h2 className="text-lg font-semibold">{plan.name}</h2>
          <p className="text-xs text-muted">{t(`intervals.${plan.interval}`)}</p>
        </div>
        <p className="text-xl font-semibold tracking-tight">{publicPlanPrice(plan.priceMinor, plan.currency, plan.interval, per, t('free'))}</p>
      </div>
      {plan.current ? <p className="w-fit rounded-[10px] bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent">{t('current')}</p> : null}
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
        {plan.limits.length ? (
          <ul className="mt-1 flex flex-col gap-1 text-sm">
            {plan.limits.map((limit) => (
              <li key={limit.key}>
                {limit.label}: {limit.limit == null ? t('unlimited') : formatDecimal(limit.limit)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-1 text-sm text-muted">{t('noLimits')}</p>
        )}
      </div>
    </article>
  )
}
