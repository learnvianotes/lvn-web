# lvn-web

The LearnViaNotes web app — Next.js 15, React 19, Tailwind, shadcn-style UI, next-intl.
Architecture: lvn-backend `docs/architecture/lvn-architecture-v2.md` (the single source of truth for all three
repositories) and this app's [web addendum](docs/architecture/web-addendum.md).

Phase 0: the landing page and the existing study notes at **/core** (lvn-backend ADR-0002).
Accounts and user notes arrive with the backend in Phase 1–2.

`/core` is the old learnvianotes.in app in guest mode, unchanged for readers (`core-app/`, ADR-0002 amendment):
its own root layout `app/(core)/`, client-side routing under `/core`, and content served as static JSON from
`/core/data/*`, built from `content-build/`. The new site lives in `app/(site)/`.

## Develop

```bash
pnpm install
cp .env.example .env          # every URL comes from here; personal overrides go in .env.local
pnpm dev            # http://localhost:3000 (bound to 0.0.0.0)
pnpm lint && pnpm typecheck && pnpm test
pnpm test:e2e       # builds to .next-e2e and starts it on :3100 (a running `pnpm dev` is not touched)
```

## Tests

| Folder | Runner | What |
| --- | --- | --- |
| `tests/unit/core` | Vitest | `/core` data documents, page titles, the HTML converter, and the fidelity check: every content fragment rendered by the old `ContentView` must match its source HTML |
| `tests/unit/site` | Vitest | the landing page's catalog loader |
| `tests/e2e` | Playwright (desktop + Pixel 7) | `/core` as a guest (navigation, code tabs, search, theme, 404, redirects, accessibility) and the landing page |
| `tests/support` | — | shared helpers (`fidelity.ts`) |

## Content

`/core` pages and their JSON are generated at build time from `content-build/`. To change a subject, edit its source under
`content-src/authoring/<subject>/` and run `pnpm content:<subject>` (e.g. `pnpm content:dsa-basics`), then rebuild.
