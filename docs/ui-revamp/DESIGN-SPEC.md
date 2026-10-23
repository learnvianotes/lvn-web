# LearnViaNotes design spec

Normative values live in [`tokens.json`](./tokens.json). Web maps them to CSS variables in `app/globals.css` (product) and `core-app/src/shared/styles/base.css` (reader). Mobile should read `tokens.json` and this document, not Tailwind class names.

The product is a study tool for college and interview preparation, 18+, global audience. One navy, ink, and paper. No purple, violet, indigo, lavender, pink gradients, sparkle marks, dummy testimonials, or invented statistics.

## Themes

`data-theme` on the root is `light` or `dark`, chosen before first paint from `cnote:theme` (JSON `"light"` or `"dark"`), otherwise the system preference. The toggle writes that key. Do not use a third theme.

| Token | CSS variable | Use |
| --- | --- | --- |
| paper | `--bg` | Page background |
| surface | `--surface` | Cards, header, dialogs, inputs |
| surfaceMuted | `--surface-2` | Wells, hover, skeletons, code chips |
| ink | `--fg` | Primary text |
| inkSecondary | `--text-2` on the reader only | Secondary prose |
| inkMuted | `--muted` | Help, meta, placeholders |
| line | `--border` | Borders, dividers |
| lineStrong | `--border-strong` on the reader | Stronger rules |
| brand | `--accent` | Links, primary buttons, current nav |
| brandHover | `--accent-hover` | Primary button hover |
| brandForeground | `--accent-fg` | Text on brand |
| brandSoft | `--accent-soft` | Selected nav, icon wells, eyebrows |
| success | `--good` | Success text and borders |
| warning | `--warn` | Warning text |
| danger | `--bad` | Errors, invalid fields |
| info | `--def` | Definitions, secondary category |
| inverse | `--inverse` | Ink panels (sign-in hero, contest hero, notes greeting) |
| inverseInk | `--inverse-ink` | Text and buttons on inverse |
| inverseMuted | `--inverse-muted` | Secondary text on inverse |

Category hues (reader landing only) are `category` in `tokens.json`: dsa, fundamentals, engineering, ai, programming. AI is navy, not pink.

## Type

Family: Inter for UI, JetBrains Mono for code. Weights: 400 body, 500–600 labels, 700 titles, 800 the marketing and home headings only.

| Token | Size / line | Use |
| --- | --- | --- |
| xs | 12 / 16 | Meta, kbd, eyebrows |
| sm | 14 / 20 | Secondary, form errors, buttons |
| md | 16 / 24 | Body, inputs |
| lg | 18 / 28 | Leads |
| xl | 20 / 28 | Card titles |
| 2xl | 24 / 32 | Page titles in the app |
| 3xl | 30 / 36 | Public page titles |
| 4xl | 36 / 40 | Marketing heading, narrow |
| 5xl | 48 / 52 | Marketing heading, from 640px |

Tracking tightens as size grows (see `tokens.json`). Use `text-wrap: balance` on headings and `pretty` on leads. Do not set a heading level for decoration: each page has one `h1`.

## Space, radius, shadow, motion

Space is a 4px grid: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80.

| Radius | px | Use |
| --- | --- | --- |
| sm | 6 | Skeletons, small chips |
| md | 10 | Inputs on the reader |
| lg | 14 | Buttons, inputs, alerts (`rounded-xl` is 12; new work uses 14) |
| xl | 18 | Cards |
| 2xl | 24 | Feature panel, heroes |
| pill | 999 | Wordmark actions, tags |

Shadows: `sm` under cards, `md` under menus and dialogs. No coloured glow.

Motion: 120ms colour, 180ms opacity. The welcome fade is opacity only (no translate), 500ms, ease `cubic-bezier(0.2, 0.8, 0.2, 1)`. `prefers-reduced-motion: reduce` disables animation and transition.

## Layout

| Name | px | Rule |
| --- | --- | --- |
| contentMax | 1152 | Page column |
| readingMax | 768 | Note and legal prose |
| sidebar | 248 | App nav, from 1024px |
| header | 56 | Plus `safe-area-inset-top` |
| touchMin | 40 | Icon buttons and row targets |
| pagePadding | 16 | Horizontal padding |

