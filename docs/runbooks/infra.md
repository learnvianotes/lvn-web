# Infrastructure for the launch: one-time setup

Each step needs the owner's sign-in (Google, Cloudflare, GitHub or GoDaddy). The servers are lvn-backend's
`docs/runbooks/lightsail.md` (ADR-0096): the Lightsail VMs, DNS, the R2 buckets and keys, the Resend domain, the GitHub
environments and every secret. This page covers what the web adds. The old app's own setup is in its
`docs/runbooks/infra.md` on `release/college-launch`; sections 1 and 5 here are shared with it.

## 1. The test Firebase project

Beta signs in with Google through its own Firebase project, never production's. `next build` refuses a beta
(`sandbox`) build with the production project id (`config/firebase-projects.json`). Until the project exists, leave
its variables empty: beta then offers email sign-in only.

1. Firebase console → Add project → `learnvianotes-test`.
   - If that id is taken, Firebase adds a suffix. Put the real id in `config/firebase-projects.json` → `test`.
2. Add a web app. Its config goes into the `beta` environment's variables: `NEXT_PUBLIC_FIREBASE_API_KEY`,
   `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, `NEXT_PUBLIC_FIREBASE_PROJECT_ID` and `NEXT_PUBLIC_FIREBASE_APP_ID` in lvn-web,
   and `LVN_FIREBASE_PROJECT_ID` in lvn-backend (§4).
3. Authentication → Sign-in method: enable Google only (the launch shows email and Google; email accounts are the
   API's own).
4. Authentication → Settings → Authorized domains: add `beta.learnvianotes.in` (and `localhost` for local sign-in).
5. Google Cloud Console → APIs & Services → Credentials → the OAuth **web** client Firebase created for this
   project (do not copy its client id into the repo). On that client:
   - Authorized JavaScript origins: `https://beta.learnvianotes.in` and `http://localhost:3000`.
   - Authorized redirect URIs: keep `https://<project-id>.firebaseapp.com/__/auth/handler` and add
     `https://beta.learnvianotes.in/__/auth/handler`.
   The site serves Firebase's helper at `/__/auth` on its own host (`NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` stays
   `<project-id>.firebaseapp.com`, the proxy's upstream). Without that redirect URI, Google refuses the sign-in
   with `redirect_uri_mismatch`. Without the JavaScript origin, a Google Identity Services popup fails with
   `origin_mismatch`.
6. If the OAuth consent screen is in Testing, only listed test users can finish. Publish it, or add each Google
   account as a test user.
7. lvn-backend's `LVN_FIREBASE_PROJECT_ID` for beta is this same project. A mismatch makes every Google token fail
   verification (`Google sign-in could not be verified`).

The project can stay on the free Spark plan: only Authentication is used (ADR-0007).

## 2. Production's Firebase project

`config/firebase-projects.json` names `learnvianotes-2e2d7`, the old site's project, so returning Google users keep
their accounts (ADR-0007). Confirm this before launch (see [launch.md](../launch.md)).

- Add `www.learnvianotes.in` to its Authorized domains, if it isn't there already.
- On its OAuth web client, add JavaScript origin `https://www.learnvianotes.in` and redirect URI
  `https://www.learnvianotes.in/__/auth/handler`, and keep the existing `firebaseapp.com` handler (same as §1).
- Its web config goes into the `production` environment's variables, as in §1.
  `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` stays `<project-id>.firebaseapp.com`.
- A production build accepts no other project, and no other build accepts this one.

## 3. Google Analytics (optional, ADR-0092)

Leave `NEXT_PUBLIC_GA_MEASUREMENT_ID` empty and there is no analytics, no banner and no footer control. To use it:

1. Create a GA4 property and a web data stream for `www.learnvianotes.in`; copy its measurement id (`G-…`) into the
   `production` environment's variable `NEXT_PUBLIC_GA_MEASUREMENT_ID`. Give beta its own property, or none.
