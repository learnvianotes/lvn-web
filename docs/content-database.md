# Study content in Firestore

All study content — 14 subjects, 258 topics, 150 problems — lives in **Firestore**. The website
ships no content files; it reads everything from the database and caches it on the device.

## Pipeline

```
content-src/                  sources (legacy HTML, Python notes authored in code, solution files)
   │  npm run content:extract      scan + normalize (scripts/content/extract.mjs)
   ▼
content-build/                scanned content as JSON (the seed input — not served)
   │  npm run content:seed         convert → verify → write → read back → verify
   ▼
Firestore                     structured content, read by the app
```

`npm run content:seed` converts every HTML fragment (1,132 of them) into **structured content**
(`schema/content.ts`) and refuses to write unless every fragment, rendered with the app's own
components, reproduces its source exactly — elements, classes, attributes, text and code. After
writing it reads everything back from Firestore and checks again.

| Command | Does |
|---|---|
| `npm run content:seed:check` | Convert + verify only (no database needed) |
| `npm run content:seed` | Seed the **local emulator** (start it with `npm run emulators`) |
| `npm run content:seed:live` | Seed the **live project** (asks you to type the project id) |

Seeding is idempotent: unchanged content produces the same version; documents that no longer exist
in the source are deleted.

## Structured content

Each topic is a tree of typed nodes — `section`, `heading`, `paragraph`, `list` / `listItem`,
`codeBlock` (`lang`, `label`, `value`), `callout` (`variant`: def · example · note · warn · good · bad),
`grid` / `card`, `table` / `tableRow` / `tableCell`, `flow*`, `step*`, `chips` / `chip`, `kv*`,
`formula`, `bits`, `gantt*`, `tabs` / `tabPanel`, `qa` / `qaQuestion`, `svg`, and inline `text`,
`strong`, `em`, `code`, `link`, `icon`, `br`, …

The web app renders each type with one component (`src/features/content/`). A native app can do the
same with native components.

**Stored flat.** Firestore allows at most 20 levels of nesting, and content trees go deeper, so a
tree is stored as an ordered array of nodes that each point to their parent by index:

```json
"content": [
  { "type": "section",  "parent": -1 },
  { "type": "heading",  "parent": 0, "level": 3 },
  { "type": "icon",     "parent": 1, "icon": "ti-pencil" },
  { "type": "text",     "parent": 1, "value": "Create, read, update" },
  { "type": "codeBlock","parent": 0, "lang": "py", "label": "Python", "value": "ages = {…}" }
]
```

`unflatten()` in `schema/content.ts` rebuilds the tree (order = document order).

## Documents

| Path | Contents |
|---|---|
| `meta/content` | `version` (hash of all content), counts, `generatedAt` |
| `catalog/current` | Subjects with topic outlines — navigation, search, progress totals |
| `subjects/{subjectId}` | Title, description, icon, category, kind, counts |
| `subjects/{subjectId}/topics/{topicId}` | `title`, `group`, `order`, `content` (flat) |
| `subjects/sheet-150/problems/{problemId}` | Problem metadata, `statement` / `io` / … (flat content), `naive` & `optimal` (`content`, `code` per language, `complexity`), `similar` |

Content is public and read-only (`firestore.rules`); only the seeder (admin SDK) writes it.

## How the app loads content

`src/features/catalog/source.ts`:

1. Everything fetched from Firestore is stored on the device (IndexedDB).
2. Once per session the app reads `meta/content` (one tiny document). If the version changed, the
   device cache is cleared and content is fetched fresh.
3. A repeat visit costs **one** read; offline, cached content keeps working.

## Local development

```bash
npm run emulators       # Auth + Firestore + Functions (Java 21 needed: brew install openjdk@21)
npm run content:seed    # fill the local Firestore
npm run dev:local       # app on http://localhost:9091 against the emulators
```

Emulator data (seeded content, test accounts) is kept in `.emulator-data/` between restarts.

## Release checklist (live project)

Everything here is free on Firebase's Spark plan (no gcloud or paid tools needed).

1. Get admin credentials for seeding — a **service account key**: Firebase console → Project settings →
   Service accounts → *Generate new private key*. Save it as `service-account.json` in the project
   folder (git-ignored; never commit or share it).
2. `npm run deploy:rules` — security rules + indexes (content becomes publicly readable).
3. `GOOGLE_APPLICATION_CREDENTIALS=./service-account.json npm run content:seed:live` — type the project id to confirm.
4. `npm run deploy:hosting`.

(Alternative to step 1 if you use the free gcloud CLI: `gcloud auth application-default login` with the
project owner's account, then run step 3 without the variable.)

Cloud Functions (`functions/`) are optional and need the pay-as-you-go Blaze plan; the app works without them.
