# Launch: the College/Interview track (18+) on the rewrite

The College/Interview track launches on the rewrite (Next.js, with lvn-backend's API). The owner approved the plan on
2026-10-22:

- one Lightsail VM per environment running the Docker Compose stack;
- Cloudflare R2 for files and backups, and Resend for email (lvn-backend ADR-0096).

**Beta comes first:** `https://beta.learnvianotes.in`, on the 2 GB VM `13.204.214.142`.

**Production has no VM for now.** Its server was deleted on 2026-10-22; it comes back as another 2 GB VM with the same
stack. Until then, a `v*` tag builds the images and stops before touching anything.

The old app (`release/college-launch`, Vite + Firebase) is no longer deployed by CI. Its Firebase Hosting workflow is
retired on lvn-web's branch `feat/lightsail-deploy-retire-firebase`, which takes effect once merged into
`release/college-launch`. The live site at www.learnvianotes.in stays on Firebase Hosting until production's DNS moves
to the new VM.

## Status

| Launch item | State | Where |
| --- | --- | --- |
| Privacy, Terms and Grievance pages, operator named in config | Built. All filled in: operator, address, courts (Bengaluru), Grievance Officer (LearnViaNotes Admin) and mailbox | `/legal/privacy`, `/legal/terms`, `/legal/grievance`; `config/legal.ts` → `LEGAL` |
| Grievances resolved within 7 days, removals within 36 h | Built | `features/legal/Grievance.tsx`, Terms §9 |
| Age (whole years) at sign-up, refusing under-18s, every answer confirmed | Built (web, phone, API) | lvn-backend ADR-0091 (`ACCOUNT_MINIMUM_AGE`), ADR-0104; `lib/age.ts`, `components/auth/AgeCheck.tsx` |
| Google Analytics only after consent, synced across tabs | Built; off until `NEXT_PUBLIC_GA_MEASUREMENT_ID` is set | lvn-backend ADR-0092; `lib/consent.ts`, `lib/analytics.ts` |
| Real 404s, robots.txt, sitemap | Built | `app/robots.ts`, `app/sitemap.ts`, `tests/e2e/landing.spec.ts` |
| Brand blue, no purple | Built across web, phone and emails | lvn-backend ADR-0094 |
| Page titles, descriptions, canonical links | Built | each route's metadata; `lib/page-title.ts` |
| Separate Firebase projects for beta and production | Built; **the beta project `learnvianotes-test` is not created yet** | `config/firebase-projects.json`, `lib/launch-checks.ts`, [runbooks/infra.md](runbooks/infra.md) |
| CI on every push; beta from `release/**`, production from `v*` tags | Built: images in GHCR, deployed over SSH to the Lightsail VM, failing unless every service is healthy over HTTPS; **needs the GitHub environments** | `.github/workflows/deploy.yml`; lvn-backend ADR-0096, `docs/runbooks/lightsail.md`; [runbooks/release.md](runbooks/release.md) |
| Uploads off for the launch | Built: every upload control is hidden while the API says uploads are off | lvn-backend ADR-0097; `features/notes/uploads.ts` |
| The old site's subjects, topics and Sheet 150 problems | Built: imported from its Firestore as public notes of the LearnViaNotes account; **not run on beta yet** | lvn-backend ADR-0098, `docs/runbooks/legacy-content.md` |
| Launch copy: Exam Prep "A plan for the day", Study Groups "Learn with peers" | Built | `messages/en.json` → `home.features` |
| Export my data with the age record and activity events | Built | lvn-backend `data-export.service.ts`; Profile → Your data |
| Never delete an account unasked | Built | lvn-backend ADR-0091; deletion stays ADR-0088's request + 14 days |
| Launch, release and infra runbooks | Written | this file, [runbooks/release.md](runbooks/release.md), [runbooks/infra.md](runbooks/infra.md) |

A production build (`NEXT_PUBLIC_APP_ENV=production`) refuses to run until two things hold:

- `LEGAL` is filled in;
- it uses the production Firebase project.

So nothing can go live with blank legal pages or the wrong sign-in project. A beta build (`sandbox`) doesn't need
`LEGAL`, and refuses the production Firebase project.

## On Lightsail

- **What runs on each VM:** api, worker, web (standalone Node), Postgres 16, Redis 7 and Caddy (automatic HTTPS for
  the hosts in `LVN_SITE_HOSTS`). Every service has a memory cap, and the caps fit 2 GB. Not on the VM: ClamAV, the PDF
  engine, Typesense (search runs on Postgres) and monitoring. Budget and measurements: lvn-backend
  `docs/runbooks/lightsail.md`.
- **Deploying:** [runbooks/release.md](runbooks/release.md). lvn-backend deploys the stack, and lvn-web deploys only
  its own image into it. Each deploy fails unless every service is healthy and the site answers over HTTPS.
- **Files** are in R2. The browser may reach only the R2 endpoint's origin (`NEXT_PUBLIC_STORAGE_ORIGINS`, from the
  `LVN_R2_ENDPOINT` variable).
