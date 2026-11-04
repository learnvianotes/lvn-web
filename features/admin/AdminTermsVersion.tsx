'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { useFormatter, useTranslations } from 'next-intl'
import { useState, type ReactNode } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Field } from '@/components/ui/field'
import { AdminTermsStatusDocument, ResetAdminSettingDocument, UpdateAdminSettingDocument } from '@/graphql/generated/graphql'
import { publishedTermsVersion, TERMS_VERSION } from '@/features/legal/documents'
import { currentIsUnpublished, initialTermsChoice, K_ANONYMITY_THRESHOLD, selectableTermsVersions, TERMS_VERSION_KEY, termsChoiceIssue, termsRegistryGaps } from '@/features/admin/terms-model'

const SELECT = 'h-11 w-full min-w-0 max-w-full rounded-xl border border-border bg-surface px-3 text-[15px] text-fg disabled:opacity-60'

/**
 * The terms version people accept (lvn-backend ADR-0103), in the Legal section of /admin/settings: what is in effect
 * and where it comes from, who has accepted it, the last change, and a picker limited to versions both this web build
 * and the API's allowlist publish. Switching, or resetting to the server default, is confirmed first: every signed-in
 * person is then asked to accept again. Saved with updateAdminSetting / resetAdminSetting on key terms_version.
 */
