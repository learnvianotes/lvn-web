'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { GraduationCap } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { attempt, problemOf } from '@/features/groups/shared'
import { ClassroomByCodeDocument, RequestToJoinClassroomDocument, WithdrawClassroomJoinRequestDocument } from '@/graphql/generated/graphql'
import { cleanCode } from './shared'

/**
 * /classes/join/<code> (lvn-backend ADR-0046): the class a code names, by its name and teacher only, and a request to
 * join it. The code admits nobody: the teacher or a TA answers.
 */
export function JoinByCode({ code: raw, via }: { code: string; via: 'CODE' | 'LINK' }) {
  const t = useTranslations('classes')
  const code = cleanCode(raw)
  const { data, loading, error: lookup, refetch } = useQuery(ClassroomByCodeDocument, { variables: { code }, fetchPolicy: 'network-only' })
  const [request, requesting] = useMutation(RequestToJoinClassroomDocument)
  const [withdraw] = useMutation(WithdrawClassroomJoinRequestDocument)
  const [error, setError] = useState<string | null>(null)
  const found = data?.classroomByCode
  const run = async (fn: () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>) => {
    setError(await attempt(fn, t('failed')))
    await refetch()
  }
  if (loading && !data) return <p role="status" className="text-sm text-muted">{t('loading')}</p>
  const problem = problemOf(lookup, undefined, t('failed'))
  return (
    <div className="mx-auto flex max-w-md flex-col gap-4">
      <h1 className="text-2xl font-semibold tracking-tight">{t('joinTitle')}</h1>
      {problem ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {problem}
        </p>
      ) : !found ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noSuchCode')}</p>
      ) : (
        <section className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-6 shadow-sm">
          <span className="flex items-center gap-2 text-sm text-muted">
            <GraduationCap className="size-4 text-accent" aria-hidden />
            <span className="font-mono">{code}</span>
          </span>
          <h2 className="text-xl font-semibold">{found.name}</h2>
          <p className="text-sm text-muted">{t('byTeacher', { name: found.teacher.displayName })}</p>
          {found.viewerRole ? (
            <>
              <p className="text-sm">{t('alreadyIn')}</p>
              <Link href={`/classes/${found.id}`} className="w-fit font-semibold text-accent hover:underline">
                {t('open')}
              </Link>
            </>
          ) : found.viewerRequestId ? (
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-sm text-muted">{t('waiting')}</span>
              <Button variant="secondary" size="sm" onClick={() => void run(() => withdraw({ variables: { requestId: found.viewerRequestId! } }))}>
                {t('withdraw')}
              </Button>
            </div>
          ) : (
            <>
              <Button className="w-fit" disabled={requesting.loading} onClick={() => void run(() => request({ variables: { code, via } }))}>
                {t('askToJoin')}
              </Button>
              <p className="text-xs text-muted">{t('askHint')}</p>
            </>
          )}
          {error ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          ) : null}
        </section>
      )}
    </div>
  )
}
