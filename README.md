# LearnViaNotes

A quick, focused interview sheet: 21 subjects of notes plus 150 coding problems with solutions in
Python, C++, Java and JavaScript. Nothing is required — sign-in is optional and only adds a synced
streak, study history and notes. Just learn.

Subjects: DSA Basics · DSA Advanced · Sheet 150 · OOPs · Computer Networks · DBMS · Operating Systems ·
Cryptography · System Design · Git & GitHub · API Design · Generative AI · Machine Learning · Deep Learning ·
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
npm run build            # production build in dist/
npx vite preview         # serve dist/ locally (service worker active)
npm run emulators        # local Firebase: Auth + Firestore + Functions (needs Java 21)
npm run dev:local        # app on :9091 using the local emulators
```

## Going live

The build output (`dist/`) is a static site, so any static host works. The routes are client-side, so
unknown paths must serve `index.html`. That's already configured for:

| Host | Config | Deploy |
|---|---|---|
| Firebase Hosting | `firebase.json` | `npm run build && npx firebase-tools deploy --only hosting` |
| Netlify | `public/_redirects` | build command `npm run build`, publish directory `dist` |
| Vercel | `vercel.json` | framework "Vite" (defaults work) |

After deploying, open the site on your phone:
- **Android (Chrome):** menu → *Install app* (or the *Install app* link at the bottom of the home page).
- **iPhone (Safari):** Share → *Add to Home Screen*.

## Feedback → Google Sheets

Follow [docs/feedback-google-sheets.md](docs/feedback-google-sheets.md) (about 5 minutes), then paste the
Apps Script URL into `FEEDBACK_URL` in `src/config.ts`.

## Editing content

```
content-src/legacy-html/       original notes and Sheet 150 modules (source)
content-src/code/<problem>/    naive|optimal .py/.cpp/.java/.js: fills in or replaces solution code
        │  npm run content:extract
        ▼
content-build/                 scanned content as JSON (don't edit by hand; not served)
        │  npm run content:seed
        ▼
Firestore                      structured content the app reads
```

- **Python, C, C++, Java, JavaScript, SQL, Data Science and Deep Learning** are authored as code in
  `content-src/authoring/<subject>/` (`npm run content:<subject>`): every example is executed — Python in
  process, C/C++ with clang + sanitizers, Java on JDK 21, JavaScript on Node, SQL on SQLite — and its output
  is checked before the HTML is generated. See [content-src/authoring/README.md](content-src/authoring/README.md).
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
