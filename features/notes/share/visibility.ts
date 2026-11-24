/**
 * Who the share dialog offers. Contracts 0.74.0 (lvn-backend PR #47) stores these
 * four values on Visibility: PRIVATE, SHARED, UNLISTED, PUBLIC.
 */
export type ShareAudience = 'PRIVATE' | 'SHARED' | 'UNLISTED' | 'PUBLIC'

/**
 * Root cause of “sharing only allows Private, and changing it doesn't work”:
 *
 * 1. Each audience was an `<input type="radio" class="sr-only">`. That class is
 *    `position: absolute` with a 1×1 clipped box, so the control leaves the row
 *    and sits at the dialog's origin. A click on the row often never reaches it,
 *    and `onChange` never runs. The checked state is fully controlled, so the
 *    dialog stays on Private.
 * 2. Public was `disabled` whenever the note had no published version. Copy link
 *    was also disabled while visibility was Private.
 * 3. Nothing updated the selection until the mutation returned a note.
 *
 * Public is now gated by the platform setting `public_notes_require_verification`
 * (and by moderation), not by whether a version has been published.
 */
export const SHARING_ROOT_CAUSE =
  'Clipped sr-only radios inside the share dialog do not receive the row click, and Public was disabled until the note was published, so a draft could not leave Private.'

export function audienceOf(visibility: string): ShareAudience {
  if (visibility === 'PUBLIC' || visibility === 'UNLISTED' || visibility === 'SHARED') return visibility
  return 'PRIVATE'
}

/** The wire value is the audience. UNLISTED is its own enum value, not SHARED. */
export function wireVisibility(audience: ShareAudience): ShareAudience {
  return audience
}

/**
 * Public is selectable before publish. It is blocked when moderators hid the note,
 * when the viewer cannot change visibility, and when public notes require verification
 * and this account still needs to verify (`publicHeld` from the gate list).
 */
export function audienceDisabled(input: {
  changeVisibility: boolean
  offPublic: boolean
  audience: ShareAudience
  publicHeld?: boolean
}): boolean {
  if (!input.changeVisibility) return true
  if (input.audience !== 'PUBLIC') return false
  if (input.offPublic) return true
  return !!input.publicHeld
}

/** A link exists once the note is not private. Unlisted and public use /n/; shared uses the app. */
export function linkEnabled(visibility: string): boolean {
  return visibility !== 'PRIVATE'
}
