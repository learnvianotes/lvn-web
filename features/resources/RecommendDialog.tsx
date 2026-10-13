'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useLazyQuery, useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { MyClassroomsDocument, MyGroupsDocument, RecommendResourceDocument, SearchDocument } from '@/graphql/generated/graphql'
import { RESOURCE_LIMITS } from '@/lib/contracts/validation'

type To = { kind: 'person'; id: string; name: string } | { kind: 'group'; id: string; name: string } | { kind: 'class'; id: string; name: string }

/**
 * Recommending a resource with a reason (lvn-backend ADR-0075): to a person (the API decides whom: people one follows,
 * is connected to or shares a group or class with), to a group one may post in, or to a class one teaches.
 */
export function RecommendDialog({ resourceId, open, onClose }: { resourceId: string; open: boolean; onClose: () => void }) {
  const t = useTranslations('resources.recommend')
  const [tab, setTab] = useState<To['kind']>('person')
  const [to, setTo] = useState<To | null>(null)
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [sent, setSent] = useState<string | null>(null)
  const [recommend, sending] = useMutation(RecommendResourceDocument)
  const groups = useQuery(MyGroupsDocument, { skip: !open || tab !== 'group' })
  const classes = useQuery(MyClassroomsDocument, { skip: !open || tab !== 'class' })
  const [query, setQuery] = useState('')
  const [find, found] = useLazyQuery(SearchDocument)
  useEffect(() => {
    if (tab !== 'person' || query.trim().length < 2) return
    const timer = setTimeout(() => void find({ variables: { query: query.trim(), scopes: ['PEOPLE'], first: 8 } }), 250)
    return () => clearTimeout(timer)
  }, [query, tab, find])

  const close = () => {
    setTo(null)
    setReason('')
    setError(null)
    setSent(null)
    onClose()
  }
  const send = async () => {
    if (!to) return
    setError(null)
    try {
      const place = to.kind === 'person' ? { userId: to.id } : to.kind === 'group' ? { groupId: to.id } : { classroomId: to.id }
      const res = await recommend({ variables: { input: { resourceId, to: place, reason: reason.trim() || null } } })
      const problem = res.data?.recommendResource.userErrors[0]?.message
      if (problem) setError(problem)
      else setSent(to.name)
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }
  const choice = (option: To) => (
    <li key={`${option.kind}:${option.id}`}>
      <button type="button" role="radio" aria-checked={to?.id === option.id} onClick={() => setTo(option)} className={`w-full rounded-lg px-3 py-2 text-left text-sm ${to?.id === option.id ? 'bg-accent-soft font-semibold text-accent' : 'hover:bg-surface-2'}`}>
        {option.name}
      </button>
    </li>
  )
  const myGroups = (groups.data?.myGroups ?? []).map((g) => ({ kind: 'group' as const, id: g.id, name: g.name }))
  const myClasses = (classes.data?.myClassrooms ?? []).filter((c) => c.viewerRole === 'TEACHER' || c.viewerRole === 'TA').map((c) => ({ kind: 'class' as const, id: c.id, name: c.name }))
  const people = (found.data?.search.people ?? []).map((p) => ({ kind: 'person' as const, id: p.id, name: `${p.displayName} (@${p.handle})` }))
  return (
    <Dialog open={open} onClose={close} title={t('title')}>
      {sent ? (
        <div className="flex flex-col gap-4">
          <p role="status">{t('sent', { to: sent })}</p>
          <Button onClick={close} className="self-end">
            {t('done')}
          </Button>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          <div role="tablist" className="flex gap-1 rounded-xl bg-surface-2 p-1">
            {(['person', 'group', 'class'] as const).map((k) => (
              <button
                key={k}
                type="button"
                role="tab"
                aria-selected={tab === k}
                onClick={() => {
                  setTab(k)
                  setTo(null)
                }}
                className={`flex-1 rounded-lg px-3 py-1.5 text-sm font-semibold ${tab === k ? 'bg-surface shadow-sm' : 'text-muted'}`}
              >
                {t(`tab.${k}`)}
              </button>
            ))}
          </div>
          {tab === 'person' ? (
            <>
              <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('findPerson')} aria-label={t('findPerson')} className="h-10 rounded-xl border border-border bg-bg px-3 text-sm" />
              <p className="text-xs text-muted">{t('personHint')}</p>
            </>
          ) : null}
          <ul role="radiogroup" aria-label={t(`tab.${tab}`)} className="flex max-h-56 flex-col gap-1 overflow-y-auto">
            {(tab === 'person' ? people : tab === 'group' ? myGroups : myClasses).map(choice)}
          </ul>
          {tab === 'group' && groups.data && !myGroups.length ? <p className="text-sm text-muted">{t('noGroups')}</p> : null}
          {tab === 'class' && classes.data && !myClasses.length ? <p className="text-sm text-muted">{t('noClasses')}</p> : null}
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('reason')}</span>
            <textarea rows={2} maxLength={RESOURCE_LIMITS.reason} value={reason} onChange={(e) => setReason(e.target.value)} placeholder={t('reasonHint')} className="rounded-xl border border-border bg-bg px-3 py-2" />
          </label>
          {error ? <Alert tone="error">{error}</Alert> : null}
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={close}>
              {t('cancel')}
            </Button>
            <Button disabled={!to || sending.loading} onClick={() => void send()}>
              {t('send')}
            </Button>
          </div>
        </div>
      )}
    </Dialog>
  )
}
