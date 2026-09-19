# C-NOTE

**Personal Computer Science learning and interview-preparation platform.**

A clean, offline-first technical reference system covering 13 CS subjects.
Built for focused study — not for flashiness.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Framework | React 19 + TypeScript (strict) |
| Build | Vite 6 |
| Styling | Tailwind CSS v4 (Vite plugin) + CSS custom properties |
| Routing | React Router v7 |
| Icons | Lucide React |
| Fonts | Inter (UI) · JetBrains Mono (code) |
| Storage | localStorage via abstraction layer |

No backend. No database. No Firebase (Phase 1). Fully static.

---

## Project Structure

```
src/
├── app/
│   ├── App.tsx               # Root component
│   ├── router.tsx            # All routes defined here
│   └── providers/
│       └── ThemeProvider.tsx # Theme state + persistence
│
├── components/
│   ├── ui/                   # Reusable UI primitives
│   │   ├── Button.tsx
│   │   ├── IconButton.tsx
│   │   ├── Input.tsx
│   │   ├── Badge.tsx
│   │   ├── Divider.tsx
│   │   ├── Spinner.tsx
│   │   ├── Skeleton.tsx
│   │   ├── Tooltip.tsx
│   │   └── EmptyState.tsx
│   ├── layout/               # Application shell
│   │   ├── AppShell.tsx
│   │   ├── GlobalHeader.tsx
│   │   └── PageContainer.tsx
│   ├── navigation/           # Navigation components
│   │   ├── Breadcrumbs.tsx
│   │   └── MobileNavigation.tsx
│   └── feedback/             # Error/loading states
│       ├── ErrorBoundary.tsx
│       ├── ErrorState.tsx
│       ├── LoadingState.tsx
│       └── NotFound.tsx
│
├── contexts/
│   └── ThemeContext.tsx       # Theme context (createContext only)
│
├── features/
│   └── theme/
│       └── ThemeToggle.tsx   # Theme toggle button
│
├── hooks/
│   └── useTheme.ts           # Theme hook
│
├── pages/
│   ├── HomePage.tsx
│   ├── SubjectsPage.tsx
│   ├── SubjectDetailPage.tsx
│   ├── TopicDetailPage.tsx
│   ├── QuestionDetailPage.tsx
│   ├── DesignSystemPage.tsx  # Internal design reference
│   └── NotFoundPage.tsx
│
├── lib/
│   └── storage.ts            # localStorage abstraction
│
├── types/
│   ├── subject.ts            # Domain model
│   ├── theme.ts              # Theme types
│   └── common.ts             # Shared utility types
│
├── styles/
│   ├── tokens.css            # CSS custom properties (design tokens)
│   ├── typography.css        # Font imports + type hierarchy
│   ├── global.css            # Base resets + import orchestration
│   ├── components.css        # All component styles
│   ├── layout.css            # Shell, header, container styles
│   └── pages.css             # Page-specific styles
│
├── content/                  # Future: Markdown learning content
│   └── README.md
│
└── data/                     # Application metadata registries
    ├── subjects.ts           # 13 subjects (Phase 1: metadata only)
    └── README.md
```

---

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

---

## Architecture

### Theme System

- Themes: `dark` (default) | `light`
- Theme is stored in `localStorage` via the storage abstraction
- An inline script in `index.html` reads the stored value before React mounts (prevents flash)
- `ThemeProvider` manages state and sets `data-theme` on `<html>`
- Components consume CSS custom properties — no JS theme logic inside components

### Design Token System

All visual values live in `src/styles/tokens.css` as CSS custom properties.

```css
/* ✅ Correct — semantic token */
background-color: var(--color-surface);

/* ❌ Wrong — hardcoded value */
background-color: #161b27;
```

Two theme sets:
- `:root` / `[data-theme="dark"]` — dark theme (default)
- `[data-theme="light"]` — light theme

### Storage Abstraction

```ts
import { get, set, remove, STORAGE_KEYS } from '@/lib/storage'

// Theme is stored like this:
set(STORAGE_KEYS.THEME, 'dark')
const saved = get<Theme>(STORAGE_KEYS.THEME)
```

Currently backed by `localStorage`. The interface allows swapping to
IndexedDB or Firebase without touching consumer code.

### Content Architecture

- `src/data/` — Structured TypeScript metadata (subjects, topics, question index)
- `src/content/` — Actual Markdown learning content (populated Phase 2+)

The UI navigates using lightweight data. Content is loaded per-question
(lazy) in future phases. See `src/data/README.md` and `src/content/README.md`.

---

## Routes

| Path | Page |
|---|---|
| `/` | Home — subject overview |
| `/subjects` | All subjects list |
| `/subjects/:subjectId` | Subject detail + topics |
| `/subjects/:subjectId/topics/:topicId` | Topic detail + questions |
| `/subjects/:subjectId/topics/:topicId/questions/:questionId` | Question detail |
| `/design-system` | Internal Design Lab |
| `*` | 404 Not Found |

---

## Subjects (13 Total)

1. Sheet 150
2. Computer Networks
3. Operating Systems
4. DBMS
5. OOPs
6. Cryptography
7. System Design
8. Git & GitHub
9. API Design
10. DSA — Basics
11. DSA — Advanced
12. Machine Learning & AI
13. GenAI Fluency

---

## Current Phase

**Phase 1 — Frontend Foundation** ✅

This phase establishes the architecture. No real learning content has been added.

Future phases will populate content, implement question pages, search,
progress tracking, and optional Firebase sync.

### Phase 1 Checklist

- [x] Application runs
- [x] TypeScript strict mode compiles
- [x] Production build passes
- [x] All routes work
- [x] 404 page works
- [x] Error boundary exists
- [x] Dark theme works
- [x] Light theme works
- [x] Theme persists after refresh
- [x] Application shell works
- [x] Responsive layout works
- [x] Mobile navigation works
- [x] UI primitives exist
- [x] Design Lab exists at `/design-system`
- [x] Semantic design tokens defined
- [x] Storage abstraction exists
- [x] Domain types defined
- [x] Content/data directories exist with READMEs
- [x] No Sheet 150 content migrated
- [x] No Firebase added
- [x] No backend added