2. In GA4 → Admin, set:
   - **Data retention:** 2 months. This must match `config/legal.ts` → `RETENTION.analyticsMonths`.
   - **Google signals:** off.
   - **Ads personalisation:** off.
   - **Enhanced measurement:** off for site search and form interactions. Page views are sent by the app, path only.
3. Check on beta: the banner asks, nothing loads before "Allow", and "Analytics choice" in the footer asks
   again.

## 4. Deploy credentials

The lvn-web repository needs two GitHub **environments**, `beta` and `production` (Settings → Environments). Give
`production` a required reviewer, and limit each environment's deployment branches and tags:

- `beta`: `release/**`;
- `production`: tags `v*`.

Each environment needs (names only; lvn-backend's `docs/runbooks/lightsail.md` says where each value comes from):

| Kind | Name | Value |
| --- | --- | --- |
| secret | `LVN_DEPLOY_SSH_KEY` | the VM's `deploy` user's private SSH key |
| secret | `LVN_DEPLOY_HOST` | the VM's address (beta: `13.204.214.142`; production: none yet) |
| secret | `LVN_SSH_KNOWN_HOSTS` | the VM's SSH host key line(s) |
| secret | `LVN_GHCR_TOKEN` | a token that can read the GHCR images, for the VM's `docker login` |
| variable | `LVN_GHCR_USER` | that token's account |
| variable | `LVN_PUBLIC_URL` | `https://beta.learnvianotes.in` (production: `https://www.learnvianotes.in`) |
| variable | `LVN_APP_ENV` | `sandbox` for beta, `production` for production |
| variable | `LVN_R2_ENDPOINT` | `https://<account id>.r2.cloudflarestorage.com`: becomes `NEXT_PUBLIC_STORAGE_ORIGINS` |
| variable, optional | `NEXT_PUBLIC_FIREBASE_API_KEY`, `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN`, `NEXT_PUBLIC_FIREBASE_PROJECT_ID`, `NEXT_PUBLIC_FIREBASE_APP_ID` | §1 and §2; empty hides Google sign-in |
| variable, optional | `NEXT_PUBLIC_GA_MEASUREMENT_ID` | §3 |
| variable, optional | `NEXT_PUBLIC_SENTRY_DSN` | browser error reports |

The images are pushed with the workflow's own `GITHUB_TOKEN`; no registry secret is needed for that. The repository
secret `LVN_BACKEND_READ_TOKEN` (read access to `learnvianotes/lvn-backend`) is for CI's contract check only.

## 5. The grievance mailbox

`learnvianotes.in` has no MX record today, so mail to it bounces. The Grievance page needs a working address, e.g.
`grievance@learnvianotes.in`; it goes into `config/legal.ts` → `LEGAL.email`.

DNS is at GoDaddy. In either option:

- **add** records only;
- keep the records the site already needs;
- if an SPF TXT record already exists, merge the new one into it.

| Option | DNS records to add | Replies come from |
| --- | --- | --- |
| Zoho Mail free plan | the verification TXT, MX `mx.zoho.in` / `mx2.zoho.in` / `mx3.zoho.in`, SPF TXT, DKIM TXT (exact values on Zoho's setup page) | `grievance@learnvianotes.in` |
| Forwarding to Gmail (a forwarding service such as ImprovMX) | the service's MX records and SPF TXT | your Gmail, unless you set up “Send mail as” with SMTP |

*(Unverified)* Zoho's free-plan limits, and whether forwarding services include SMTP on their free tier. The API's own
mail goes through Resend (lvn-backend ADR-0096). Its records (DKIM, and SPF and MX on a sending subdomain; the exact
values are on Resend's Domains page) sit beside these. If one of them would touch the root SPF record, merge it in.

## 6. Uptime alerts

The Lightsail VMs run no monitoring stack: there is no room in 2 GB (lvn-backend ADR-0096). Until the owner picks a
service (Grafana Cloud, or an uptime checker), watch these from outside, emailing `ALERT_EMAIL`:

- `https://beta.learnvianotes.in/health/ready`, and production's once it is back;
- `/robots.txt` on each, which catches a broken web deploy that still serves a cached page.
