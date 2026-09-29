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

## Sign-in on your own domain (mobile reliability)

When a phone blocks the Google popup, the app falls back to a full-page redirect. With the default
`authDomain` (`<project>.firebaseapp.com`) that redirect hands the result back through a third-party
site, which Safari and newer Chrome/Firefox block — the user returns signed out.

So on the domains listed in `SAME_SITE_AUTH_DOMAINS` (`src/config.ts`) the app uses the site's own
domain as `authDomain` (Firebase Hosting serves `/__/auth/handler` on every connected domain).
Each of those domains must be allowed as a redirect target of the Google OAuth client:

1. [Google Cloud Console → APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials?project=learnvianotes-2e2d7)
   → OAuth 2.0 Client IDs → the client **Firebase's Google provider uses** — its id is shown in
   Firebase console → Authentication → Sign-in method → Google → *Web SDK configuration*
   (for this project: `761935379919-92vi63rnkfrq5vqi5jphehsg2sd4jg7b…`). Editing any other client has no effect.
2. **Authorized JavaScript origins** — add `https://www.learnvianotes.in` and `https://learnvianote.web.app`.
3. **Authorized redirect URIs** — add `https://www.learnvianotes.in/__/auth/handler` and
   `https://learnvianote.web.app/__/auth/handler`. Save (changes can take a few minutes).
4. Put the domains into `SAME_SITE_AUTH_DOMAINS` in `src/config.ts` and deploy.

Adding a new custom domain later: add it to `SAME_SITE_AUTH_DOMAINS`, to Firebase → Authentication →
Authorized domains, and to the OAuth client as above.