Breakpoints: 640, 768, 1024. Below 1024 the app sidebar is a drawer. Below 768 the public header links move into Site menu.

## Components

### Button

- **Primary:** brand fill, brandForeground text, hover brandHover, height 44 (md) or 48 (lg), horizontal padding 20 or 24, radius lg or pill for marketing. Disabled: 50% opacity, no pointer.
- **Secondary:** surface, line border, ink text, hover surfaceMuted.
- **Ghost:** muted text, hover surfaceMuted and ink.
- **Icon:** 40×40, ghost.
- Focus: 2px brand outline, 2px offset. Do not remove it.

### Input

Height 44, full width, radius lg, surface fill, line border, ink text, muted placeholder. Focus: brand border and a 2px brand ring at 30% opacity. Invalid: danger border, `aria-invalid`, error id in `aria-describedby`. Disabled: 60% opacity.

### Field

Label (14px, medium) above the control, 6px gap. Optional hint 12px muted. Error 12px danger, `role="alert"`, tied with `aria-describedby`.

### Alert

Radius lg, 16×12 padding, 14px. `info`: brandSoft. `success`: success at 10% on a success border. `error`: danger at 10%, `role="alert"`. Other tones are `role="status"`.

### Dialog

Native `<dialog>`. Surface panel, line border, radius 2xl, shadow md, width `100% - 32px`, max 448px (or 768px when wide). Side drawer: full height, 448px from 640px. Title is an `h2`. Close is an X icon, 40×40, name "Close". Escape and backdrop click close, unless `persistent`.

### Loading

`role="status"`, live polite. Visible text "Loading…" plus three skeleton bars (16px, 16px, 96px tall) in a 448px column. Skeletons are surfaceMuted; they shimmer only when motion is allowed. They do not change layout size.

### Load failed

Error alert: "This could not be loaded." and a secondary button "Try again". The session check uses "LearnViaNotes did not answer. Check your connection and try again." instead of the first sentence. Retry stays disabled while the request is in flight.

### Empty

Dashed line border, radius 2xl, padding 24×40, centered muted text. The sentence is the screen's own copy (do not invent a generic joke).

### Inverse panel

`inverse` fill, `inverseInk` text, 4px brand strip on the top edge. No orbs, no gradient. Used for the sign-in hero, the notes greeting, the public-note call to action, and the open contest card.

### Wordmark

Logo tile 30px (decorative) plus "LearnVia" in ink and "Notes" in brand, extrabold. The link name is "LearnViaNotes". Destination is `/` until the tab is signed in, then `/home`.

### App shell (signed in)

Skip link "Skip to content", visible on focus, target `#main`.

Sidebar (from 1024px): wordmark, then nav "Main":

| Label | Path |
| --- | --- |
| Home | /home |
| My Notes | /notes |
| Explore | /search |
| Subjects | /subjects |
| Groups | /groups |
| Classrooms | /classes |
| Exams | /exams |
| Quizzes | /quizzes |
| Contests | /contests |
| Rhythm | /rhythm |
| Resources | /resources |
| Community | /community |
| AI Assistant | /ask |
| Bookmarks | /saved |

Current item: brandSoft background, brand text, `aria-current="page"`. Others: muted, hover surfaceMuted. Footer of the nav: "Upload a PDF" when uploads are on, then primary "Create Note".

Top bar: Menu (below 1024, `aria-expanded`), search field "Search notes, topics, people, or ask AI…", theme, notifications, avatar (first letter of the display name) to `/profile`, name "Your account". Drawer name "Menu", close "Close the menu". Opening the drawer moves focus to Close and locks body scroll. Escape or Close returns focus to Menu.

### Public header

Same wordmark rule. From 768px: Features (`/#features`), Subjects (`/subjects`), Community (`/community`), Get Started (`/sign-up`, hidden once signed in). Resources from 1024px. Search, notifications, account or "Sign in", theme. Below 768px a "Browse" button opens those links plus Resources and Get Started. It is not named "Menu" (that name is the signed-in app drawer).

### Theme toggle

Name "Switch to dark theme" or "Switch to light theme". Moon in light, sun in dark.

## States

