'use client'

import { useMutation } from '@apollo/client/react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { attempt } from '@/features/groups/shared'
import { ConnectRepositoryAppDocument } from '@/graphql/generated/graphql'

/**
 * GitHub's return after the App is installed (lvn-backend ADR-0078): the install link's state, the installation and the
 * person's code go to the API, which connects the workspace's repository only when GitHub confirms them.
 */
export function GitHubSetup() {
  const t = useTranslations('workspaces.app')
  const params = useSearchParams()
  const [connect] = useMutation(ConnectRepositoryAppDocument)
  const [state, setState] = useState<{ status: 'working' | 'done' | 'failed' | 'missing' | 'requested'; text?: string; groupId?: string }>({ status: 'working' })
  const asked = useRef(false)
  const installationId = params.get('installation_id')
  const code = params.get('code')
  const linkState = params.get('state')
  useEffect(() => {
    if (asked.current) return
    asked.current = true
    if (params.get('setup_action') === 'request') return setState({ status: 'requested' })
    if (!installationId || !code || !linkState) return setState({ status: 'missing' })
    let groupId: string | undefined
    void attempt(async () => {
      const res = await connect({ variables: { input: { state: linkState, installationId, code } } })
      groupId = res.data?.connectRepositoryApp.group?.id
      return res
    }, t('setupMissing')).then((problem) => setState(problem ? { status: 'failed', text: problem } : { status: 'done', groupId }))
  }, [connect, installationId, code, linkState, params, t])
  const back = state.groupId ?? linkState?.split('.')[0]
  return (
    <div className="mx-auto flex max-w-xl flex-col gap-4 py-8">
      <h1 className="text-2xl font-semibold">{t('setupTitle')}</h1>
      {state.status === 'working' ? (
        <p role="status" className="text-muted">
          {t('setupWorking')}
        </p>
      ) : null}
      {state.status === 'done' ? <p role="status">{t('setupDone')}</p> : null}
      {state.status === 'failed' ? (
        <p role="alert" className="text-bad">
          {state.text}
        </p>
      ) : null}
      {state.status === 'missing' ? <p role="alert">{t('setupMissing')}</p> : null}
      {state.status === 'requested' ? <p role="status">{t('setupRequested')}</p> : null}
      {back && state.status !== 'working' ? (
        <Link href={`/groups/${back}`} className="font-semibold text-accent hover:underline">
          {t('setupBack')}
        </Link>
      ) : null}
    </div>
  )
}
