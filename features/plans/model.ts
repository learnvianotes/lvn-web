import type { PlanInterval } from '@/graphql/generated/graphql'
import { formatDecimal } from '@/features/admin/metrics'
import { formatPlanPrice } from '@/features/admin/plans-model'

/** ₹ from minor units, or the free label when the price is zero. */
export function publicPlanPrice(minor: number, currency: string, interval: PlanInterval, per: { month: string; year: string }, freeLabel: string): string {
  if (minor <= 0) return freeLabel
  return formatPlanPrice(minor, currency, interval, per)
}

/** Share of a limit that is used, from 0 to 1. Null when the limit is unlimited or not a number. */
export function usageRatio(used: string, limit: string | null | undefined): number | null {
  if (limit == null || limit === '') return null
  const usedN = Number(used)
  const limitN = Number(limit)
  if (!Number.isFinite(usedN) || !Number.isFinite(limitN) || limitN <= 0) return null
  return Math.min(1, Math.max(0, usedN / limitN))
}

export function usageText(used: string, limit: string | null | undefined, unlimited: string): string {
  if (limit == null || limit === '') return unlimited
  return `${formatDecimal(used)} / ${formatDecimal(limit)}`
}

export function formatResetsAt(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' }).format(date)
}
