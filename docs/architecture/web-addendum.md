# lvn-web addendum

How the web app implements section 12 of the spec (lvn-backend `docs/architecture/lvn-architecture-v2.md`). Where this file and the spec disagree,
the spec wins unless an accepted ADR says otherwise.

## Route map

| Route | Group | Rendering | Phase | Status |
| --- | --- | --- | --- | --- |
| `/` | `(public)` | Static | 0 | Live — landing, links into `/core` |
| `/core`, `/core/[subjectId]`, `/core/[subjectId]/[itemId]` | `(public)` | SSG from `content-build/` | 0 | Live — existing study content (lvn-backend ADR-0002) |
| `/sitemap.xml`, `/robots.txt`, `/manifest.webmanifest` | — | Static | 0 | Live; robots blocks everything outside production |
| `/n/[slug]-[id]` | `(public)` | ISR, revalidated by the API on publish | 2 | Not started |
| `/u/[handle]`, `/explore` | `(public)` | SSR/ISR | 2–3 | Not started |
| `/sign-in`, `/sign-up`, `/verify`, `/reset`, `/oauth/callback` | `(auth)` | Client | 1 | Not started |
| `/home`, `/notes`, `/groups`, `/classrooms`, `/quizzes`, `/search`, `/ai`, `/profile` | `(app)` | Client behind auth | 2–6 | Not started |
| `/teacher/*`, `/group-admin/*` | `(app)` | Client, role-gated | 3 | Not started |

Old URLs from learnvianotes.in: `/<subject>` and `/<subject>/<topic>` → 301 to `/core/...`; `/about`, `/login`,
`/signup`, `/forgot-password`, `/history`, `/settings` → 307 to `/` (no equivalent until Phase 1).

## Folder map

```text
app/                     routes only; (public)/ today, (auth)/ and (app)/ from Phase 1
features/core-content/   /core: Zod schema for content-build/, loader, build-time HTML renderer, components, CSS
components/              site header/footer, theme toggle; components/ui/ = shadcn-style primitives only
lib/                     env (Zod-validated), cn(), theme key
state/                   Zustand: theme (session, command palette, notifications, workspace arrive with their features)
i18n/, messages/         next-intl request config; English messages
e2e/                     Playwright (desktop + Pixel 7), axe checks
```

`graphql/`, Apollo Client, React Hook Form and Tiptap are added in the phase that first needs them (§18: "Later-phase
code is not written early").

## Decisions specific to this app

- **Content HTML is trusted and rendered at build time.** `/core` pages render pipeline HTML that was sanitised by
  `scripts/content/sanitize.mjs`; code is highlighted with highlight.js during the build, so readers download no
  highlighter. User-written notes (Phase 2) are Tiptap JSON rendered through components — never raw HTML.
- **Tabs are progressive enhancement.** The server renders an accessible tablist; `TabsEnhancer` (client) only toggles
  `hidden`, supports arrow keys and remembers the reader's language across pages.
- **Theme** is applied before first paint by an inline script and stored under `lvn:theme` (per-device preference,
  not auth data — §7.1 storage rules are respected).
- **Search engines:** `NEXT_PUBLIC_APP_ENV` ≠ `production` sets `noindex` and a disallow-all robots.txt, so sandbox
  never competes with production.

## Brand

The LearnViaNotes logo is one set of shapes in `branding/logo-paths.json` — a copy of lvn-mobile's
`assets/brand/logo-paths.json`, kept identical until the shapes move into `@lvn/contracts`. `node branding/render-icons.mjs`
(needs `rsvg-convert`) renders `public/icons/` (SVG favicon, PNG favicons, Apple touch icon, PWA and maskable icons);
`components/brand/Logo.tsx` draws it inline in the header next to the name from `messages/en.json`. The previous app's
artwork is kept in `branding/legacy/`.

## Budgets (section 12.2) — current numbers

| Budget | Target | Now |
| --- | --- | --- |
| Route JS (first load) | < 200 kB gz | 106 kB on every route |
| Accessibility | WCAG 2.1 AA, axe in Playwright | 0 serious/critical violations on a topic page |
| LCP on public pages | < 2.5 s | Measure with Lighthouse CI once sandbox exists |