| State | What the person sees |
| --- | --- |
| Session unknown | Skeleton and "Loading…" inside the app frame. No redirect yet. |
| Session unreachable (8s or network error on the first check) | The offline sentence and Try again. No redirect to sign-in. |
| Signed out on an app route | Redirect to `/sign-in?next=<path>`. |
| Query loading, no data yet | Loading skeleton. Do not show an empty state. |
| Query failed, no data | Load failed and Try again. Do not show "nothing here" or a form that would save over unread data. |
| Query ok, empty | The screen's empty sentence. |
| Missing public subject, topic, note, or profile | Real 404: "Page not found." / "This page doesn't exist or is no longer public." / "Go home". |
| Catalogue request failed | Heading "Subjects" and "Subjects could not load just now. Try again in a moment." Not a 404. |
| Server render threw | "This could not be loaded.", the offline sentence, Try again. |

## Screens

Copy below is the English string. Routes and actions stay as they are.

### `/` Landing

Public header. One column below 1024px, two columns from 1024px (copy, then the note illustration).

- Eyebrow: "Built by students, learn together"
- H1: "Your Learning Community for a Brighter Tomorrow" (the last two words in brand)
- Lead: "Create notes, share knowledge, prepare for exams, learn with AI and grow together."
- Signed out: "Get Started Free" → `/sign-up`, "Already have an account? Sign in", "Browse subjects" → `/subjects`
- Signed in: "Open your home" → `/home`, "Your account" → `/profile`. No Get Started.
- Region "What you can do", six equal tiles: Smart Notes (`/notes`), AI Learning (`/ask`), Study Groups (`/groups`), Exam Prep (`/exams`), Quizzes & Flashcards (`/review`), Community (`/community`). Icon well is brandSoft for every tile.
- If subjects load: h2 "Subjects", link "All subjects", up to nine subject cards. If they do not, the block is omitted (the subjects page says why).

Illustration: a note, a small tree, flashcards ("What is a BST?"), a cap, and a chip "Explain simply". Paper, navy, amber, teal. No pink, no sparkle glyph. Accessible name: "A note, flashcards and a question answered".

### `/subjects`, `/subjects/[slug]`, `/subjects/[slug]/[topic]`

Public frame, or the app shell when signed in (not on `/`).

- Index h1 "Subjects". Lead: "The subjects and topics notes on LearnViaNotes are organised by. Each topic gathers the public notes and resources people share on it." Cards link to `/subjects/{slug}`.
- Subject h1 is the subject title. Breadcrumb "Where you are": Subjects › title. H2 "Topics".
- Topic h1 is the topic title. Breadcrumb adds the subject and any parent. H2 "Subtopics" when there are children. Region "Public notes". Empty: "No public notes on {topic} yet." and "Write one".
- Down: see States. Missing slug: 404.

### `/resources` and `/resources/[id]`

Catalogue is a filterable grid (type, query, sort). A card's picture is decorative; the title is the link name. Loading and failure use the shared states, including while the session is still unknown.

Resource page: title, status if it is not approved, discussion when approved. Loading is the skeleton, not a blank box. A failed load is Try again. A real miss is the resource not-found copy.

### `/n/[slug]`

Server-rendered public note. Inverse panel at the foot invites sign-up ("the call to action" strings in `publicNote`) and a link back into the note. A missing note is 404. A failed fetch is the route error screen.

### `/u/[handle]`

Public profile. Tabs and empty dashes use that screen's own sentences.

### Legal and `/unsubscribe`

`/legal/terms`, `/legal/privacy`, `/legal/content-licence`, `/legal/grievance`. Prose column, reading max, the document's own h1. Unsubscribe keeps its result text if the app frame arrives late.

### Auth (`/sign-in`, `/sign-up`, `/sign-up/details`, `/verify`, `/reset`, `/oauth/callback`)

Public header. From 1024px: inverse panel beside a surface card. Below that, the panel is a banner and the form is a sheet overlapping it by 24px.

Inverse copy: "Turn your notes into knowledge that sticks." / "Learn, revise and share with your class — at your own pace." Chips from 640px: "All your notes in one place", "A weekly Rhythm, not a streak to lose", "Learn together with your class".

