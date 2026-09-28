# Architecture

LearnViaNotes is a **static React app + Firebase**. Content is plain JSON on a CDN; everything
personal (streak, history, notes, preferences, activity events) belongs to a signed-in learner and
lives in Firestore behind strict per-user rules. A small Cloud Functions backend does server-side
work (cleanup, aggregates) that doesn't belong in the browser.

```
                ┌──────────────────────────── Browser (React 19 + Vite, PWA) ───────────────────────────┐
                │  app/        shell, routes (lazy-loaded pages)                                        │
                │  features/   auth · catalog · home · study · progress · voice · focus · help · search │
                │              telemetry  ← each feature owns its components, state, styles              │
                │  services/   firebase app · storage · analytics · userdata repository (interface)     │
                │  shared/     ui, lib (theme, dates, highlight), global styles                         │
                └──────────────┬──────────────────────────────┬─────────────────────────────────────────┘
                               │ static JSON (CDN)            │ Firebase SDKs (lazy)
                     public/content/*.json          ┌─────────┴──────────┬────────────────────┐
                     (built by scripts/content)     │ Firebase Auth      │ Firestore          │
                                                    │ email, Google,     │ users/{uid}/…      │
                                                    │ GitHub, LinkedIn   │ topicStats, trending│
                                                    └────────────────────┴─────────┬──────────┘
                                                                                   │ triggers / schedule
                                                                        functions/ (Cloud Functions)
                                                                        cleanupUserData · rollupStudyStats
```

## Folders

| Path | What lives there |
|---|---|
| `src/app/` | `App.tsx` (routes, lazy pages), `shell/` (header, layout state, footer) |
| `src/features/<name>/` | One folder per feature: components, hooks, stores and its own `.css` |
| `src/services/` | Integrations with no UI: Firebase app/Firestore, `storage` (localStorage), `analytics`, `userdata/` repository |
| `src/shared/` | Reusable UI (`Status`), helpers (`theme`, `date`, `highlight`, `install`) and global styles |
| `schema/firestore.ts` | **Single source of truth** for every stored document — used by the app (`@schema/…`) and copied into the backend at build time |
| `functions/` | Cloud Functions (TypeScript, Node 22) |
| `scripts/content/` | Content pipeline: legacy HTML → `public/content/*.json` |

Rules of thumb as the app grows:
- A feature imports from `services/`, `shared/` and other features' public modules — never the other way round.
- Nothing outside `services/userdata/` talks to Firestore for learner data. It goes through the
  `UserDataRepository` interface (`fetchAll`, `commit`, `appendEvents`, `deleteAll`, `trending`).
- New document shapes are added to `schema/firestore.ts` **and** `firestore.rules` in the same change.

## Guest vs signed-in

| | Guest | Signed in |
|---|---|---|
| Notes, problems, search, filters, problem of the day, explore upcoming courses | ✔ | ✔ |
| Progress, streak calendar, history, review queue | sign-in banner | ✔ |
| Read-aloud, smart study kit, focus timer, personal notes | — | ✔ |
| Sort & rearrange subjects, "Notify me" on upcoming courses, settings (except theme) | — | ✔ |
| Activity tracking | nothing recorded | ✔ (batched) |

## Data flow for a learner

1. Local-first stores (`features/progress/*`) update instantly and persist to `localStorage`.
2. `progress/sync.ts` uploads changes ~2 s later (and on tab hide / reconnect) through the repository,
   pulls other devices' changes when the tab regains focus, and wipes the device copy on sign-out.
3. `telemetry/track.ts` queues activity events and writes them **one document per batch**
   (`users/{uid}/events`), every 30 s or 50 events — a handful of writes per session.

## Performance

- Every page except Home is its own chunk (`React.lazy`), prefetched when the browser is idle.
- Vendor code is split into long-cached chunks (`vendor-react`, `vendor-firebase`).
- Firebase Auth loads after first paint; Firestore (~120 KB) only after someone signs in.
- Feature CSS ships with its feature's chunk.
- Content is static JSON, cached by the service worker (stale-while-revalidate).

## Logs & metrics → recommendations

The event log is designed as the raw input for a recommendation system:

| Event | Fields |
|---|---|
| `topic_view` / `topic_time` / `topic_complete` / `topic_revisit` | subject `s`, topic `k`, seconds `v` |
| `problem_status` | problem `i`, status `l` |
| `search` | query `l`, result `i`, result count `v` |
| `listen`, `kit_open`, `note_save`, `focus_complete` | feature usage |
| `subject_filter`, `subject_sort`, `course_interest` | what learners want |

`rollupStudyStats` (daily) turns these into `topicStats/*` (views, time, completions, unique learners,
last 30 days) and `trending/current` (shown on the signed-in home page).

## Where this goes next

**Now → ~10k learners: stay on Firebase.** It covers auth, database, hosting and functions with no
servers to run, and the free tier absorbs early traffic. Do next:
1. Enable Authentication + Firestore (see `docs/auth-setup.md`), deploy rules.
2. Move to the Blaze plan and deploy `functions/` (cleanup + daily aggregates).
3. Turn on **App Check** so only the real site can use the API key.
4. Install the **"Stream Firestore to BigQuery"** extension on the `events` collection group —
   analytics and model training then run in BigQuery, not in the app.

**Recommendations (v1 → v2).**
- v1 (no ML): "continue where you left off", spaced-repetition review queue (already built),
  trending topics, "learners who finished X next studied Y" (co-occurrence counts computed in the
  daily rollup), next step of the learner's path.
- v2: train a model on the BigQuery event table (e.g. BigQuery ML matrix factorization, or
  embeddings of topics + learner histories), write per-learner suggestions to
  `users/{uid}/recommendations`, read them in the app through the repository.

**If the product outgrows Firebase** (complex relational queries, payments/subscriptions, heavy
server logic, or cost at scale): add an API service (Node/TypeScript on Cloud Run) with Postgres
(Cloud SQL or Supabase) behind it. Because the UI only talks to `UserDataRepository` and the
schema is shared, the move is: implement the repository against the new API, migrate data with a
script, switch — no feature code changes. Keep Firebase Auth (or swap it for the same kind of
provider) and static hosting for content either way.

## Local development

```bash
npm run dev                 # app on :9090 (live Firebase project)
npm run emulators           # local Auth :9099 + Firestore :8080 + Functions :5001, UI on :4000
                            # (Firestore emulator needs Java 21: brew install openjdk@21)
npm run emulators:auth      # Auth only (no Java needed)
npm run dev:local           # app on :9091 against the local emulators
                            # data persists in .emulator-data/ between restarts
npm run functions:build     # compile the backend
npm run deploy:rules        # firestore.rules + indexes
npm run deploy:functions    # Cloud Functions (Blaze plan)
```
