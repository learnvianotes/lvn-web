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
| `/sign-in`, `/sign-up`, `/sign-up/details`, `/verify`, `/reset`, `/oauth/callback` | `(site)/(auth)` | Client | 1 | Live — email + password, Google (Firebase, ADR-0007), GitHub and LinkedIn (PKCE); registration details, institutional code, reset |
| `/profile` | `(site)/(app)` | Client behind auth | 1 | Live (Phase 1 account page: verification, college email, study details, old-site data, sign-out); the full profile follows in Phases 2–3 |
| `/notes`, `/notes/[id]` | `(site)/(app)` | Client behind auth | 2 | Live (P2b): notes home (welcome, templates, notes as cards, folders, tags, trash), the editor (cards as one Tiptap document, autosave with an IndexedDB mirror, history, publish, read aloud), the reader for shared notes |
| `/home`, `/groups`, `/classrooms`, `/quizzes`, `/search`, `/ai` | `(app)` | Client behind auth | 2–6 | Not started |
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
features/notes/          the notes app: model/ (editor document ⇄ cards, save planning, positions — pure, unit-tested),
                         editor/ (Tiptap nodes per card type, node views, slash menu, autosave, IndexedDB mirror),
                         render/ (read-only cards, server-safe), NotesHome, NotePage, NoteReader, dialogs
lib/contracts/           copies of @lvn/contracts code the web runs (validation, positions, enums) — pnpm contracts:sync
components/              site header/footer, theme toggle, auth/ (forms and session); components/ui/ = shadcn-style primitives only
graphql/                 operations, the API schema copy, generated typed documents
lib/                     env (Zod-validated), cn(), theme key, apollo client, auth/ (session refresh, PKCE, Google, redirects)
state/                   Zustand: theme, session (command palette, notifications, workspace arrive with their features)
i18n/, messages/         next-intl request config; English messages
tests/unit/              Vitest (core/, site/, auth/); tests/support/ = shared helpers
tests/e2e/               Playwright (desktop + Pixel 7), axe checks; auth flows run against a mocked GraphQL API
```

`graphql/`, Apollo Client, React Hook Form and Tiptap are added in the phase that first needs them (§18: "Later-phase
code is not written early").

## Decisions specific to this app

- **`/core` is the old app, kept as it was** (ADR-0002 amendment). Its content is pipeline HTML sanitised by
  `scripts/content/sanitize.mjs`, converted at build time into the old structured format by the strict
  `core-app/server/fromHtml.ts` (an unknown element or attribute fails the build) and rendered by the old
  components — never as raw HTML. User-written notes (Phase 2) are Tiptap JSON rendered through components.
- **Sessions (§7.1).** The access token lives only in memory (`state/session.ts`); the refresh token is an HttpOnly
  cookie scoped to the API's `/graphql`. On load, `AuthProvider` restores the session with `refreshSession`; refreshes
  are single-flight in a tab and serialised across tabs with the Web Locks API, because the API treats a reused
  refresh token as theft and revokes the family. `lib/apollo.ts` retries a request once after an UNAUTHENTICATED.
- **GraphQL.** Operations live in `graphql/operations/*.graphql`; `pnpm graphql:sync` copies the API schema from
  lvn-backend (`contracts/graphql/schema.graphql`) and `pnpm codegen` writes typed documents to `graphql/generated/`.
- **Providers.** Google uses Firebase Authentication, loaded only when the button is pressed and signed out of
  straight after. On https the SDK's auth domain is this site, and `/__/auth` is proxied to `<project>.firebaseapp.com`
  so the Google result stays in first-party storage. GitHub and LinkedIn use Authorization Code + PKCE with the
  verifier kept in this tab. A button shows only when both the API (`signInOptions`) and this deployment's env offer
  the provider. The API exchanges the Firebase ID token (`signInWithGoogle`) and links an email that already has an
  account; this app does not create one.
- **Theme** is applied before first paint by one inline script (`lib/theme.ts`) in each root layout. `cnote:theme`
  is JSON `"system"` (the default), `"light"`, or `"dark"`. `cnote:accent` is JSON `"navy"` (the default), `"teal"`,
  `"forest"`, `"slate"`, or `"amber"`. `data-theme` is the resolved scheme. The choice is per device, not auth data
  (§7.1), and it carries between `/` and `/core`.
- **The note editor (P2b).** A note is one Tiptap document whose top-level nodes are cards, one node type per card
  type (§12.2); rich-text cards hold paragraphs and lists, structured cards (table, question, quiz, flashcard) are atoms
  edited through forms. Every card node carries its id, position and revision, so a save sends only what changed:
  `features/notes/model/save.ts` turns the document into UPSERT / MOVE / DELETE operations with the revision the editor
  saw (§13.2) and keeps unmoved cards' fractional positions. Card content is validated before sending with the same
  `@lvn/contracts/validation` the API uses. Card ids are UUIDv7 made with `crypto.getRandomValues` (`randomUUID` is
  missing on plain-HTTP origins such as the dev machine's address).
- **Drafts are never lost.** Each change is written to IndexedDB (`lvn-notes` / `drafts`, keyed by user and note) before
  the 2 s autosave sends it; the entry is removed when the server has acknowledged everything. Offline, saves retry with
  backoff and on `online`; reopening a note sends what the mirror holds first. Signing out deletes the mirror (shared
  computers), asking first if anything is unsent.
- **Look and feel.** The brand's night-sky surface for welcomes, accents per note (a stable colour from its id), templates
  to start from, a formatting bubble on selection, a card handle (add below, move, duplicate, turn into, delete), focus
  mode, read aloud with the current card highlighted, and confetti on a first publish — never with reduced motion.
- **Contracts code.** Until @lvn/contracts is published (lvn-backend ADR-0031), `pnpm contracts:sync` copies the parts the
  web runs into `lib/contracts/`; CI checks the copies match lvn-backend.
- **Terms version (lvn-backend ADR-0103; owner default (a), which the owner may veto).**
  - **The list.** `PUBLISHED_TERMS_VERSIONS` in `features/legal/documents.ts` is the one list of versions this app has
    published, oldest first, each with a short summary of what changed. `TERMS_VERSION` is its last entry, the
    version of the text the pages ship.
  - **Who decides.** The version people accept is the API's `Query.termsVersion`. A platform admin sets it on
    /admin/settings → Legal (`features/admin/AdminTermsVersion.tsx`).
  - **What can be picked.** Only versions on both this list and the API's `terms_published_versions` allowlist. That
    allowlist is the setting, else `TERMS_PUBLISHED_VERSIONS`, else the API's built-in `2026-10-08,2026-11-03`. The
    operator keeps it equal to this list, and the card names any version that is on only one of them.
  - **Confirming.** A switch or a reset asks for a confirm saying every signed-in person is asked to accept again. The
    card shows how many people accepted each version. These counts come from the API, which hides a count below 5.
  - **The page label.** The legal pages read `Query.termsVersion` on the server (ISR, 60 s;
    `features/legal/terms-version.ts`) for their "Version" label. If the API is unreachable, they show
    `TERMS_VERSION`. If the API's version is not on the list, they show `TERMS_VERSION` and log a warning.
  - **Label and text can differ.** The pages always carry the newest text. So the label names a different version
    than the text in two cases: between deploying a new text and switching to it, and after switching back to an
    older version. Keep the gap short.
  - **To publish a version:** add it last on the list with its text, deploy, add it to `terms_published_versions`,
    then switch.
  - **Google Analytics** (ADR-0092) is not involved.
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
