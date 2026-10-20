# Releasing

The live site (www.learnvianotes.in, Firebase project `learnvianotes-2e2d7`) changes only when a `v*` tag is
pushed. The test site (Firebase project `learnvianotes-test`) follows every push to a `release/**` branch. Both
run through `.github/workflows/deploy.yml`.

| Push | Deploys to | Builds with | Firebase alias | GitHub environment |
| --- | --- | --- | --- | --- |
| a `release/**` branch | test site | `npm run build:test` (noindex, robots `Disallow: /`) | `test` | `test` |
| a `v*` tag, e.g. `v1.0.0` | live site | `npm run build` (launch checks, sitemap) | `production` | `production` |

Each deploy runs lint, unit tests and the build, then deploys **the Firestore rules first, then the site**. A new
site may write fields that only the new rules accept: the age check writes `adultConfirmedAt` and
`termsVersion`, which old rules refuse.

## Before the first live release

- `src/config.ts` → `LEGAL` is filled in (operator, address, courts' city, Grievance Officer, mailbox). Until it
  is, `npm run build` stops with a launch-check error, so a tag can't deploy.
- `src/config.ts` → `RETENTION` matches reality: the backup schedule ([infra.md](infra.md#3-daily-backups)) and
  Google Analytics → Admin → Data retention.
- The GitHub environments exist ([infra.md](infra.md#5-deploy-credentials)). Give `production` a required
  reviewer, so a pushed tag also waits for one click.

## Releasing

1. Merge the finished work into the release branch and push it. Check the test site.
2. Tag the commit and push the tag:
   ```bash
   git tag -a v1.0.0 -m "v1.0.0: College / Interview track"
   git push origin v1.0.0
   ```
3. Watch the Deploy run, then check on the live site: the home page, a topic, `/privacy`, `/robots.txt`,
   `/sitemap.xml`, and that `/no-such-page` answers 404 (`curl -sI https://www.learnvianotes.in/no-such-page`).

## Content changes

Pages exist only for the subjects and topics in `content-build/catalog.json`: the build writes one HTML file per
topic, and any other address is a 404. When subjects or topics change:

1. Seed the test project and push to the release branch:
   `SEED_PROJECT=test npm run content:seed:live`.
2. When releasing, seed the live project (`npm run content:seed:live`), then push the tag.
   - If the tag goes out first, new topics answer 404 when opened directly until the seed finishes.
   - If the seed goes out first, new topics answer 404 when opened directly until the site deploys.

   Either way, in-app navigation works throughout.

## Rolling back

- **The site:** Firebase console → Hosting → the site → Release history → the previous release → Roll back.
  This is instant and needs no build.
- **Rules:** Firebase console → Firestore → Rules → History → the previous version → Restore.
- **Then fix forward:** revert on the release branch, check the test site, and tag a new version.

## Manual fallback

From a laptop signed in with `firebase login`, with each project's web config in `.env.production.local` and
`.env.test.local`, when CI is down:

- **Live:** `npm run deploy:rules && npm run deploy:hosting`, rules first.
- **Test:** `npm run deploy:test`, which does both.

The launch checks still apply.
