/* ============================================================
   APP CONFIG — values come from the environment (lvn-backend
   ADR-0022: no URL is written into code).
   ============================================================ */

export const APP_NAME = 'LearnViaNotes'

/** Shown in the help center and attached to feedback reports. */
export const APP_VERSION = process.env.NEXT_PUBLIC_APP_VERSION ?? 'web'

/**
 * Google Apps Script web-app URL that appends feedback to a Google Sheet (NEXT_PUBLIC_FEEDBACK_URL).
 * Empty = the form explains it isn't set up yet.
 */
export const FEEDBACK_URL = process.env.NEXT_PUBLIC_FEEDBACK_URL ?? ''
