import type { NotificationFieldsFragment } from '@/graphql/generated/graphql'

type Translate = (key: string, values?: Record<string, string | number>) => string

/**
 * The sentence for a notification (lvn-backend ADR-0042): written here from its category, the actor's name and the
 * note's title, which the API resolved with its own read checks. Nothing in a notification is user-written text.
 */
export function describeNotification(
  n: Pick<NotificationFieldsFragment, 'category' | 'data' | 'actor' | 'note' | 'path'> & { group?: NotificationFieldsFragment['group']; classroom?: NotificationFieldsFragment['classroom'] },
  t: Translate,
): string {
  const actor = n.actor?.displayName ?? t('someone')
  const data = (n.data ?? {}) as Record<string, unknown>
  // Join requests and answers are about a group or a class (lvn-backend ADR-0046); a class may be gone from view.
  const place = n.classroom ? n.classroom.name : n.group ? n.group.name : null
  switch (n.category) {
    case 'SHARE':
      return n.note ? t('share', { actor, note: n.note.title || t('untitled') }) : t('shareGone', { actor })
    case 'VERIFICATION':
      if (data.kind === 'REQUESTED') return t('verificationRequested', { actor })
      // An application to teach (lvn-backend ADR-0073).
      if (data.purpose === 'TEACHER_ROLE') return t(data.decision === 'APPROVED' ? 'teacherApproved' : 'teacherDeclined')
      if (data.decision === 'APPROVED') return n.actor ? t('verificationApprovedBy', { actor }) : t('verificationApproved')
      return t('verificationRejected')
    case 'FOLLOW':
      return t('follow', { actor })
    case 'JOIN_REQUEST':
      return t('joinRequest', { actor, group: place ?? t('aGroup') })
    case 'JOIN_DECISION':
      if (!place && n.path.startsWith('/classes/')) return data.decision === 'APPROVED' ? t('classJoinApproved') : t('classJoinRejected')
      return data.decision === 'APPROVED' ? t('joinApproved', { group: place ?? t('aGroup') }) : t('joinRejected', { group: place ?? t('aGroup') })
    case 'MENTOR_INVITE':
      return t('mentorInvite', { actor, group: place ?? t('aGroup') })
    case 'DOUBT':
      return t(data.kind === 'ANSWERED' ? 'doubtAnswered' : data.kind === 'RESOLVED' ? 'doubtResolved' : 'doubtAsked', { actor, group: place ?? t('aGroup') })
    case 'CLASSROOM_INVITE':
      return t('classInvite', { actor, classroom: place ?? t('aClass') })
    case 'COMMENT': {
      const reply = data.kind === 'REPLY'
      if (n.note) return t(reply ? 'replyOnNote' : 'commentOnNote', { actor, note: n.note.title || t('untitled') })
      if (place) return t(reply ? 'replyIn' : 'commentIn', { actor, place })
      return t('commentGone', { actor })
    }
    case 'MENTION': {
      // Someone named the viewer with @handle (lvn-backend ADR-0054); where, never what they wrote.
      const thing = t(`mentionThing.${data.entityType === 'GROUP_POST' ? 'GROUP_POST' : 'COMMENT'}`)
      if (n.note) return t('mentionOnNote', { actor, note: n.note.title || t('untitled') })
      if (place) return t('mentionIn', { actor, thing, place })
      return t('mentionGone', { actor })
    }
    case 'CLASSROOM_POST':
      return t('classPost', { actor, classroom: place ?? t('aClass') })
    case 'QUIZ_PUBLISHED':
      // A quiz published to the viewer's class (lvn-backend ADR-0064); the notification opens it.
      return t('quizPublished', { actor, classroom: place ?? t('aClass') })
    case 'MODERATION': {
      // What a moderator decided about the viewer's own content (lvn-backend ADR-0051); the reason is shown with it.
      const type = typeof data.entityType === 'string' ? data.entityType : 'OTHER'
      // About the account itself (ADR-0053): a warning, a suspension, or a suspension lifted.
      if (type === 'USER') return t(data.kind === 'SUSPENDED' ? 'moderationAccountSuspended' : data.kind === 'RESTORED' ? 'moderationAccountRestored' : 'moderationAccountWarned')
      const thing = t(`moderationThing.${['COMMENT', 'GROUP_POST', 'CLASSROOM_POST', 'DOUBT', 'GROUP'].includes(type) ? type : 'OTHER'}`)
      const what = type === 'GROUP' ? (place ? t('moderationWhatGroup', { group: place }) : thing) : n.note ? t('moderationWhatOn', { thing, note: n.note.title || t('untitled') }) : place ? t('moderationWhatIn', { thing, place }) : thing
      // A removed group's owner opens it to read why and appeal (ADR-0053).
      const kind = data.kind === 'REMOVED' ? (type === 'GROUP' ? 'moderationGroupRemoved' : 'moderationRemoved') : data.kind === 'WARNED' ? 'moderationWarned' : data.kind === 'RESTORED' ? 'moderationRestored' : 'moderationHidden'
      return t(kind, { what })
    }
    case 'CONNECTION':
      return data.kind === 'ACCEPTED' ? t('connectionAccepted', { actor }) : t('connectionRequested', { actor })
    case 'REVISION_REMINDER':
      // An exam's revision task left today (lvn-backend ADR-0070): the exam is the viewer's own.
      return typeof data.examName === 'string' && data.examName ? t('revisionReminder', { exam: data.examName }) : t('revisionReminderAny')
    case 'DATA_EXPORT':
      return t('dataExport')
    case 'NOTES_IMPORT': {
      const count = (k: string) => (typeof data[k] === 'number' ? (data[k] as number) : 0)
      return t('notesImport', { created: count('created'), skipped: count('skipped'), failed: count('failed') })
    }
    default:
      return t('other')
  }
}
