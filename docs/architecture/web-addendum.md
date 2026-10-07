# lvn-web addendum

How the web app implements section 12 of the spec (lvn-backend `docs/architecture/lvn-architecture-v2.md`). Where this file and the spec disagree,
the spec wins unless an accepted ADR says otherwise.

## Route map

| Route | Group | Rendering | Phase | Status |
| --- | --- | --- | --- | --- |
| `/` | `(site)/(public)` | Static | 0 | Live — landing, links into `/core` |
| `/core`, `/core/about`, `/core/[subjectId]`, `/core/[subjectId]/[itemId]` | `(core)` — own root layout | SSG shell + the old app routing client-side | 0 | Live — the old site's app in guest mode (lvn-backend ADR-0002 amendment) |
| `/core/data/*.json` | `(core)` | Static route handler | 0 | Live — content documents for the old app |
| `/sitemap.xml`, `/robots.txt`, `/manifest.webmanifest` | — | Static | 0 | Live; robots blocks everything outside production |
| `/n/[slug]-[id]` | `(public)` | ISR, revalidated by the API on publish | 2 | Not started |
| `/u/[handle]`, `/explore` | `(public)` | SSR/ISR | 2–3 | Not started |
| `/sign-in`, `/sign-up`, `/verify`, `/reset`, `/oauth/callback` | `(auth)` | Client | 1 | Not started |
| `/home`, `/notes`, `/groups`, `/classrooms`, `/quizzes`, `/search`, `/ai`, `/profile` | `(app)` | Client behind auth | 2–6 | Not started |
| `/teacher/*`, `/group-admin/*` | `(app)` | Client, role-gated | 3 | Not started |

Old URLs from learnvianotes.in: `/<subject>`, `/<subject>/<topic>` and `/about` → 308 to `/core/...`; `/login`,
`/signup`, `/forgot-password`, `/history`, `/settings` → 307 to `/` (no equivalent until Phase 1). Unknown URLs get
`app/global-not-found.tsx`; unknown `/core` paths get the old app's own "Page not found" with a 404 status.

## Folder map

```text
app/                     routes only. (site)/ = the new site's root layout: (public)/ today, (auth)/ and (app)/ from
                         Phase 1. (core)/ = /core's root layout and routes. global-not-found.tsx for unmatched URLs
core-app/                the old learnvianotes.in app, guest mode (src/, schema/), and server/ = build-time
                         conversion of content-build/ into the documents it reads
features/core-content/   the landing page's catalog loader (Zod schema for content-build/catalog.json) and subject cards
components/              site header/footer, theme toggle; components/ui/ = shadcn-style primitives only
lib/                     env (Zod-validated), cn(), theme key
state/                   Zustand: theme (session, command palette, notifications, workspace arrive with their features)
i18n/, messages/         next-intl request config; English messages
tests/unit/              Vitest (core/ and site/); tests/support/ = shared helpers
tests/e2e/               Playwright (desktop + Pixel 7), axe checks
```

`graphql/`, Apollo Client, React Hook Form and Tiptap are added in the phase that first needs them (§18: "Later-phase
code is not written early").

## Decisions specific to this app

- **`/core` is the old app, kept as it was** (ADR-0002 amendment). Its content is pipeline HTML sanitised by
  `scripts/content/sanitize.mjs`, converted at build time into the old structured format by the strict
  `core-app/server/fromHtml.ts` (an unknown element or attribute fails the build) and rendered by the old
  components — never as raw HTML. User-written notes (Phase 2) are Tiptap JSON rendered through components.
- **Theme** is applied before first paint by an inline script in each root layout and stored under `cnote:theme`
  (the old site's key, JSON-encoded) so the choice carries between `/` and `/core` (per-device preference, not auth
  data — §7.1 storage rules are respected).
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
| Route JS (first load) | < 200 kB gz | Landing 124 kB transferred. `/core` 200 kB — the old app with its router and highlighter, as on the old site; at the limit, so new `/core` code needs a matching cut |
| Accessibility | WCAG 2.1 AA, axe in Playwright | Landing: 0 serious/critical. `/core` topic: only the old design's known findings (ADR-0002 amendment) |
| LCP on public pages | < 2.5 s | Measure with Lighthouse CI once sandbox exists |
