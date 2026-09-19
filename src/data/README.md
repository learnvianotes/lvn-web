# src/data/

This directory contains **application metadata and registries** — structured TypeScript data files
that define the shape and organization of C-NOTE content.

## Current Files

| File | Purpose |
|------|---------|
| `subjects.ts` | All 13 C-NOTE subjects (metadata only — no content) |

## Future Files (Phase 2+)

| File | Purpose |
|------|---------|
| `topics.ts` | All topics across all subjects |
| `questions.ts` | All question metadata (title, difficulty, tags) |
| `registry.ts` | Combined ContentRegistry for the app to consume |

## Principles

- Data files export **typed TypeScript arrays/objects** — no raw JSON
- UI components import from `@/data/` not from `@/content/`
- `@/content/` holds the actual Markdown learning content
- `@/data/` holds the index/registry that the UI navigates

## Why separate data from content?

The UI (navigation, subject lists, breadcrumbs, routing) needs lightweight
structured data to render quickly. It does not need to load full Markdown
content until a specific question page is opened.

This separation enables:
- Fast initial load (data is tiny)
- Lazy content loading per question (future)
- Type-safe navigation without parsing Markdown

## Phase Status

✅ `subjects.ts` — 13 subjects with metadata
❌ `topics.ts` — Phase 2
❌ `questions.ts` — Phase 2
❌ `registry.ts` — Phase 2
