/* Help center articles. `body` is plain text; blank lines separate paragraphs, "- " starts a bullet. */

export interface HelpArticle {
  id: string
  topic: 'Getting started' | 'Streak & progress' | 'Study tools' | 'Account & privacy' | 'App'
  title: string
  body: string
  keywords?: string
}

export const ARTICLES: HelpArticle[] = [
  {
    id: 'account-needed', topic: 'Getting started', title: 'Do I need an account?',
    body: `No. Every note and all 150 coding problems are free to read without signing in.

Signing in adds the extras:
- Your study streak and calendar
- History: which topics you visited, when, and for how long
- Read-aloud, the smart study kit, focus timer and personal notes
- Solved / revisit marks, a review queue, and your own subject order
- Everything synced across your devices`,
    keywords: 'login signup free guest',
  },
  {
    id: 'find', topic: 'Getting started', title: 'Finding a topic or problem',
    body: `Press / (or ⌘K / Ctrl K) anywhere to search subjects, topics, headings and problems by name or LeetCode number.

On the home page, use the filter chips (DSA, CS Fundamentals, …) to narrow the subjects. “Explore more courses” lists what’s coming next.`,
    keywords: 'search filter shortcut leetcode',
  },
  {
    id: 'streak', topic: 'Streak & progress', title: 'How does the streak work?',
    body: `A day counts toward your streak when you complete a topic, solve a problem, or study for at least a minute (reading, listening or a focus session).

The streak is the number of days in a row that count, ending today — or yesterday, so you still have today to keep it alive.

Click any day in the calendar to see what you studied then.`,
    keywords: 'calendar days fire',
  },
  {
    id: 'tracked', topic: 'Streak & progress', title: 'What exactly is tracked?',
    body: `While you're signed in:
- Topics you open, with the date and time
- Active study time per topic (only while the tab is visible and you're reading, scrolling or listening — idle time doesn't count)
- Revisits: a topic you studied on an earlier day
- Completed topics, solved / revisit problems, focus sessions

Nothing is tracked when you're signed out.`,
    keywords: 'history time spent metrics analytics',
  },
  {
    id: 'completed', topic: 'Streak & progress', title: 'When is a topic marked “Completed”?',
    body: `When you reach the end of it and have spent real reading time on it (scaled to its length). Skimming straight to the bottom doesn't count.

Click the “Completed” badge to mark it unread again.`,
    keywords: 'done read finish',
  },
  {
    id: 'review', topic: 'Streak & progress', title: 'The review queue',
    body: `Completed topics come back for review after 1, 3, 7, 14 and 30 days — spaced repetition, so they stick.

Use “Revisit later” on any topic to add it to the queue straight away. You'll find the queue on the home page and in Study history.`,
    keywords: 'spaced repetition revise revisit',
  },
  {
    id: 'listen', topic: 'Study tools', title: 'Read-aloud',
    body: `Press “Listen” on a topic (or the headphones on a problem) to have it read to you. The paragraph being read is highlighted and followed.

- K pauses and resumes, Esc stops
- Change speed and voice in the player
- Voices come from your device; Chrome and Edge usually have the most natural ones`,
    keywords: 'voice speak audio tts',
  },
  {
    id: 'kit', topic: 'Study tools', title: 'Smart study kit',
    body: `Above every topic: quick notes (the key sentence of each section), side headings to jump around, the key terms and must-remember points, and your own notes.

It's generated instantly from the topic itself, works offline, and “Explain it to me” reads the recap aloud.`,
    keywords: 'quick notes summary side headings remember',
  },
  {
    id: 'focus', topic: 'Study tools', title: 'Focus timer',
    body: `The timer in the header runs focus sessions of 15–60 minutes (or your own length) with an optional break. Completed focus minutes count toward your streak.

It keeps running if you reload or switch pages.`,
    keywords: 'pomodoro timer concentrate',
  },
  {
    id: 'arrange', topic: 'Study tools', title: 'Sorting and rearranging subjects',
    body: `Signed in, use the sort menu above the subjects (recommended, recently studied, most progress, A–Z) or “Rearrange” to drag them into your own order. Your order is saved to your account.`,
    keywords: 'order sort drag customize',
  },
  {
    id: 'signin', topic: 'Account & privacy', title: 'Trouble signing in',
    body: `- Google / GitHub / LinkedIn: allow pop-ups for this site, or try again — on some phones the sign-in opens as a full page instead.
- “This email already uses a different sign-in method”: sign in with the method you used first.
- Forgot your password: use “Forgot password?” on the sign-in page. For your privacy we never say whether an email is registered.
- Still stuck? Tell us in the Report tab.`,
    keywords: 'login password reset google github linkedin error',
  },
  {
    id: 'privacy', topic: 'Account & privacy', title: 'Your data and privacy',
    body: `We store your name, email, study progress, activity and notes — only to power your streak, history and recommendations. It's never sold or shared.

- Signing out removes your study data from that device
- Delete your account (and all of its data) anytime from the account menu`,
    keywords: 'delete account data gdpr',
  },
  {
    id: 'offline', topic: 'App', title: 'Install the app & offline use',
    body: `- Android (Chrome): menu → Install app
- iPhone (Safari): Share → Add to Home Screen

Pages you've opened once stay available offline.`,
    keywords: 'pwa install offline phone',
  },
]

export const SHORTCUTS: { keys: string[]; action: string }[] = [
  { keys: ['/'], action: 'Search' },
  { keys: ['⌘', 'K'], action: 'Search (Ctrl K on Windows)' },
  { keys: ['↑', '↓', '↵'], action: 'Pick a search result' },
  { keys: ['K'], action: 'Pause / resume read-aloud' },
  { keys: ['Esc'], action: 'Close dialogs, stop read-aloud' },
]