- **Email** goes through Resend (`MAIL_TRANSPORT=resend`). The domain must be verified in Resend first.

## Uploads are off

At launch nobody can upload files (lvn-backend ADR-0097: no room for the virus scanner on a 2 GB VM). The API's
`UPLOADS_ENABLED` is false, `Query.uploadsEnabled` says so, and the web and the phone hide every upload control:

- Upload, Read a PDF and Notes from photos;
- picture, video, audio and file cards, and voice notes;
- note imports;
- group pictures and resource covers from the device;
- verification documents and teaching proof.

Everything else works: notes, cards, code, sharing, groups and search.

**Turning them back on** (lvn-backend ADR-0097):

1. give the scanner room, or point `CLAMAV_URL` at one elsewhere;
2. for PDF conversion, run the PDF engine;
3. set the lvn-backend environment variable `LVN_UPLOADS_ENABLED=true`;
4. check the R2 files bucket's CORS rule allows `PUT` from the site;
5. deploy lvn-backend.

The web needs no change: the controls come back when the API says uploads are on.

## The old site's content

`content:import-legacy` (lvn-backend ADR-0098, `docs/runbooks/legacy-content.md`) reads the old site's Firestore
(`learnvianotes-2e2d7`) with a read-only service account. It writes:

- the 22 subjects and their topics into the catalogue;
- each of the 757 topics and 150 Sheet 150 problems as a public note of the LearnViaNotes account, on its topic.

It is idempotent, has a dry run, and imports no accounts: people sign in again with Google. Old progress and personal
notes are ADR-0023's separate snapshot and claim.

Checked on the local stack with the full content in the Firestore emulator:

- 907 notes and 21,042 cards in about 40 seconds;
- a second run changed nothing;
- `/subjects/dsa-basics/analysis` lists its note.

## Checked on the local stack (2026-10-22)

The real deploy script was run against the Compose stack on this machine:

| Question | Answer |
| --- | --- |
| Does the API boot and serve sign-up without the worker? | **Yes.** With the worker stopped, `signUp` returned a session. |
| Do sign-up, verification or reset emails go through the Redis queue? | **No.** The API sends them itself, through Resend. With the worker stopped, "Confirm your email" and "Reset your password" arrived at once, and no job was queued. Only notification and digest emails go through `comms.email` and need the worker. |
| Can the PDF engine be left out on day one with uploads off? | **Yes.** With uploads off, `createUploadIntent` answers UNAVAILABLE, and nothing reaches the `notes.pdf-parse` queue. |

The worker still has to run for data exports, account deletion, scheduled jobs, search indexing and notification
emails.

## Decisions waiting for the owner

