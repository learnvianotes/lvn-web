# Launch: College / Interview track (18+), on this app

This branch (`release/college-launch`, cut from `4f2a9275`, the build live on 2026-10-20) is the launch build.
The rewrite (lvn-web `main`) follows later. The School track (5th std+) is a later phase: it needs parent
accounts and School content.

## Status of the 2-day plan

| # | Item | State | Where |
| --- | --- | --- | --- |
| 1 | Legal pages and a named operator | Built; **waiting for the operator's details** | `/privacy`, `/terms`, `/grievance`; `src/config.ts` → `LEGAL` |
| 2 | Refuse under-18s at sign-up | Built | `src/features/auth/age.ts`, `AgeGate.tsx` |
| 3 | GA only with consent | Built | `src/services/analytics.ts`, `consent.ts` |
| 4 | Real 404s, robots.txt, sitemap.xml | Built | `build/site-pages.ts`, `firebase.json` |
| 5 | No purple; SEO | Built (page heads and titles; full pre-rendering not done) | `src/shared/lib/pages.ts` |
| — | CI on every push; production only from a tag | Built; **needs GitHub environments** | `.github/workflows/`, [runbooks/release.md](runbooks/release.md) |
| — | Test project, Blaze and budget, backups and drill, uptime, mailbox | Steps written; **need the owner's sign-in** | [runbooks/infra.md](runbooks/infra.md) |

The production build refuses to run until `LEGAL` is filled in, so nothing can go live with blank legal pages.

## Decisions waiting for the owner

1. The legal operator, the postal address, the city for disputes and the Grievance Officer. The 26 Sep launch post
   came from Thrishank Kuntimaddi; is he the operator, or the Grievance Officer, or both?
2. The mailbox: a Zoho inbox or forwarding to Gmail ([infra.md §6](runbooks/infra.md#6-the-grievance-mailbox)).
   Either way it needs a GoDaddy DNS change.
3. Blaze billing on `learnvianotes-2e2d7`, and creating `learnvianotes-test`.
4. `ALERT_EMAIL`: who gets the uptime alerts.
5. Pre-rendering for SEO: in these 2 days or week 1.
   - Today each page's HTML already has its own title, description, canonical link and share tags.
   - The page body is still drawn by JavaScript, which Google renders.
6. Section 7 calls. What is built now:
   - **How the age question is asked:** the date of birth (day, month, year), with no defaults and no hint of the
     cut-off. A neutral age screen ([FTC COPPA FAQ H.3, D.7](https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions)).
     - The chosen date is shown in words. At the gate, where an answer can delete an account, every answer gets a
       "Is this right?" step.
     - Only the outcome is stored.
     - A refusal is remembered on the device for a day.
     - A single "I am 18 or older" checkbox would be simpler, but the FTC calls it not neutral.
   - **Parent-email waitlist:** not built. It would collect a parent's email from a child, so it needs its own
     notice; it belongs with the School track.
   - **GA:** kept, behind opt-in. To remove it, leave `VITE_FIREBASE_MEASUREMENT_ID` empty in production.
   - **The feedback form:** kept.
     - Reports go to a Google Sheet; the Privacy Policy says so.
     - The screenshot can be removed before sending.
     - Reports are kept 12 months; somebody has to actually clear the sheet.
   - **"Free forever":** still on the sign-in page. The Terms say "free to use" and promise nothing about the
     future. Keep the line, or change it to "Free to use".
   - **Retention:** backups 7 days, feedback 12 months, Google Analytics 2 months (`src/config.ts` → `RETENTION`).
     - The Privacy Policy prints these numbers.
     - The backup schedule and GA's retention setting must match them.

## Legal notes (have a lawyer read the pages)

The pages follow the rules cited below, but they are drafts, not legal advice. Checked 2026-10-20:

- **IT (Intermediary) Rules 2021, rule 3(2), as amended 10 Feb 2026** (G.S.R. 120(E)):
  - publish the Grievance Officer's name and contact details;
  - acknowledge complaints within 24 hours;
  - resolve them within **7 days** (it was 15);
  - act on removal requests within 36 hours.

  The Grievance page commits to these. Rule 3(1)(c), now **every three months**, requires telling users that
  accounts can be suspended and content removed; that is not built. It applies only if LearnViaNotes counts as an
  intermediary, which is unsettled for a site that publishes only its own notes.
  [MeitY consolidated text](https://www.meity.gov.in/static/uploads/2026/02/550681ab908f8afb135b0ad42816a1c9.pdf)
- **SPDI Rules 2011:**
  - rule 4 lists what a privacy policy must contain;
  - rule 5(9) requires a Grievance Officer who answers within a month;
  - passwords are sensitive data.
- **DPDP Act 2023 and Rules 2025** (notified 13 Nov 2025): notice (rule 3), children (s.9), grievances (rule 14,
  ≤ 90 days), breach reporting and the end of IT Act s.43A all apply from **13 May 2027**. A proposal to bring this
  forward to 13 Nov 2026 had not been notified as of 8 Oct 2026; check the Gazette before launch.
  - From then on, rule 8(3) requires keeping personal data, traffic data and logs for at least a year. The Privacy
    Policy's "we may keep a record longer when the law requires it" covers this.
  - The Third Schedule's erasure rule applies only to large platforms.
  - [Rules](https://egazette.gov.in/WriteReadData/2025/267650.pdf),
    [commencement](https://egazette.gov.in/WriteReadData/2025/267647.pdf)
- **Self-declared age:** the UK ICO accepts it only for low-risk processing. Here, under-18s get no account at
  all, and reading needs none.

## Known limits

- **An account that answers under 18 at the gate:** its data is deleted at once.
  - Firebase deletes the sign-in record itself only after a recent sign-in, so on an old session the gate asks for
    the password (or the Google popup) first.
  - If they sign out instead, the record goes the next time the account signs in on that device. Otherwise it stays,
    with no data, until removed from the Firebase console, or by a clean-up function once Blaze is on (not built).
- **A refusal on a shared device:** for a day, no unconfirmed account can get past the gate there; confirmed adults
  are not affected. Nobody's account is deleted unless they answer under 18 themselves.
- **Cloud Functions aren't deployed** (Spark plan). Account deletion still works from the app.
  `npm run deploy:functions` after Blaze adds the server-side clean-up and the trending topics.
- **Pages are generated from `content-build/catalog.json`.** Seed and deploy together
  ([release.md](runbooks/release.md#content-changes)).
