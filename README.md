# lvn-web

The LearnViaNotes web app — Next.js 15, React 19, Tailwind, shadcn-style UI, next-intl.
Architecture: lvn-backend `docs/architecture/lvn-architecture-v2.md` (the single source of truth for all three
repositories) and this app's [web addendum](docs/architecture/web-addendum.md).

Phase 0: the landing page and the existing study notes at **/core** (lvn-backend ADR-0002).
Accounts and user notes arrive with the backend in Phase 1–2.

## Develop

```bash
pnpm install
cp .env.example .env          # every URL comes from here; personal overrides go in .env.local
pnpm dev            # http://localhost:3000 (bound to 0.0.0.0)
pnpm lint && pnpm typecheck && pnpm test
pnpm build && pnpm test:e2e     # Playwright starts `next start` on :3100
```

## Content

`/core` pages are generated at build time from `content-build/`. To change a subject, edit its source under
`content-src/authoring/<subject>/` and run `pnpm content:<subject>` (e.g. `pnpm content:dsa-basics`), then rebuild.
