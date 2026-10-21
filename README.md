# LearnViaNotes

A quick, focused interview sheet: 22 subjects of notes plus 150 coding problems with solutions in
Python, C++, Java and JavaScript. Nothing is required — sign-in is optional and only adds a synced
streak, study history and notes. Just learn.

Subjects: DSA Basics · DSA Advanced · Sheet 150 · OOPs · Computer Networks · DBMS · Operating Systems ·
Cryptography · System Design · Git & GitHub · API Design · Artificial Intelligence · Generative AI · Machine Learning · Deep Learning ·
Data Science · Python · C · C++ · Java · JavaScript · SQL

- **Content from the database.** All subjects live in Firestore as structured content (headings,
  paragraphs, code blocks, callouts, tables, …) and are rendered by reusable components. The site ships no
  content files; what's fetched is cached on the device. See [docs/content-database.md](docs/content-database.md).
- **Progress stays on the device** (`localStorage`) — unless the learner signs in (email, Google,
  GitHub or LinkedIn via Firebase Auth); then progress, the streak, study history (topic, date, time
  spent, revisits) and personal notes sync to their own Firestore documents. Setup and security
  checklist: [docs/auth-setup.md](docs/auth-setup.md).
- **Study tools.** Read-aloud for every topic and problem (Web Speech API, offline), a focus timer
  that counts toward the streak, a spaced-repetition review queue, and a "smart study kit" per topic
  (quick notes, side headings, key terms) generated in the browser from the topic's structure.
- **Installable (PWA).** Works offline for anything already opened.
- **Help center** (speech-bubble "?" icon in the header): feedback with an automatic screenshot goes straight to a Google Sheet (see below).

## Architecture

Feature-based React app + Firebase (Auth, Firestore, Cloud Functions). Folder layout, data flow,
guest vs signed-in features, the event log for recommendations and the roadmap:
[docs/architecture.md](docs/architecture.md).

## Development

```bash
npm install
npm run dev              # http://localhost:9090
npm test                 # unit tests (Vitest)
npm run build:test       # build for the test site (noindex; skips the launch checks)
npm run build            # production build in dist/ — stops until src/config.ts → LEGAL is filled in
npx vite preview         # serve dist/ locally (service worker active)
npm run emulators        # local Firebase: Auth + Firestore + Functions (needs Java 21)
npm run dev:local        # app on :9091 using the local emulators
```

## Going live

Launch status, owner decisions and legal notes: [docs/launch.md](docs/launch.md).

- **Releases:** retired. The launch moved to the rewrite on Lightsail (lvn-web `main`, lvn-backend ADR-0096); this
  branch's Firebase deploy workflow is removed, and the old site changes only by hand
  ([docs/runbooks/release.md](docs/runbooks/release.md#manual-fallback)).
- **One-time setup:** Blaze, the test project, backups, uptime alerts and the mailbox
  ([docs/runbooks/infra.md](docs/runbooks/infra.md)).

The build output (`dist/`) is a static site with one HTML file per real page, generated from
`content-build/catalog.json` by `build/site-pages.ts`. There is no catch-all rewrite, so unknown paths get
`404.html` with a 404 status.

| Host | Config | Deploy |
|---|---|---|
| Firebase Hosting (live) | `firebase.json`, `.firebaserc` (aliases `production`, `test`) | by hand only (the deploy workflow is retired) |
| Netlify | `public/_redirects` (no catch-all) | build command `npm run build`, publish directory `dist` |
| Vercel | `vercel.json` (`cleanUrls`, no catch-all) | framework "Vite" (defaults work) |

After deploying, open the site on your phone:
- **Android (Chrome):** menu → *Install app* (or the *Install app* link at the bottom of the home page).
- **iPhone (Safari):** Share → *Add to Home Screen*.

## Feedback → Google Sheets

Follow [docs/feedback-google-sheets.md](docs/feedback-google-sheets.md) (about 5 minutes), then paste the
Apps Script URL into `FEEDBACK_URL` in `src/config.ts`.

## Editing content

```
content-src/legacy-html/       original notes and Sheet 150 modules (source; generated for authored subjects)
content-src/authoring/<subj>/  subjects written as verified code (npm run content:<subject>)
content-src/code/<problem>/    naive|optimal .py/.cpp/.java/.js: fills in or replaces solution code
        │  npm run content:extract
        ▼
content-build/                 scanned content as JSON (don't edit by hand; not served)
        │  npm run content:seed
        ▼
Firestore                      structured content the app reads
```

- **DSA Basics, DSA Advanced, Python, C, C++, Java, JavaScript, SQL, Artificial Intelligence, Machine Learning, Data Science and Deep Learning** are authored as code in
  `content-src/authoring/<subject>/` (`npm run content:<subject>`): every example is executed — Python in
  process, C/C++ with clang + sanitizers, Java on JDK 21, JavaScript on Node, SQL on SQLite — and its output
  is checked before the HTML is generated. See [content-src/authoring/README.md](content-src/authoring/README.md).
  The two DSA subjects show every algorithm in Python, C++, Java and JavaScript tabs; all four versions run at
  build time and must print the same output ([content-src/authoring/DSA_GUIDE.md](content-src/authoring/DSA_GUIDE.md)).
- Topic HTML is normalized into one small style vocabulary (`scripts/content/sanitize.mjs` →
  `src/styles/prose.css`), so every subject looks the same in light and dark mode.
- Code is validated on every extract. C++ is compiled with `clang++`, and Java and JavaScript are
  syntax-checked; anything that fails is rejected and listed in the output.
- `node scripts/content/check-code.mjs <lc-id …>` checks the solution files for specific problems.
- `JAVAC=/path/to/javac node scripts/content/compile-java.mjs` fully compiles every Java snippet (needs a JDK).

## Local development with the database

```bash
npm run emulators        # Firebase Auth + Firestore + Functions locally (needs Java 21)
npm run content:seed     # put all subjects into the local Firestore (verified)
npm run dev:local        # app on :9091 using the emulators
```

Release steps (live project): [docs/content-database.md](docs/content-database.md#release-checklist-live-project).
