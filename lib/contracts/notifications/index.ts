// Copied from lvn-backend contracts/src/notifications/index.ts by scripts/contracts-sync.mjs — do not edit here.
import { z } from 'zod'
import { enumValues } from '../domain/enums'

/**
 * Push notifications (spec §9.3, ADR-0021). Delivered through Firebase Cloud Messaging — Android directly, iOS via
 * APNs — and nothing else of Firebase. The payload carries ids only: the app fetches the content over the API, so
 * permission checks happen on that fetch (§9.2) and no note, comment or message text passes through Google.
 *
 * Links are in-app paths ("/n/os-notes-0199…"), never full URLs: each app joins them to its own scheme or origin
 * from its environment, so no domain is written into the contract (ADR-0022).
 */

export const NotificationCategory = {
  COMMENT: 'COMMENT', SHARE: 'SHARE', CLASSROOM_POST: 'CLASSROOM_POST', QUIZ_PUBLISHED: 'QUIZ_PUBLISHED',
  REVISION_REMINDER: 'REVISION_REMINDER', STREAK_AT_RISK: 'STREAK_AT_RISK', JOIN_REQUEST: 'JOIN_REQUEST',
  JOIN_DECISION: 'JOIN_DECISION', FOLLOW: 'FOLLOW', CONNECTION: 'CONNECTION', MENTOR_INVITE: 'MENTOR_INVITE',
  DOUBT: 'DOUBT', FORK_PUBLISHED: 'FORK_PUBLISHED', VERIFICATION: 'VERIFICATION', DATA_EXPORT: 'DATA_EXPORT',
  NOTES_IMPORT: 'NOTES_IMPORT', CLASSROOM_INVITE: 'CLASSROOM_INVITE', MODERATION: 'MODERATION', MENTION: 'MENTION',
} as const
export type NotificationCategory = (typeof NotificationCategory)[keyof typeof NotificationCategory]

/** An absolute in-app path: starts with a single "/", no scheme, host or "//". */
const IN_APP_PATH = /^\/(?!\/)[A-Za-z0-9\-._~!$&'()*+,;=:@%/?#]*$/

/** The FCM `data` block. Strict: any extra key (for example, smuggled content) is rejected. */
export const pushData = z
  .object({
    notificationId: z.uuid(),
    category: z.enum(enumValues(NotificationCategory)),
    path: z.string().max(512).regex(IN_APP_PATH, 'must be an in-app path such as /n/<slug>-<id>'),
  })
  .strict()
export type PushData = z.infer<typeof pushData>

/**
 * The whole message. Title and body are short, generated server-side, and never quote note, comment or message
 * text ("Priya commented on your note", not the comment). Restricted minors get generic text.
 */
export const pushMessage = z
  .object({
    title: z.string().min(1).max(65),
    body: z.string().max(120),
    data: pushData,
  })
  .strict()
export type PushMessage = z.infer<typeof pushMessage>

/**
 * Live updates (§9.2, ADR-0042): what the `live` subscription delivers. A kind and an id, nothing else — the client
 * refetches through the API, where the permission checks run.
 */
export const LiveEventKind = { NOTIFICATION: 'NOTIFICATION' } as const
export type LiveEventKind = (typeof LiveEventKind)[keyof typeof LiveEventKind]

export const liveEvent = z
  .object({
    kind: z.enum(enumValues(LiveEventKind)),
    id: z.uuid(),
    at: z.iso.datetime(),
  })
  .strict()
export type LiveEvent = z.infer<typeof liveEvent>