export function TermsVersionCard({ overridden, onSaved }: { overridden: boolean; onSaved: () => void }) {
  const t = useTranslations('adminTerms')
  const format = useFormatter()
  const { data, error, previousData, refetch } = useQuery(AdminTermsStatusDocument, { fetchPolicy: 'cache-and-network' })
  const [update, updating] = useMutation(UpdateAdminSettingDocument)
  const [reset, resetting] = useMutation(ResetAdminSettingDocument)
  const [choice, setChoice] = useState<string | null>(null)
  const [confirming, setConfirming] = useState<'switch' | 'reset' | null>(null)
  const [problem, setProblem] = useState<string | null>(null)
  const [done, setDone] = useState<string | null>(null)
  const status = data?.adminTermsStatus ?? previousData?.adminTermsStatus

  if (!status) {
    if (CombinedGraphQLErrors.is(error) && error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')) return <p className="text-muted">{t('notAllowed')}</p>
    return error ? <Alert tone="error">{t('failed')}</Alert> : <p className="text-muted">{t('loading')}</p>
  }

  const { current, source } = status
  const selectable = selectableTermsVersions(status.publishedVersions)
  const gaps = termsRegistryGaps(status.publishedVersions)
  const unpublished = currentIsUnpublished(current)
  const value = choice ?? initialTermsChoice(current, selectable)
  const choiceIssue = termsChoiceIssue(current, value, selectable)
  const busy = updating.loading || resetting.loading
  const count = (n: number | null) => (n == null ? t('fewerThan', { n: K_ANONYMITY_THRESHOLD }) : format.number(n))
  const summary = publishedTermsVersion(current)?.summary
  const chosenSummary = publishedTermsVersion(value)?.summary

  const failed = (err: unknown) => (CombinedGraphQLErrors.is(err) ? (err.errors[0]?.message ?? t('failed')) : t('failed'))
  const finish = (message: string) => {
    setChoice(null)
    setConfirming(null)
    setDone(message)
    void refetch()
    onSaved()
  }

  const switchVersion = async () => {
    setProblem(null)
    setDone(null)
    if (termsChoiceIssue(current, value, selectable)) return
    try {
      const res = await update({ variables: { input: { key: TERMS_VERSION_KEY, value } } })
      const userError = res.data?.updateAdminSetting.userErrors[0]
      if (userError) {
        setConfirming(null)
        setProblem(userError.message)
        return
      }
      finish(t('switched', { version: value }))
    } catch (err) {
      setConfirming(null)
      setProblem(failed(err))
    }
  }

  const resetToDefault = async () => {
    setProblem(null)
    setDone(null)
    try {
      const res = await reset({ variables: { key: TERMS_VERSION_KEY } })
      const userError = res.data?.resetAdminSetting.userErrors[0]
      if (userError) {
        setConfirming(null)
        setProblem(userError.message)
        return
      }
      finish(t('resetDone'))
    } catch (err) {
      setConfirming(null)
      setProblem(failed(err))
    }
  }

  return (
    <article aria-labelledby="terms-version-title" className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 id="terms-version-title" className="font-semibold">
            {t('title')}
          </h3>
          <p className="text-xs text-muted">{TERMS_VERSION_KEY}</p>
        </div>
        <span className={overridden ? 'rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent' : 'rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted'}>{t(`sources.${source}`)}</span>
      </div>
      <p className="text-sm text-muted">{t('lead')}</p>

      <dl className="grid gap-3 text-sm sm:grid-cols-2">
        <Fact label={t('current')}>
          <span className="font-semibold">{current}</span>
          {summary ? <span className="block text-muted">{summary}</span> : null}
        </Fact>
        <Fact label={t('source')}>{t(`sourceHints.${source}`)}</Fact>
        <Fact label={t('acceptedCurrent', { version: current })}>{count(status.acceptedCurrent)}</Fact>
        <Fact label={t('acceptedOlder')}>{count(status.acceptedOlder)}</Fact>
        <div className="flex flex-col gap-0.5 sm:col-span-2">
          <dt className="text-muted">{t('lastChange')}</dt>
          <dd>
            {status.lastChange ? (
              <>
                {t(status.lastChange.previous ? 'changedFrom' : 'changed', { who: status.lastChange.actorDisplayName ?? t('removedAccount'), previous: status.lastChange.previous ?? '' })}
                <span className="text-muted">
                  {' · '}
                  <time dateTime={status.lastChange.at}>{format.dateTime(new Date(status.lastChange.at), { dateStyle: 'medium', timeStyle: 'short' })}</time>
                </span>
              </>
            ) : (
              t('neverChanged')
            )}
          </dd>
        </div>
      </dl>

      {unpublished ? <Alert tone="error">{t('currentUnpublished', { version: current, shown: TERMS_VERSION })}</Alert> : null}
      {gaps.webOnly.length ? <Alert>{t('webOnly', { versions: gaps.webOnly.join(', '), count: gaps.webOnly.length })}</Alert> : null}
      {gaps.apiOnly.length ? <Alert>{t('apiOnly', { versions: gaps.apiOnly.join(', '), count: gaps.apiOnly.length })}</Alert> : null}

      {selectable.length ? (
        <Field label={t('choose')} hint={t('chooseHint')}>
          <select
            className={SELECT}
            value={value}
            disabled={busy}
            onChange={(e) => {
              setChoice(e.target.value)
              setProblem(null)
              setDone(null)
            }}
          >
            {initialTermsChoice(current, selectable) === '' ? (
              <option value="" disabled>
                {t('choosePlaceholder')}
              </option>
            ) : null}
            {selectable.map((v) => (
              <option key={v.version} value={v.version}>
                {t(v.version === current ? 'optionCurrent' : 'option', { version: v.version, summary: v.summary })}
              </option>
            ))}
          </select>
        </Field>
      ) : (
        <Alert tone="error">{t('noneSelectable')}</Alert>
      )}

      {problem ? <Alert tone="error">{problem}</Alert> : null}
      {done ? <Alert tone="success">{done}</Alert> : null}

      <div className="flex flex-col gap-2 sm:flex-row">
        <Button type="button" size="sm" className="h-11 w-full sm:w-auto" disabled={!!choiceIssue || busy} onClick={() => setConfirming('switch')}>
          {value && value !== current ? t('switchTo', { version: value }) : t('switch')}
        </Button>
        {overridden ? (
          <Button type="button" size="sm" variant="secondary" className="h-11 w-full sm:w-auto" disabled={busy} onClick={() => setConfirming('reset')}>
            {t('reset')}
          </Button>
        ) : null}
      </div>

      <Dialog open={confirming !== null} onClose={() => setConfirming(null)} title={confirming === 'reset' ? t('confirmResetTitle') : t('confirmTitle', { version: value })} sheet>
        <div className="flex flex-col gap-4 text-sm">
          {confirming === 'reset' ? (
            <p>{t('confirmReset', { current })}</p>
          ) : (
            <>
              <p>{t('confirmSwitch', { current, version: value })}</p>
              {chosenSummary ? <p className="text-muted">{t('confirmSummary', { summary: chosenSummary })}</p> : null}
            </>
          )}
          <p className="rounded-xl border border-bad/30 bg-bad/10 px-3 py-2 font-medium">{t(confirming === 'reset' ? 'confirmEveryoneReset' : 'confirmEveryone')}</p>
          <p className="text-muted">{t('confirmCounts', { accepted: count(status.acceptedCurrent), current })}</p>
          <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
            <Button type="button" variant="ghost" className="h-11 w-full sm:w-auto" onClick={() => setConfirming(null)}>
              {t('cancel')}
            </Button>
            <Button type="button" className="h-11 w-full sm:w-auto" disabled={busy} onClick={() => void (confirming === 'reset' ? resetToDefault() : switchVersion())}>
              {busy ? t('saving') : confirming === 'reset' ? t('confirmResetAction') : t('confirmAction', { version: value })}
            </Button>
          </div>
        </div>
      </Dialog>
    </article>
  )
}

function Fact({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <dt className="text-muted">{label}</dt>
      <dd>{children}</dd>
    </div>
  )
}