Sign in h1 "Sign in". Lead "Welcome back. Pick up where you left off." Fields Email, Password. Submit "Sign in". "Forgot your password?" → `/reset`. "New to LearnViaNotes? Create an account". Errors: "Enter a valid email address.", "Required", or "Something went wrong. Try again." Provider buttons only when configured.

Sign up h1 "Create your account". Fields: name, email, password (hint "At least 10 characters. Avoid passwords you use elsewhere."), date of birth, optional college email, terms checkbox. "I'm here to" Learn or Teach. Submit "Create account".

Details: "Almost there". Reset: "Reset your password" then "Choose a new password". Verify and the OAuth callback use their `auth.verify` and `auth.callback` strings, including "Checking your link…" and "Signing you in…".

### App home `/home`

H1 is the time-of-day greeting with the first name, or the anonymous greeting. Daily line when it has arrived, otherwise the home lead. Cards: continue a note, next exam, week's Rhythm. Recommendations are picture cards in navy, teal, and amber (not pink). Rooms: groups and classes. Each card stays on Loading or Try again until its own query returns. Empty is that card's sentence, not a fake number.

### Notes `/notes` and `/notes/[id]`

Greeting panel (inverse) when viewing all notes: time-of-day line, h1 either the first-note line or the with-notes line, "Create Note", and when uploads are on "Read a PDF" and photos. Continue chip when a latest note exists. Sidebar from 768px: views, folders, tags. Phones: a horizontal scroller of the same views. A failed list says it could not be loaded and does not say "Start your first note".

The note page is the editor or the reader. Do not restyle the document model. Chrome uses the same buttons, fields, and inverse rules.

### Search `/search`

Opened from the top bar (and Ctrl/⌘K). Dialog name "Search notes, people, groups and topics". "Ask AI" sends the typed words to `/ask?q=` and does not send them until the person confirms.

### Groups, classes, exams, quizzes, contests, rhythm, community, ask, bookmarks, review

Each is the app shell plus:

- H1 from that screen's `title` in `messages/en.json` (`groups`, `classes`, `exams`, `quizzes`, `contests`, `rhythm`, `community`, `ai`, `saved`, `review`).
- Lead under the title when the namespace has one.
- Primary action in the page header (create, join, plan) as a primary button.
- List or board of cards on surface, line border, radius xl.
- Empty dashed well with that screen's empty sentence.
- Failure: shared load-failed. Never an empty well when the request failed.

Contest hero (the open weekly contest) is an inverse panel: eyebrow "Weekly", the contest title as h2, question count and minutes, primary join/continue link. Trophy in amber.

Ask: the question field is labelled "Your question". Answers list shows Loading while the first page loads. A running answer stays on the card; failure uses the answer's error text.

### Profile, people, skills, notifications, achievements, history, teach

`/profile` and its tabs (notifications, people, skills). Skills does not render the form until the profile has loaded. Achievements h1 "Achievements" with the real points copy (no invented totals). History and teach follow the same header, list, empty, and error pattern.

### Admin

`/admin/verification`, `/admin/moderation`, `/admin/contests`, `/admin/ai`. Sidebar groups People, Content, AI. Current row is brandSoft and brand text. These screens were not restructured. Allowlist and plans are not in this tree; when they arrive they should use this shell, these tokens, and these states.

### `/core` (off unless enabled)

Reader shell: sticky header 56px, wordmark to the reader home, search, help, theme. Study pages use a contents drawer below 1024px. Loading is a spinner with "Loading…" after 200ms (so a cache hit does not flash). Error: "Couldn't load this content" and Try again. Not found: "Page not found" / "This subject or topic doesn't exist." / "Back to home". The launch splash shows the name and "Opening notes…", then yields to that shell as soon as the app mounts. Catalogue fetches give up after 8 seconds and show the error, not a blank page.

## What mobile must match

- Every token in `tokens.json`, both themes.
- The same English strings (or the same keys once mobile has a catalogue).
- Wordmark destination: marketing home vs app home.
- The same nav order and routes.
- The same four data states: loading skeleton, failed with retry, empty sentence, content.
- Touch targets at least 40px. Safe area on the header. One thumb menu below the large breakpoint, not a second product.
- No purple, no pink feature tiles, no sparkle, no fake social proof.
