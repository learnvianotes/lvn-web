'use client'

/**
 * Small SVG charts for the admin usage dashboard. No chart library: a line chart, a bar list and a heatmap table are
 * all the dashboard needs. Every chart carries its numbers as a real <table> as well, for screen readers and for
 * anyone who prefers reading figures.
 */
import { useFormatter, useTranslations } from 'next-intl'
import { useId } from 'react'
import { heat, linePoints, niceMax, retentionWidth } from './shape'

const COLORS = ['var(--accent)', 'var(--good)', 'var(--warn)', 'var(--def)', 'var(--bad)']
const W = 640
const H = 180

export type LineSeries = { key: string; label: string; values: number[] }

/** One or more series over the same buckets (dates). */
export function LineChart({ title, dates, series }: { title: string; dates: string[]; series: LineSeries[] }) {
  const t = useTranslations('adminUsage.chart')
  const format = useFormatter()
  const id = useId()
  const max = niceMax(Math.max(0, ...series.flatMap((s) => s.values)))
  return (
    <figure aria-labelledby={`${id}-title`} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
      <figcaption id={`${id}-title`} className="font-semibold">{title}</figcaption>
      {!dates.length ? (
        <p className="text-sm text-muted">{t('empty')}</p>
      ) : (
        <>
          <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted" aria-hidden>
            {series.map((s, i) => (
              <li key={s.key} className="flex items-center gap-1.5">
                <span className="inline-block h-0.5 w-4" style={{ background: COLORS[i % COLORS.length] }} />
                {s.label}
              </li>
            ))}
          </ul>
          <svg viewBox={`-40 -8 ${W + 48} ${H + 28}`} className="h-auto w-full" aria-hidden focusable="false" data-testid="line-chart">
            {[0, 0.5, 1].map((f) => (
              <g key={f}>
                <line x1={0} x2={W} y1={H - f * H} y2={H - f * H} stroke="var(--border)" strokeWidth={1} />
                <text x={-6} y={H - f * H + 4} textAnchor="end" fontSize={11} fill="var(--muted)">{format.number(max * f)}</text>
              </g>
            ))}
            <text x={0} y={H + 18} fontSize={11} fill="var(--muted)">{dates[0]}</text>
            {dates.length > 1 ? <text x={W} y={H + 18} textAnchor="end" fontSize={11} fill="var(--muted)">{dates[dates.length - 1]}</text> : null}
            {series.map((s, i) => (
              <polyline key={s.key} points={linePoints(s.values, W, H, max)} fill="none" stroke={COLORS[i % COLORS.length]} strokeWidth={2} strokeLinejoin="round" />
            ))}
          </svg>
          <DataTable caption={title} header={[t('date'), ...series.map((s) => s.label)]} rows={dates.map((d, i) => [d, ...series.map((s) => format.number(s.values[i] ?? 0))])} />
        </>
      )}
    </figure>
  )
}

export type Bar = { key: string; label: string; value: number; display?: string }

/** Horizontal bars, largest first as given. */
export function BarList({ title, bars, valueLabel, note }: { title: string; bars: Bar[]; valueLabel: string; note?: string | null }) {
  const t = useTranslations('adminUsage.chart')
  const format = useFormatter()
  const id = useId()
  const max = Math.max(1, ...bars.map((b) => b.value))
  return (
    <figure aria-labelledby={`${id}-title`} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
      <figcaption id={`${id}-title`} className="font-semibold">{title}</figcaption>
      {!bars.length ? <p className="text-sm text-muted">{t('empty')}</p> : null}
      <ul className="flex flex-col gap-2" aria-hidden>
        {bars.map((bar) => (
          <li key={bar.key} className="flex flex-col gap-1 text-sm">
            <span className="flex items-baseline justify-between gap-3">
              <span className="truncate">{bar.label}</span>
              <span className="font-medium">{bar.display ?? format.number(bar.value)}</span>
            </span>
            <span className="h-2 rounded-full bg-surface-2">
              <span className="block h-2 rounded-[10px] bg-accent" style={{ width: `${(Math.max(0, bar.value) / max) * 100}%` }} />
            </span>
          </li>
        ))}
      </ul>
      {bars.length ? <DataTable caption={title} header={[t('name'), valueLabel]} rows={bars.map((b) => [b.label, b.display ?? format.number(b.value)])} /> : null}
      {note ? <p className="text-xs text-muted">{note}</p> : null}
    </figure>
  )
}

/** Retention cohorts: one row per sign-up week, one column per week since. The table is the chart. */
export function RetentionHeatmap({ cohorts }: { cohorts: { start: string; size: number; returned: number[] }[] }) {
  const t = useTranslations('adminUsage.retention')
  const format = useFormatter()
  const width = retentionWidth(cohorts)
  const pct = (v: number) => format.number(v, { style: 'percent', maximumFractionDigits: 1 })
  return (
    <div className="overflow-x-auto rounded-2xl border border-border bg-surface p-4">
      <table className="w-full border-separate border-spacing-0.5 text-xs" data-testid="retention-heatmap">
        <caption className="pb-2 text-left text-sm font-semibold">{t('caption')}</caption>
        <thead>
          <tr>
            <th scope="col" className="px-2 py-1 text-left font-medium text-muted">{t('cohort')}</th>
            <th scope="col" className="px-2 py-1 text-right font-medium text-muted">{t('size')}</th>
            {Array.from({ length: width }, (_, i) => (
              <th key={i} scope="col" className="px-2 py-1 text-center font-medium text-muted">{t('week', { n: i })}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cohorts.map((c) => (
            <tr key={c.start}>
              <th scope="row" className="whitespace-nowrap px-2 py-1 text-left font-medium">{c.start}</th>
              <td className="px-2 py-1 text-right">{format.number(c.size)}</td>
              {Array.from({ length: width }, (_, i) => {
                const v = c.returned[i]
                if (v === undefined) return <td key={i} className="px-2 py-1" />
                const s = heat(v)
                return (
                  <td
                    key={i}
                    className="rounded px-2 py-1 text-center"
                    style={{ background: `color-mix(in srgb, var(--accent) ${Math.round(s * 85)}%, transparent)`, color: s > 0.5 ? 'var(--accent-fg)' : undefined }}
                  >
                    {pct(v)}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** The figures behind a chart, folded away but always in the page. */
export function DataTable({ caption, header, rows }: { caption: string; header: string[]; rows: (string | number)[][] }) {
  const t = useTranslations('adminUsage.chart')
  return (
    <details className="text-sm">
      <summary className="cursor-pointer text-muted">{t('showTable')}</summary>
      <div className="overflow-x-auto pt-2">
        <table className="w-full text-left text-sm">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr>
              {header.map((h) => (
                <th key={h} scope="col" className="border-b border-border px-2 py-1 font-medium text-muted">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) =>
                  j === 0 ? <th key={j} scope="row" className="px-2 py-1 font-normal">{cell}</th> : <td key={j} className="px-2 py-1">{cell}</td>,
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  )
}
