'use client'

import { useMutation } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { attempt } from '@/features/groups/shared'
import { ReactDocument, type ReactionKind, type ReactionsFieldsFragment, type ReactionTargetType } from '@/graphql/generated/graphql'

const KINDS: { kind: ReactionKind; emoji: string }[] = [
  { kind: 'LIKE', emoji: '👍' },
  { kind: 'HELPFUL', emoji: '💡' },
  { kind: 'CELEBRATE', emoji: '🎉' },
]

/**
 * Three reactions, one per person (lvn-backend ADR-0047). Counts are exact for the owner and in groups and classes;
 * on a public note others see a milestone or nothing (ADR-0027).
 */
export function ReactionBar({ target, reactions, disabled, onChanged, size = 'md' }: { target: { type: ReactionTargetType; id: string }; reactions: ReactionsFieldsFragment; disabled?: boolean; onChanged: () => void; size?: 'sm' | 'md' }) {
  const t = useTranslations('discussion')
  const [react, reacting] = useMutation(ReactDocument)
  const [error, setError] = useState<string | null>(null)
  const press = async (kind: ReactionKind) => {
    const next = reactions.viewerReaction === kind ? null : kind
    setError(await attempt(() => react({ variables: { target, kind: next } }), t('failed')))
    onChanged()
  }
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {KINDS.map(({ kind, emoji }) => {
        const c = reactions.counts.find((x) => x.kind === kind)
        const mine = reactions.viewerReaction === kind
        const number = c?.count ? (c.atLeast ? `${c.count.toLocaleString('en-IN')}+` : String(c.count)) : ''
        return (
          <button
            key={kind}
            type="button"
            aria-pressed={mine}
            aria-label={t(`react.${kind}`)}
            title={t(`react.${kind}`)}
            disabled={disabled || reacting.loading}
            onClick={() => void press(kind)}
            className={`inline-flex items-center gap-1 rounded-full border transition disabled:opacity-50 ${size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-sm'} ${mine ? 'border-accent bg-accent-soft text-accent' : 'border-border text-muted hover:border-accent/50 hover:text-fg'}`}
          >
            <span aria-hidden>{emoji}</span>
            {number ? <span className="tabular-nums">{number}</span> : null}
          </button>
        )
      })}
      {error ? (
        <span role="alert" className="text-xs text-red-600 dark:text-red-400">
          {error}
        </span>
      ) : null}
    </div>
  )
}
