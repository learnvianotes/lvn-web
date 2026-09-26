# LearnViaNotes

A quick, focused interview sheet: 13 subjects of notes plus 150 coding problems with solutions in
Python, C++, Java and JavaScript. Nothing is required: no sign-up, no login, no server. Just learn.

Subjects: DSA Basics · DSA Advanced · Sheet 150 · OOPs · Computer Networks · DBMS · Operating Systems ·
Cryptography · System Design · Git & GitHub · API Design · GenAI Fluency · Machine Learning & AI

- **Static site.** All content is JSON in `public/content`, served with the app.
- **Progress stays on the device.** Solved/revisit status, completed topics and the study streak live in
  the browser's `localStorage`.
- **Installable (PWA).** Works offline for anything already opened.
- **Help center** (speech-bubble "?" icon in the header): feedback with an automatic screenshot goes straight to a Google Sheet (see below).

## Development

```bash
npm install
npm run dev              # http://localhost:9090
npm run build            # production build in dist/
npx vite preview         # serve dist/ locally (service worker active)
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
public/content/                generated JSON (don't edit by hand)
```

- Topic HTML is normalized into one small style vocabulary (`scripts/content/sanitize.mjs` →
  `src/styles/prose.css`), so every subject looks the same in light and dark mode.
- Code is validated on every extract. C++ is compiled with `clang++`, and Java and JavaScript are
  syntax-checked; anything that fails is rejected and listed in the output.
- `node scripts/content/check-code.mjs <lc-id …>` checks the solution files for specific problems.
- `JAVAC=/path/to/javac node scripts/content/compile-java.mjs` fully compiles every Java snippet (needs a JDK).

## Optional: Firestore

The content can also be served from Firestore instead of static JSON. This is only worth doing if you
need it; see `scripts/content/seed-firestore.mjs`, `firestore.rules`, and `VITE_CONTENT_SOURCE` in
`.env.example`.
