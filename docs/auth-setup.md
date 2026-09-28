# Sign-in, streak sync and security setup

Sign-in is optional. Learners who never sign in keep using the app exactly as before
(progress in `localStorage`); they just see a sign-in banner where the streak calendar was.
Signed-in learners get the streak calendar, study history (topic, date, time spent, revisits),
the review queue and personal notes — synced across devices through Firestore.

Everything below happens in the [Firebase console](https://console.firebase.google.com) for the
project in `.firebaserc`. None of it needs code changes.

## 1. Authentication providers

**Build → Authentication → Sign-in method**

| Provider | What to do |
|---|---|
| Email/Password | Enable. (Leave "Email link" off.) |
| Google | Enable, choose a support email. |
| GitHub | Create an OAuth app at GitHub → Settings → Developer settings → OAuth Apps. Paste the **callback URL** shown by Firebase into the GitHub app, then paste the GitHub **Client ID / Secret** into Firebase. |
| LinkedIn | Needs *Identity Platform* (Authentication → Settings → upgrade; free tier covers 50k MAU). Then **Add new provider → OpenID Connect**: name `linkedin` (the id becomes `oidc.linkedin`), issuer `https://www.linkedin.com/oauth`, and the Client ID / Secret from a LinkedIn app that has the *Sign In with LinkedIn using OpenID Connect* product. Add Firebase's callback URL to the LinkedIn app's redirect URLs. |

Only the providers listed in `AUTH_PROVIDERS` (`src/config.ts`) get a button — add `'github'` /
`'linkedin'` there once they're enabled.

**Authentication → Settings**

- **Authorized domains**: add your production domain(s) (`localhost` is there by default). The hosting
  site in `firebase.json` is `learnvianote`, so add **`learnvianote.web.app`** and
  **`learnvianote.firebaseapp.com`** (plus any custom domain) — otherwise Google sign-in fails on the
  live site with `auth/unauthorized-domain`.
- **User account management → Email enumeration protection**: keep **on** (default for new projects).
  The app's messages are already generic, so nobody can probe which emails are registered.
- **Password policy**: require at least 8 characters with letters and numbers (the sign-up form
  enforces the same on the client).
- **User actions**: keep “Create (sign-up)” and “Deletion” enabled — learners can delete their
  own account and data from the account menu.

**Templates**: customize the verification and password-reset emails (sender name, app name).

## 2. Firestore

1. **Build → Firestore Database → Create database** (production mode) if it doesn't exist.
2. Deploy the rules in `firestore.rules`:

   ```bash
   npx firebase-tools deploy --only firestore:rules
   ```

   The rules allow each learner to read and write **only their own** `users/{uid}` documents,
   validate every field and size, and deny everything else.

Data layout:

```
users/{uid}                  { progress: { problems, topics, revisitTopics, studied }, updatedAt }
users/{uid}/days/{YYYY-MM-DD}  { topics: { "subject/topic": { title, subject, sec, visits, last } }, focus, updatedAt }
users/{uid}/notes/{id}       { key, text, updatedAt }
```

## 3. Recommended hardening

- **App Check** (Build → App Check) with reCAPTCHA Enterprise for the web app, then enforce it for
  Firestore and Authentication. This stops scripts from using your API key outside the site.
- In Google Cloud console → APIs & Services → Credentials, **restrict the browser API key** to your
  domains (HTTP referrers).
- Security headers (`nosniff`, `X-Frame-Options: DENY`, HSTS, …) are set in `firebase.json`,
  `vercel.json` and `public/_headers` (Netlify).

## What the app does for privacy

- Passwords never touch our code beyond being handed to Firebase Auth.
- Error messages never reveal whether an email has an account.
- Post-login redirects only accept same-site paths (no open redirects).
- Signing out uploads pending changes and then **wipes the local copy** of progress, history and
  notes, so nothing is left behind on a shared computer. Local data from another account is never
  merged into a different one.
- Deleting the account removes all of the learner's Firestore documents, then the account.
