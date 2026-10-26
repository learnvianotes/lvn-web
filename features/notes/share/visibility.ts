import type { Visibility } from '@/graphql/generated/graphql'

/**
 * Who the share dialog offers. The wire enum is still PRIVATE | SHARED | PUBLIC.
 * UNLISTED is the product name for a link that is not listed on public pages.
 */
export type ShareAudience = 'PRIVATE' | 'UNLISTED' | 'PUBLIC'

/**
 * Root cause of “sharing only allows Private, and changing it doesn't work”:
 *
 * 1. Each audience was an `<input type="radio" class="sr-only">`. That class is
 *    `position: absolute` with a 1×1 clipped box, so the control leaves the row
 *    and sits at the dialog's origin. A click on the row often never reaches it,
 *    and `onChange` never runs. The checked state is fully controlled, so the
 *    dialog stays on Private.
 * 2. Public was `disabled` whenever the note had no published version
 *    (`needsPublish`). Copy link was also disabled while visibility was Private.
 *    On a draft — the usual case — Public cannot be selected, and the middle
 *    option was labelled “Shared” (name people), not an unlisted link. There was
 *    no working way to hand someone a link.
 * 3. Nothing updated the selection until the mutation returned a note, so a
 *    refusal or a click that did not fire left Private looking stuck.
 */
export const SHARING_ROOT_CAUSE =
  'Clipped sr-only radios inside the share dialog do not receive the row click, and Public is disabled until the note is published, so a draft cannot leave Private.'

export function audienceOf(visibility: Visibility): ShareAudience {
  if (visibility === 'PUBLIC') return 'PUBLIC'
  if (visibility === 'SHARED') return 'UNLISTED'
  return 'PRIVATE'
}

/**
 * Assumption: the backend visibility fix keeps unlisted links on the existing
 * SHARED value (anyone with the link, not listed publicly). Person-shares still
 * attach to that note. A future UNLISTED enum value can replace this mapping
 * inside setNoteVisibility without a UI change.
 */
export function wireVisibility(audience: ShareAudience): Visibility {
  if (audience === 'UNLISTED') return 'SHARED'
  return audience
}

/** Public is selectable before publish. Moderation and the permission still block it. */
export function audienceDisabled(input: { changeVisibility: boolean; offPublic: boolean; audience: ShareAudience }): boolean {
  if (!input.changeVisibility) return true
  return input.audience === 'PUBLIC' && input.offPublic
}

export function linkEnabled(visibility: Visibility): boolean {
  return visibility !== 'PRIVATE'
}
