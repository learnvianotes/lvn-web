'use client'

import { useId, useMemo, useState } from 'react'
import { useTranslations } from 'next-intl'
import { filterModels, groupModels, type ListedModel } from '@/features/ai/admin/catalog'
import { cn } from '@/lib/cn'

const SELECT = 'w-full min-w-0 max-w-full rounded-xl border border-border bg-surface px-3 py-2 text-[15px] text-fg'

/**
 * A labelled select of the models that support one use, with a search box because a provider can list dozens.
 * The current value stays choosable when the account no longer offers it, so a rejected save can say why.
 */
export function ModelSelect({
  label,
  hint,
  error,
  models,
  value,
  onChange,
  searchLabel,
  allowEmpty,
  required,
}: {
  label: string
  hint?: string
  error?: string
  models: readonly ListedModel[]
  value: string
  onChange: (value: string) => void
  searchLabel: string
  allowEmpty?: boolean
  required?: boolean
}) {
  const t = useTranslations('aiAdmin')
  const id = useId()
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const [query, setQuery] = useState('')
  const groups = useMemo(() => groupModels(filterModels(models, query)), [models, query])
  const shown = new Set(groups.flatMap((group) => group.models.map((model) => model.id)))
  const keepCurrent = Boolean(value) && !shown.has(value) && !query.trim()
  const describedBy = [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(' ') || undefined
  const rows = Math.min(8, Math.max(2, shown.size + (allowEmpty || keepCurrent ? 1 : 0)))
  return (
    <div className="flex min-w-0 max-w-full flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        aria-label={searchLabel}
        placeholder={searchLabel}
        className="h-11 w-full min-w-0 max-w-full rounded-xl border border-border bg-surface px-3 text-[15px] text-fg placeholder:text-muted"
      />
      <select
        id={id}
        size={rows}
        value={value}
        required={required}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        onChange={(e) => onChange(e.target.value)}
        className={cn(SELECT, error && 'border-red-500')}
      >
        {allowEmpty ? <option value="">{t('clearModel')}</option> : null}
        {!allowEmpty && !value ? <option value="">{t('chooseModel')}</option> : null}
        {keepCurrent ? <option value={value}>{t('notOffered', { model: value })}</option> : null}
        {groups.map((group) => (
          <optgroup key={group.kind} label={t(`kinds.${group.kind}`)}>
            {group.models.map((model) => (
              <option key={model.id} value={model.id}>
                {model.id}
              </option>
            ))}
          </optgroup>
        ))}
        {groups.length === 0 && !keepCurrent ? (
          <option value={value} disabled>
            {t('noModelMatches')}
          </option>
        ) : null}
      </select>
      {hint ? (
        <p id={hintId} className="text-xs text-muted">
          {hint}
        </p>
      ) : null}
      {error ? (
        <p id={errorId} role="alert" className="text-xs font-medium text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </div>
  )
}
