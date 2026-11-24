import { Check, EyeOff, MessageSquareWarning, Trash, type LucideIcon } from 'lucide-react'
import type { ModerationChoice } from '@/features/moderation/ModerationActions'
import type { AdminContentType, ModerationActionType, ReportEntityType } from '@/graphql/generated/graphql'

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

/** Kinds moderateContent accepts. A share id is not a uuid, so it never matches. */
const MODERATABLE: Partial<Record<AdminContentType, ReportEntityType>> = {
  NOTE: 'NOTE',
  COMMENT: 'COMMENT',
  GROUP: 'GROUP',
  GROUP_POST: 'GROUP_POST',
  CLASSROOM_POST: 'CLASSROOM_POST',
  DOUBT: 'DOUBT',
  RESOURCE: 'RESOURCE',
}

function choice(action: ModerationActionType, label: string, icon: LucideIcon, tone = ''): ModerationChoice {
  return { action, label, icon, tone }
}

const approve = () => choice('APPROVE', 'APPROVE', Check)
const restore = () => choice('APPROVE', 'RESTORE', Check)
const warn = () => choice('WARN', 'WARN', MessageSquareWarning)
const hide = () => choice('HIDE', 'HIDE', EyeOff, 'text-warn')
const remove = () => choice('REMOVE', 'REMOVE', Trash, 'text-bad')
const reject = () => choice('REMOVE', 'REJECT', Trash, 'text-bad')

/**
 * Actions for one row, when this kind is one moderateContent can take and the id is a uuid. The set follows the
 * moderation queue: what is up can be hidden or removed, what is down can be put back, and a new resource is
 * approved or rejected. Dismiss is left to the queue, which is where the reports are.
 */
export function moderationFor(item: { type: AdminContentType; id: string; moderation: string | null }): { entityType: ReportEntityType; actions: ModerationChoice[] } | null {
  const entityType = MODERATABLE[item.type]
  if (!entityType || !UUID.test(item.id) || item.moderation == null) return null
  if (item.type === 'RESOURCE') {
    if (item.moderation === 'PENDING') return { entityType, actions: [approve(), reject()] }
    if (item.moderation === 'REJECTED') return { entityType, actions: [approve()] }
    return { entityType, actions: [remove()] }
  }
  if (item.type === 'GROUP') return { entityType, actions: [warn(), remove()] }
  if (item.moderation === 'HIDDEN' || item.moderation === 'REMOVED') return { entityType, actions: [restore(), warn(), hide(), remove()] }
  if (item.moderation === 'OK') return { entityType, actions: [warn(), hide(), remove()] }
  return { entityType, actions: [approve(), warn(), hide(), remove()] }
}
