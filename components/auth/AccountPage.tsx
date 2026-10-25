'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import {
  ClaimLegacyDataDocument,
  DeclineLegacyDataDocument,
  SetInstitutionalEmailDocument,
  SignOutDocument,
  UpdateProfileDocument,
  ViewerDocument,
  type ViewerQuery,
  type YearOfStudy,
} from '@/graphql/generated/graphql'
import { signedOut } from '@/lib/auth/session'
import { clearDraftMirrors, countDraftMirrors } from '@/features/notes/editor/mirror'
import { YourData } from '@/features/data/YourData'
import { DeleteAccount } from '@/features/data/DeleteAccount'
import { AccountStanding } from '@/features/moderation/Standing'
import { ReviewRequests } from '@/features/verification/ReviewRequests'
import { STUDENT_ID_ADMIN_PATH } from '@/features/verification/student-id'
import { VerifyAccount } from '@/features/verification/VerifyAccount'
import { AiAccountSection } from '@/features/ai/AiPanel'
import { Interests } from '@/features/community/Interests'

type Viewer = NonNullable<ViewerQuery['viewer']>
const YEARS: YearOfStudy[] = ['YEAR_1', 'YEAR_2', 'YEAR_3', 'YEAR_4', 'YEAR_5', 'POSTGRADUATE', 'GRADUATED', 'SCHOOL', 'NOT_STUDYING']

const card = 'flex flex-col gap-4 rounded-2xl border border-border bg-surface p-5'

