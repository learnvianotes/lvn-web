# Launch: the College/Interview track (18+) on the rewrite

The College/Interview track launches first on the old app: lvn-web `release/college-launch`, cut from `4f2a9275`. That
branch holds the launch fixes for the old app (Vite + Firebase); its own `docs/launch.md` covers that launch.

This branch, `feat/college-launch-nextjs`, ports the same fixes to the rewrite (Next.js, with lvn-backend's API), so
the rewrite meets the same bar when it replaces the old app. The ports in lvn-backend and lvn-mobile are on branches of
the same name. Nothing here is deployed.

## Status of the launch fixes on the rewrite

| Launch fix (old app) | On the rewrite | Where |
| --- | --- | --- |
| Privacy, Terms and Grievance pages, operator named in config | Built; **waiting for the operator's details** | `/legal/privacy`, `/legal/terms`, `/legal/grievance`; `config/legal.ts` → `LEGAL` |
| Grievances resolved within 7 days, removals within 36 h | Built | `features/legal/Grievance.tsx`, Terms §9 |
| Date of birth at sign-up, refusing under-18s, every answer confirmed | Built (web, phone, API) | lvn-backend ADR-0091 (`ACCOUNT_MINIMUM_AGE`); `lib/age.ts`, `components/auth/AgeCheck.tsx` |
| Google Analytics only after consent, synced across tabs | Built; off until `NEXT_PUBLIC_GA_MEASUREMENT_ID` is set | lvn-backend ADR-0092; `lib/consent.ts`, `lib/analytics.ts` |
| Real 404s, robots.txt, sitemap | Built (404s were already real) | `app/robots.ts`, `app/sitemap.ts`, `tests/e2e/landing.spec.ts` |
| Purple replaced with the brand blue; green for CS Fundamentals | Built across web, phone and emails | lvn-backend ADR-0094 |
| Page titles, descriptions, canonical links | Built | each route's metadata; `lib/page-title.ts` |
| Separate Firebase test and production projects | Built | `config/firebase-projects.json`, `lib/launch-checks.ts` |
| CI on every push; test deploys from release branches, production from `v*` tags | Built; **needs the GitHub environments and AWS** | `.github/workflows/`, lvn-backend ADR-0093, [runbooks/release.md](runbooks/release.md) |
| Export my data with the age record and activity events | Built (the archive already had them; now it says so) | lvn-backend `data-export.service.ts`; Profile → Your data |
| Never delete an account unasked | Built | lvn-backend ADR-0091; deletion stays ADR-0088's request + 14 days |
| PWA and SEO escaping fixes | SEO: built (a `$` in a title broke the title template here too). PWA: nothing to port (no offline service worker) | `lib/page-title.ts` |
| Patched `@grpc/grpc-js` | Already on `main` (`pnpm.overrides`) | `package.json` |
| Launch, release and infra runbooks | Written | this file, [runbooks/release.md](runbooks/release.md), [runbooks/infra.md](runbooks/infra.md) |

A production build (`NEXT_PUBLIC_APP_ENV=production`) refuses to run until two things hold:

- `LEGAL` is filled in;
- it uses the production Firebase project.

So nothing can go live with blank legal pages or the wrong sign-in project.

## Decisions waiting for the owner

1. **The operator's details:** the legal operator, the postal address, the city for disputes, the Grievance Officer and
   the mailbox (`config/legal.ts`). These are the same as for the old app.
2. **`TERMS_VERSION`.** The Privacy Policy and Terms changed materially: adults only, Google Analytics, the Grievance
   page. Bump `TERMS_VERSION` in lvn-web (`features/legal/documents.ts`) and lvn-backend
   (`contexts/users/src/domain/rules.ts`) together once the text is final, so every account accepts it again. It is
   left at `2026-10-08` while the text is still a draft.
3. **Which Firebase project is production for the rewrite.**
   - `config/firebase-projects.json` says `learnvianotes-2e2d7`: the old site's project, so returning Google users
     keep their Firebase UID (ADR-0007).
   - Development uses `learnvianotes-com`.
   - The sandbox should use `learnvianotes-test`, still to be created ([infra.md §1](runbooks/infra.md#1-the-test-firebase-project)).
4. **Google Analytics on the rewrite:** keep it (set `NEXT_PUBLIC_GA_MEASUREMENT_ID` for production) or leave it off.
   §15.2 is amended only for the opt-in case (ADR-0092).
5. **Minors already registered.** No real accounts exist on the rewrite yet. If any account under 18 exists when
   `ACCOUNT_MINIMUM_AGE=18` goes live, it keeps the §15.2 restricted-minor rules; nothing deletes it. Decide whether
   to ask such accounts to leave.
6. **AWS (deferred):** the sandbox and production accounts, `infra/terraform/envs/production`, and the GitHub
   environments ([release.md](runbooks/release.md)).

## How the age check works

- **What people see.** Sign-up, and the details step after a first Google sign-in, ask the date of birth with nothing
  about the cut-off.
  - The chosen date is shown in words ("14 March 2001").
  - Every answer, adult or not, gets "Is this right?" before it is sent. No answer stands out, and one mis-picked year
    can't refuse or erase anyone (FTC COPPA FAQ H.3, D.7: a neutral age screen).
- **What the API does** (`ACCOUNT_MINIMUM_AGE`, default 18; `0` turns it off):
  - `signUp` refuses a younger date, and nothing is stored;
  - `completeRegistration` erases the unfinished account a Google sign-in had just created, with the same refusal.
- **The device remembers a refusal for a day.**
  - The sign-up forms show "Sorry, you can't create an account" instead, and analytics is set to "don't allow".
  - It deletes nothing and signs nobody out: on the details page it only offers Sign out.
- **The date of birth is stored** with the account, as ADR-0017 says. The old app stored only the outcome; the
  rewrite's restricted-minor rules and the School track need the date.

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
