/* Date of birth — day, month, year with no defaults and no hint of the cut-off (age.ts). */

import { useId } from 'react'
import type { BirthDate } from './age'

const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

export function BirthDateField({ value, onChange, invalid = false }: {
  value: Partial<BirthDate>
  onChange: (next: Partial<BirthDate>) => void
  invalid?: boolean
}) {
  const hint = useId()
  const thisYear = new Date().getFullYear()
  const years = Array.from({ length: 101 }, (_, i) => thisYear - i)
  const pick = (key: keyof BirthDate) => (e: React.ChangeEvent<HTMLSelectElement>) =>
    onChange({ ...value, [key]: e.target.value ? Number(e.target.value) : undefined })

  return (
    <fieldset className="field dob" aria-describedby={hint}>
      <legend>Date of birth</legend>
      <span className="dob-row">
        <select value={value.day ?? ''} onChange={pick('day')} aria-label="Day" aria-invalid={invalid && !value.day} autoComplete="bday-day">
          <option value="">Day</option>
          {Array.from({ length: 31 }, (_, i) => <option key={i} value={i + 1}>{i + 1}</option>)}
        </select>
        <select value={value.month ?? ''} onChange={pick('month')} aria-label="Month" aria-invalid={invalid && !value.month} autoComplete="bday-month">
          <option value="">Month</option>
          {MONTHS.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
        </select>
        <select value={value.year ?? ''} onChange={pick('year')} aria-label="Year" aria-invalid={invalid && !value.year} autoComplete="bday-year">
          <option value="">Year</option>
          {years.map((y) => <option key={y} value={y}>{y}</option>)}
        </select>
      </span>
      <span id={hint} className="field-hint">Used once to check your age — we don’t keep it.</span>
    </fieldset>
  )
}
