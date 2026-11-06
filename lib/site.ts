/**
 * Public site facts shared by metadata, the legal pages and robots.txt.
 * NEXT_PUBLIC_* is read by its full name so Next can inline it into client bundles.
 */

/** Support, privacy and grievance mailbox. A blank override keeps the published address. */
export const SUPPORT_EMAIL = process.env.NEXT_PUBLIC_SUPPORT_EMAIL?.trim() || 'support@learnvianotes.in'

/**
 * Root description for search and link previews. Truthful to the landing page (student notes, learn, share)
 * and kept under about 160 characters.
 */
export const SITE_DESCRIPTION =
  'LearnViaNotes: student notes made simple. Learn faster with clear notes, and share notes with classmates and teachers.'

export const SITE_KEYWORDS = ['student notes', 'notes', 'learn', 'share notes', 'study notes', 'class notes', 'LearnViaNotes'] as const

/**
 * Prefixes robots.txt disallows. `/` stays allowed. These are signed-in areas, admin, settings, the API,
 * auth callbacks and the Firebase helper. `/resources` itself is public; only the private resource tools are listed.
 */
export const ROBOTS_DISALLOW = [
  '/admin',
  '/dashboard',
  '/home',
  '/settings',
  '/profile',
  '/api',
  '/oauth',
  '/__/',
  '/sign-in',
  '/sign-up',
  '/verify',
  '/reset',
  '/notes',
  '/classes',
  '/groups',
  '/community',
  '/contests',
  '/exams',
  '/ask',
  '/achievements',
  '/flashcards',
  '/github',
  '/history',
  '/notifications',
  '/projects',
  '/quick-notes',
  '/quizzes',
  '/review',
  '/rhythm',
  '/saved',
  '/search',
  '/teach',
  '/upload',
  '/unsubscribe',
  '/q/',
  '/quiz/',
  '/resources/mine',
  '/resources/new',
  '/resources/saved',
] as const
