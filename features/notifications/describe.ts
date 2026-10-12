import type { NotificationFieldsFragment } from '@/graphql/generated/graphql'

type Translate = (key: string, values?: Record<string, string | number>) => string

/**
 * The sentence for a notification (lvn-backend ADR-0042): written here from its category, the actor's name and the
 * note's title, which the API resolved with its own read checks. Nothing in a notification is user-written text.
 */
export function describeNotification(n: Pick<NotificationFieldsFragment, 'category' | 'data' | 'actor' | 'note'>, t: Translate): string {
  const actor = n.actor?.displayName ?? t('someone')
  const data = (n.data ?? {}) as Record<string, unknown>
  switch (n.category) {
    case 'SHARE':
      return n.note ? t('share', { actor, note: n.note.title || t('untitled') }) : t('shareGone', { actor })
    case 'VERIFICATION':
      if (data.kind === 'REQUESTED') return t('verificationRequested', { actor })
      if (data.decision === 'APPROVED') return n.actor ? t('verificationApprovedBy', { actor }) : t('verificationApproved')
      return t('verificationRejected')
    case 'FOLLOW':
      return t('follow', { actor })
    case 'CONNECTION':
      return data.kind === 'ACCEPTED' ? t('connectionAccepted', { actor }) : t('connectionRequested', { actor })
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