1. **The legal details** (`config/legal.ts`) are filled in (2026-11-03): courts in Bengaluru, Grievance Officer
   LearnViaNotes Admin at support@learnvianotes.in (`lib/site.ts`, also `config/legal.ts`).
   ([infra.md §5](runbooks/infra.md#5-the-grievance-mailbox) is how that mailbox receives mail.)
2. **The terms version** is `2026-11-03`, owner's decision (2026-11-03): the Privacy Policy and Terms changed
   materially (adults only, Google Analytics, the Grievance page), so every account accepts them again. It is the
   newest entry of `PUBLISHED_TERMS_VERSIONS` in lvn-web (`features/legal/documents.ts`). The version people accept
   is the API's (lvn-backend ADR-0103), and a platform admin can switch it on /admin/settings → Legal. They can only
   pick a version that is both on that list and on the API's `terms_published_versions` allowlist (owner default
   (a); the owner may veto it). Keep the allowlist equal to `PUBLISHED_TERMS_VERSIONS`. The admin card names any
   version that is on only one of them.
3. **Which Firebase project is production for the rewrite.**
   - `config/firebase-projects.json` says `learnvianotes-in`: production now uses this new project (owner's decision,
     2026-11-03), not the old site's. Google accounts from the old site's project are not carried over automatically.
   - Development uses `learnvianotes-com`.
   - Beta should use `learnvianotes-test`, still to be created ([infra.md §1](runbooks/infra.md#1-the-test-firebase-project)).
     Until then beta offers email sign-in only.
4. **Google Analytics on the rewrite:** keep it (set `NEXT_PUBLIC_GA_MEASUREMENT_ID` for production) or leave it off.
   §15.2 is amended only for the opt-in case (ADR-0092).
5. **Minors already registered.** No real accounts exist on the rewrite yet. If any account under 18 exists when
   `ACCOUNT_MINIMUM_AGE=18` goes live, it keeps the §15.2 restricted-minor rules; nothing deletes it. Decide whether
   to ask such accounts to leave.
6. **Production's VM:** none until it is brought back. Then repeat the beta setup for `production` (lvn-backend
   `docs/runbooks/lightsail.md`).
7. **When to turn uploads on** (above).
8. **The content import on beta:** a read-only service-account key for `learnvianotes-2e2d7`, and the LearnViaNotes
   account (lvn-backend `docs/runbooks/legacy-content.md`).

## How the age check works

- **What people see.** Sign-up, and the details step after a first Google sign-in, ask the age in whole years
  (lvn-backend ADR-0104) with nothing about the cut-off. There is no date picker.
  - A text box with the phone's number pad. The form refuses an empty answer, anything that is not a whole number
    ("17.5", "18 years") and anything outside 1 to 120 before it sends anything; the API checks the same again and
    its errors land on the same field.
  - Every answer, adult or not, gets "Is this right?" ("You are 17 years old.") before it is sent. No answer stands
    out, and one mistyped number can't refuse or hold anyone (FTC COPPA FAQ H.3, D.7: a neutral age screen).
  - Only `age` is sent. The API still takes the deprecated `dateOfBirth` from phone builds made before ADR-0104.
- **What the API does** (`ACCOUNT_MINIMUM_AGE`, default 18; `0` turns it off):
  - `signUp` refuses a younger date, and nothing is stored;
  - `completeRegistration` erases the unfinished account a Google sign-in had just created, with the same refusal.
- **The device remembers a refusal for a day.**
  - The sign-up forms show "Sorry, you can't create an account" instead, and analytics is set to "don't allow".
  - It deletes nothing and signs nobody out: on the details page it only offers Sign out.
- **What is stored** (ADR-0104, amending ADR-0017): the age given and when, for new accounts. Accounts that gave a
  date of birth before keep it, untouched, and their age comes from it. Otherwise the age now is the age given plus
  the whole years since, which is never more than the real age, so the restricted-minor rules never lift early.
- **Admins** (/admin/users) see each account's age, and the date of birth only where one is stored. They correct the
  age, or the date of birth on an account that has one; the form sends a value only when it changed, because the API
  restarts a declared age's clock on every age it is sent.

## Legal notes (have a lawyer read the pages)

The pages follow the rules below, but they are drafts, not legal advice. These rules were checked on 2026-10-20 for
the old app's launch and apply unchanged.

- **IT (Intermediary) Rules 2021, rule 3(2), as amended 10 Feb 2026** (G.S.R. 120(E)). The Grievance page commits to
  these times:
  - publish the Grievance Officer's name and contact details;
  - acknowledge complaints within 24 hours;
  - resolve them within **7 days**;
  - act on removal requests within 36 hours.

  Rule 3(1)(c), now every three months, requires telling users that accounts can be suspended and content removed.
  The Terms say it; a periodic reminder is not built.
  [MeitY consolidated text](https://www.meity.gov.in/static/uploads/2026/02/550681ab908f8afb135b0ad42816a1c9.pdf)
- **SPDI Rules 2011:**
  - rule 4 lists what a privacy policy must contain;
  - rule 5(9) requires a Grievance Officer;
  - passwords are sensitive data.
- **DPDP Act 2023 and Rules 2025** apply from **13 May 2027**: notice, children (s.9), grievances, breach reporting and
  log retention (rule 8(3)). Check the Gazette before launch for any change of date.
  - [Rules](https://egazette.gov.in/WriteReadData/2025/267650.pdf)
  - [Commencement](https://egazette.gov.in/WriteReadData/2025/267647.pdf)

## Known limits

- **A pending resource's page answers 200** for an unknown id: its submitter sees it in the browser. It is never
  indexed (`noindex`).
- **Signed-in pages answer 200** before the browser sends a signed-out visitor to sign in. They are `noindex` in every
  environment.
- **`/core` (off by default) has no analytics banner.** Turn analytics on there only together with `/core` itself.
- **Imported notes look plainer than the old pages.** Icons, bit diagrams and Gantt charts become text, and one
  inline SVG diagram is left out (lvn-backend ADR-0098).
