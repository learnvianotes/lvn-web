/* ============================================================
   APP CONFIG — the few values you may want to change.
   ============================================================ */

export const APP_NAME = 'LearnViaNotes'

/**
 * Who runs the site — shown on /privacy, /terms and /grievance and in the footer.
 * A production build stops while any of these is blank (build/launch-checks.ts).
 */
export const LEGAL = {
  /** Legal name of the person or company that operates LearnViaNotes. */
  operator: '',
  /** Postal address for notices: street, city, state, PIN. */
  address: '',
  /** City whose courts hear disputes under the Terms. */
  courtsCity: '',
  /** The Grievance Officer's name (IT Rules 2021, rule 3(2); SPDI Rules 2011, rule 5(9)). */
  grievanceOfficer: '',
  /** Mailbox for privacy and grievance mail, e.g. grievance@learnvianotes.in. */
  email: '',
  /** The date the current Privacy Policy and Terms took effect (YYYY-MM-DD). Change it whenever they change. */
  effective: '2026-10-22',
}

/** How long data is kept, as the Privacy Policy states it. Change both together. */
export const RETENTION = {
  /** Daily Firestore backups (docs/runbooks/backups.md). */
  backupDays: 7,
  /** Feedback reports in the Google Sheet. */
  feedbackMonths: 12,
  /** Google Analytics → Admin → Data retention (2 or 14 months). */
  analyticsMonths: 2,
}

/**
 * Google Apps Script web-app URL that appends feedback to a Google Sheet.
 * Setup: docs/feedback-google-sheets.md. Empty = the form explains it isn't set up yet.
 */
export const FEEDBACK_URL = 'https://script.google.com/macros/s/AKfycbwbtuRhZWjI0lrGsT4z1CJSbJmGIPZ8sPnI1tYUGq5WKZ-DNq-PGBAGN6CN0sa2XTwU/exec'

/** Google AdSense client id (ca-pub-…). Empty = no ads and no ad script. */
export const ADSENSE_CLIENT = ''

/**
 * Sign-in providers shown on the login page, in order. Add one only after enabling it in
 * Firebase console → Authentication → Sign-in method (docs/auth-setup.md).
 * Email + password is always shown.
 */
export const AUTH_PROVIDERS: ('google' | 'github' | 'linkedin')[] = ['google']

/**
 * Domains where the site runs on Firebase Hosting. On these, sign-in uses the site's own domain
 * (its built-in /__/auth/handler) instead of <project>.firebaseapp.com, so mobile browsers that block
 * cross-site storage (Safari, newer Chrome/Firefox) can finish redirect sign-ins.
 * Each one needs its https://<domain>/__/auth/handler added as an authorized redirect URI of the
 * Google OAuth client (docs/auth-setup.md → "Sign-in on your own domain").
 */
// Redirect URIs are registered on the OAuth client Firebase uses (761935379919-92vi63rnkfrq5vqi5jphehsg2sd4jg7b…).
export const SAME_SITE_AUTH_DOMAINS: string[] = ['www.learnvianotes.in', 'learnvianote.web.app']
