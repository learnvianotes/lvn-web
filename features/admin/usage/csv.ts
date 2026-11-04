/**
 * CSV for each dashboard tab: exactly the aggregates on screen, nothing per person. Headers are stable snake_case
 * column names so a sheet built on an export keeps working when the UI wording changes.
 */
import type {
  AdminUsageContentQuery,
  AdminUsageEngagementQuery,
  AdminUsageFunnelQuery,
  AdminUsageGrowthQuery,
  AdminUsageOverviewQuery,
  AdminUsageQuery,
  AdminUsageRetentionQuery,
  AdminUsageSubjectsQuery,
  AdminUsageVerificationQuery,
} from '@/graphql/generated/graphql'
import { funnelRows, share, type CsvTable } from './shape'

const hidden = (n: number): CsvTable => ({ name: 'hidden', header: ['hidden_small_groups'], rows: [[n]] })

export function overviewCsv(data: AdminUsageOverviewQuery, summary?: AdminUsageQuery['adminUsage'] | null, newToday?: number | null): CsvTable[] {
  const { adminMetrics: m, adminEngagement: e, adminGrowth: g } = data
  const tables: CsvTable[] = [
    {
      name: 'kpis',
      header: ['metric', 'value'],
      rows: [
        ['users_total', m.users.total],
        ['new_today', newToday ?? null],
        ['new_last_7_days', m.users.newLast7Days],
        ['new_last_30_days', m.users.newLast30Days],
        ['dau', e.dau],
        ['wau', e.wau],
        ['mau', e.mau],
        ['stickiness', e.stickiness],
        ['sign_ups_in_range', g.totals.signUps],
        ['verifications_in_range', g.totals.verifications],
        ['verifications_per_sign_up', share(g.totals.verifications, g.totals.signUps)],
      ],
    },
  ]
  if (summary) {
    tables.push({ name: 'top_features', header: ['feature', 'count'], rows: summary.topFeatures.map((r) => [r.name, r.count]) })
    tables.push({ name: 'top_actions', header: ['action', 'count'], rows: summary.topEvents.map((r) => [r.name, r.count]) })
  }
  return tables
}

export function growthCsv(data: AdminUsageGrowthQuery): CsvTable[] {
  const g = data.adminGrowth
  return [
    {
      name: 'series',
      header: ['bucket_start', 'sign_ups', 'email_verified', 'registrations_completed', 'verifications'],
      rows: g.series.map((p) => [p.date, p.signUps, p.emailVerified, p.registrationsCompleted, p.verifications]),
    },
    { name: 'sign_up_methods', header: ['method', 'users'], rows: g.signUpMethods.map((r) => [r.method, r.users]) },
    hidden(g.hiddenSmallGroups),
  ]
}

export function engagementCsv(data: AdminUsageEngagementQuery): CsvTable[] {
  const e = data.adminEngagement
  return [
    { name: 'summary', header: ['dau', 'wau', 'mau', 'stickiness'], rows: [[e.dau, e.wau, e.mau, e.stickiness]] },
    {
      name: 'series',
      header: ['bucket_start', 'active_users', 'learning_minutes', 'quiz_attempts', 'notes_created', 'doubts_asked', 'doubts_answered'],
      rows: e.series.map((p) => [p.date, p.activeUsers, p.learningMinutes, p.quizAttempts, p.notesCreated, p.doubtsAsked, p.doubtsAnswered]),
    },
  ]
}

export function contentCsv(data: AdminUsageContentQuery): CsvTable[] {
  const c = data.adminContentStats
  return [
    {
      name: 'counts',
      header: ['metric', 'value'],
      rows: [
        ['notes_created', c.notes.created],
        ['notes_private', c.notes.private],
        ['notes_shared', c.notes.shared],
        ['notes_unlisted', c.notes.unlisted],
        ['notes_public', c.notes.public],
        ['upload_files', c.uploads.files],
        ['upload_bytes', c.uploads.bytes],
        ['doubts_asked', c.doubts.asked],
        ['doubts_answered', c.doubts.answered],
        ['doubts_resolved', c.doubts.resolved],
        ['answers', c.doubts.answers],
        ['median_hours_to_first_answer', c.doubts.medianHoursToFirstAnswer],
        ['groups', c.places.groups],
        ['group_posts', c.places.groupPosts],
        ['classrooms', c.places.classrooms],
        ['classroom_posts', c.places.classroomPosts],
        ['note_shares', c.sharing.noteShares],
        ['place_shares', c.sharing.placeShares],
        ['saves', c.sharing.saves],
        ['scans_clean', c.scans.clean],
        ['scans_pending', c.scans.pending],
        ['scans_failed', c.scans.failed],
        ['scans_infected', c.scans.infected],
      ],
    },
    { name: 'uploads_by_purpose', header: ['purpose', 'files', 'bytes'], rows: c.uploads.byPurpose.map((r) => [r.purpose, r.files, r.bytes]) },
    hidden(c.uploads.hiddenSmallGroups),
  ]
}

export function subjectsCsv(data: AdminUsageSubjectsQuery): CsvTable[] {
  const s = data.adminTopSubjects
  return [
    { name: 'subjects', header: ['rank', 'subject', `value_${s.by.toLowerCase()}`, 'people'], rows: s.subjects.map((r, i) => [i + 1, r.title, r.value, r.users]) },
    hidden(s.hiddenSmallGroups),
  ]
}

export function retentionCsv(data: AdminUsageRetentionQuery): CsvTable[] {
  const r = data.adminRetention
  const width = r.cohorts.reduce((max, c) => Math.max(max, c.returned.length), 0)
  return [
    {
      name: 'cohorts',
      header: ['cohort_week', 'size', ...Array.from({ length: width }, (_, i) => `week_${i}`)],
      rows: r.cohorts.map((c) => [c.start, c.size, ...Array.from({ length: width }, (_, i) => c.returned[i] ?? null)]),
    },
    hidden(r.hiddenSmallGroups),
  ]
}

export function verificationCsv(data: AdminUsageVerificationQuery): CsvTable[] {
  const v = data.adminVerificationStats
  return [
    {
      name: 'summary',
      header: ['requested', 'approved', 'rejected', 'pending', 'median_hours_to_decision', 'oldest_pending_hours'],
      rows: [[v.requested, v.approved, v.rejected, v.pending, v.medianHoursToDecision, v.oldestPendingHours]],
    },
    { name: 'by_method', header: ['method', 'requested', 'approved', 'rejected'], rows: v.byMethod.map((r) => [r.method, r.requested, r.approved, r.rejected]) },
    hidden(v.hiddenSmallGroups),
  ]
}

export function funnelCsv(data: AdminUsageFunnelQuery): CsvTable[] {
  return [{ name: 'funnel', header: ['step', 'people', 'of_first_step', 'of_previous_step'], rows: funnelRows(data.adminFunnel).map((r) => [r.name, r.users, r.ofFirst, r.ofPrevious]) }]
}