/** Phase 1 account page: verification, college email, study details, old-site data, sign-out. */
export function AccountPage() {
  const t = useTranslations('profile')
  const tt = useTranslations('teach')
  const { data, loading, error, refetch } = useQuery(ViewerDocument)
  const viewer = data?.viewer
  if (loading && !viewer) return <Loading label={t('loading')} />
  if (!viewer) return error ? <LoadFailed onRetry={refetch} /> : null
  return (
    <div className="flex flex-col gap-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{viewer.displayName}</h1>
          <p className="text-sm text-muted">@{viewer.handle} · {viewer.email}</p>
        </div>
        <SignOutButton />
      </header>
      <AccountStanding userId={viewer.id} />
      {viewer.globalRole === 'PLATFORM_ADMIN' ? (
        <Link href="/admin/verification" className="flex items-center justify-between rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm font-semibold text-accent hover:border-accent">
          {t('verificationQueue')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      {viewer.globalRole === 'PLATFORM_ADMIN' ? (
        <Link href={STUDENT_ID_ADMIN_PATH} className="flex items-center justify-between rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm font-semibold text-accent hover:border-accent">
          {t('studentIdQueue')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      {viewer.globalRole === 'PLATFORM_ADMIN' ? (
        <Link href="/admin/moderation" className="flex items-center justify-between rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm font-semibold text-accent hover:border-accent">
          {t('moderationQueue')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      {viewer.globalRole === 'PLATFORM_ADMIN' ? (
        <Link href="/admin/ai" className="flex items-center justify-between rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm font-semibold text-accent hover:border-accent">
          {t('aiProviders')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      {viewer.globalRole === 'PLATFORM_ADMIN' ? (
        <Link href="/admin/contests" className="flex items-center justify-between rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm font-semibold text-accent hover:border-accent">
          {t('adminContests')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      <Link href="/home" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('home')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/exams" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('exams')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/rhythm" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('rhythm')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/achievements" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('achievements')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/review" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('review')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/history" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('history')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/classes" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('classes')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/groups" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('groups')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/resources/mine" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('resources')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/saved" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('savedResources')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/plans" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('plan')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/profile/notifications" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('notificationSettings')}
        <span aria-hidden>→</span>
      </Link>
      <Link href="/profile/people" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
        {t('people')}
        <span aria-hidden>→</span>
      </Link>
      {viewer.globalRole === 'STUDENT' && !viewer.restrictedMinor ? (
        <Link href="/teach" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
          {viewer.teacherStatus === 'PENDING' ? tt('accountPending') : viewer.teacherStatus === 'DECLINED' ? tt('accountDeclined') : tt('accountCard')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      {viewer.globalRole === 'TEACHER' || viewer.teacherStatus === 'PENDING' ? (
        <Link href="/profile/skills" className="flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 text-sm font-semibold hover:border-accent">
          {t('skills')}
          <span aria-hidden>→</span>
        </Link>
      ) : null}
      <Verification viewer={viewer} />
      {viewer.globalRole === 'TEACHER' && viewer.verified ? <ReviewRequests /> : null}
      {viewer.restrictedMinor ? <Alert>{t('minor')}</Alert> : null}
      <InstitutionalEmail viewer={viewer} />
      <StudyDetails viewer={viewer} />
      <Interests />
      <LegacyData viewer={viewer} />
      <AiAccountSection className={card} />
      <YourData />
      <DeleteAccount />
    </div>
  )
}

function SignOutButton() {
  const t = useTranslations('profile')
  const [signOut] = useMutation(SignOutDocument)
  const client = useApolloClient()
  const router = useRouter()
  return (
    <Button
      variant="secondary"
      size="sm"
      onClick={async () => {
        // Drafts mirrored in this browser are deleted on sign-out (shared computers); unsent ones only if the user agrees.
        if ((await countDraftMirrors()) > 0 && !window.confirm(t('unsavedDrafts'))) return
        await clearDraftMirrors()
        await signOut().catch(() => undefined)
        signedOut()
        await client.clearStore()
        router.replace('/')
      }}
    >
      {t('signOut')}
    </Button>
  )
}

function Verification({ viewer }: { viewer: Viewer }) {
  const t = useTranslations('profile')
  return (
    <section className={card} aria-labelledby="verification">
      <h2 id="verification" className="text-lg font-semibold">
        {viewer.verified ? `✓ ${t('verified')}` : t('notVerified')}
        {viewer.verified && viewer.verificationMethod ? <span className="text-sm font-normal text-muted"> {t(`verifiedBy.${viewer.verificationMethod}`)}</span> : null}
      </h2>
      {!viewer.verified ? <p className="text-sm text-muted">{t('verifyLead')}</p> : null}
      {!viewer.emailVerified ? <Alert>{t('emailUnverified')}</Alert> : null}
      {/* Without a college email (ADR-0019): a teacher vouches, or our team checks proof of study. */}
      {!viewer.verified ? <VerifyAccount restrictedMinor={!!viewer.restrictedMinor} /> : null}
    </section>
  )
}

function InstitutionalEmail({ viewer }: { viewer: Viewer }) {
  const t = useTranslations('profile.institution')
  const te = useTranslations('auth.errors')
  const client = useApolloClient()
  const [set] = useMutation(SetInstitutionalEmailDocument)
  const [editing, setEditing] = useState(false)
  const [email, setEmail] = useState('')
  const [problem, setProblem] = useState<string | null>(null)
  const status = viewer.institutionalEmailStatus
  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    setProblem(null)
    try {
      const { data } = await set({ variables: { email } })
      if (!data?.setInstitutionalEmail.ok) return setProblem(data?.setInstitutionalEmail.userErrors[0]?.message ?? te('generic'))
      setEditing(false)
      await client.refetchQueries({ include: [ViewerDocument] })
    } catch {
      setProblem(te('generic'))
    }
  }
  return (
    <section className={card} aria-labelledby="institution">
      <div className="flex items-center justify-between gap-3">
        <h2 id="institution" className="text-lg font-semibold">{t('title')}</h2>
        {!editing ? <Button variant="ghost" size="sm" onClick={() => setEditing(true)}>{status === 'NONE' ? t('add') : t('replace')}</Button> : null}
      </div>
      {status && status !== 'NONE' ? <p className="text-sm">{t(`status${status}`, { email: viewer.institutionalEmail ?? '' })}</p> : null}
      {viewer.institution ? <p className="text-sm text-muted">{viewer.institution.name}</p> : null}
      {status === 'CODE_SENT' ? <Button asChild size="sm" className="self-start"><Link href="/verify">{t('enterCode')}</Link></Button> : null}
      {editing ? (
        <form onSubmit={save} className="flex flex-col gap-3" noValidate>
          <Field label={t('email')} error={problem ?? undefined}>
            <Input type="email" inputMode="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Button type="submit" size="sm" className="self-start" disabled={!email}>{t('add')}</Button>
        </form>
      ) : null}
    </section>
  )
}

function StudyDetails({ viewer }: { viewer: Viewer }) {
  const t = useTranslations('profile.details')
  const ty = useTranslations('profile.years')
  const te = useTranslations('auth.errors')
  const [update] = useMutation(UpdateProfileDocument)
  const [department, setDepartment] = useState(viewer.profile?.department ?? '')
  const [year, setYear] = useState<YearOfStudy | ''>(viewer.profile?.yearOfStudy ?? '')
  const [show, setShow] = useState(viewer.profile?.showOnProfile ?? false)
  const [state, setState] = useState<'idle' | 'saved' | string>('idle')
  const save = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const { data } = await update({ variables: { input: { department: department || null, yearOfStudy: year || null, showOnProfile: show } } })
      setState(data?.updateProfile.profile ? 'saved' : (data?.updateProfile.userErrors[0]?.message ?? te('generic')))
    } catch {
      setState(te('generic'))
    }
  }
  return (
    <section className={card} aria-labelledby="details">
      <h2 id="details" className="text-lg font-semibold">{t('title')}</h2>
      <form onSubmit={save} className="flex flex-col gap-4" noValidate>
        <Field label={t('department')} hint={t('departmentHint')}>
          <Input value={department} onChange={(e) => setDepartment(e.target.value)} maxLength={80} />
        </Field>
        <Field label={t('year')}>
          <select value={year} onChange={(e) => setYear(e.target.value as YearOfStudy | '')} className="h-11 rounded-xl border border-border bg-surface px-3 text-[15px]">
            <option value="">—</option>
            {YEARS.map((y) => <option key={y} value={y}>{ty(y)}</option>)}
          </select>
        </Field>
        <label className="flex items-center gap-3 text-sm">
          <input type="checkbox" className="size-4 accent-[var(--accent)]" checked={show} onChange={(e) => setShow(e.target.checked)} />
          {t('show')}
        </label>
        <div className="flex items-center gap-3">
          <Button type="submit" size="sm">{t('save')}</Button>
          {state === 'saved' ? <span role="status" className="text-sm text-muted">{t('saved')}</span> : state !== 'idle' ? <span role="alert" className="text-sm text-red-600">{state}</span> : null}
        </div>
      </form>
    </section>
  )
}

function LegacyData({ viewer }: { viewer: Viewer }) {
  const t = useTranslations('profile.legacy')
  const client = useApolloClient()
  const [claim] = useMutation(ClaimLegacyDataDocument)
  const [decline] = useMutation(DeclineLegacyDataDocument)
  const legacy = viewer.legacyImport
  if (!legacy || legacy.status === 'NOT_FOUND') return null
  const act = async (fn: () => Promise<unknown>) => {
    await fn()
    await client.refetchQueries({ include: [ViewerDocument] })
  }
  return (
    <section className={card} aria-labelledby="legacy">
      <h2 id="legacy" className="text-lg font-semibold">{t('title')}</h2>
      {legacy.status === 'AVAILABLE' && legacy.counts ? (
        <>
          <p className="text-sm">{t('available', { topics: legacy.counts.completedTopics, problems: legacy.counts.markedProblems, days: legacy.counts.studyDays })}</p>
          <div className="flex gap-3">
            <Button size="sm" onClick={() => void act(() => claim())}>{t('claim')}</Button>
            <Button size="sm" variant="ghost" onClick={() => void act(() => decline())}>{t('decline')}</Button>
          </div>
        </>
      ) : null}
      {legacy.status === 'CLAIMED' ? (
        <div className="flex items-center justify-between gap-3">
          <p className="text-sm">{t('claimed')}</p>
          <Button size="sm" variant="ghost" onClick={() => void act(() => decline())}>{t('remove')}</Button>
        </div>
      ) : null}
      {legacy.status === 'DECLINED' ? <p className="text-sm text-muted">{t('declined')}</p> : null}
    </section>
  )
}
