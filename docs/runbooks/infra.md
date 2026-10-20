# Infrastructure: one-time setup

Each step here needs the owner's Google (or GoDaddy) sign-in, so none of it has been done yet. Run them in
order. Expected running cost is about $0–5 a month: Blaze keeps the free quotas, and backup storage is billed
per GiB.

Sources were checked on 2026-10-20 and are linked inline. Items marked *(unverified)* still need checking.

## 1. Blaze plan and budget alerts (production)

1. Firebase console → `learnvianotes-2e2d7` → Upgrade → Blaze, linked to the owner's billing account.
   - Blaze keeps the Spark free quotas
     ([pricing plans](https://firebase.google.com/docs/projects/billing/firebase-pricing-plans)).
   - It is required for scheduled backups and for Cloud Functions.
2. Google Cloud console → Billing → Budgets & alerts → Create budget:
   - Scope: project `learnvianotes-2e2d7`.
   - Amount: e.g. ₹500 a month.
   - Alerts: at 50%, 90% and 100% of actual spend, plus 100% of forecast; email to billing admins.
3. A budget only **alerts**; it does not stop spending ([budgets](https://cloud.google.com/billing/docs/how-to/budgets)).
   Spend caps exist only for a few products, not Firestore or Hosting
   ([spend caps](https://cloud.google.com/billing/docs/how-to/budgets-spend-caps)).
4. Deploy the Cloud Functions, which have not run on Spark: `npm run deploy:functions`.
   - `cleanupUserData` deletes a deleted account's data server-side.
   - `rollupStudyStats` computes the anonymous topic totals.

## 2. The test project

1. Firebase console → Add project → `learnvianotes-test`.
   - If that id is taken, Firebase adds a suffix. Put the real id in `.firebaserc` (`projects.test` and the
     `targets` key) and its site address in `.env.test`.
2. Add a web app. Its config goes into the GitHub `test` environment (step 5), and locally into `.env.test.local`
   for `npm run deploy:test`.
3. Authentication → Sign-in method: enable Email/Password and Google, as in production.
   - Add `learnvianotes-test.web.app` to Authorized domains.
4. Firestore → Create database, in the same location as production. (Production's location is shown in its
   Firestore console.)
5. Seed it: `SEED_PROJECT=test npm run content:seed:live`. It asks you to type the project id.
6. Deploy it: `npm run deploy:test`, or push a `release/**` branch once step 5 is done.

The test project can stay on Spark unless you want to test backups or functions there.

## 3. Daily backups

Firestore scheduled backups:

- one daily and one weekly schedule per database at most;
- retention up to 14 weeks;
- a restore always creates a **new** database;
- they need Blaze ([backups](https://firebase.google.com/docs/firestore/backups),
  [gcloud](https://cloud.google.com/firestore/native/docs/backups)).

Backup storage costs about a fifth of live data per GiB, and restores are billed per GiB
([pricing](https://cloud.google.com/firestore/pricing)).

```bash
gcloud config set project learnvianotes-2e2d7
gcloud firestore backups schedules create --database='(default)' --recurrence=daily --retention=7d
gcloud firestore backups schedules list --database='(default)'
```

The 7 days must match `RETENTION.backupDays` in `src/config.ts`; the Privacy Policy states that number.

### Restore drill (once, the day after the first backup)

```bash
gcloud firestore backups list --format="table(name,database,state,snapshotTime)"
gcloud firestore databases restore \
  --source-backup=projects/learnvianotes-2e2d7/locations/LOCATION/backups/BACKUP_ID \
  --destination-database=restore-drill
# Compare the number of accounts (users documents) in the live and restored databases.
TOKEN=$(gcloud auth print-access-token)
for db in '(default)' restore-drill; do
  curl -s -X POST -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
    "https://firestore.googleapis.com/v1/projects/learnvianotes-2e2d7/databases/$db/documents:runAggregationQuery" \
    -d '{"structuredAggregationQuery":{"structuredQuery":{"from":[{"collectionId":"users"}]},"aggregations":[{"alias":"n","count":{}}]}}'
done
gcloud firestore databases delete --database=restore-drill   # when the counts match
```

Write down the date, the backup used, both counts and how long the restore took.

## 4. Uptime alerts

Cloud Monitoring → Uptime checks → Create:

- Protocol HTTPS, host `www.learnvianotes.in`, path `/`, every 5 minutes, from at least 3 regions.
- A second check on `/robots.txt` catches a broken deploy that still serves a cached page.
- Alert policy: notify an email channel. `ALERT_EMAIL` is still waiting on the owner.

By default the check alerts when at least two regions fail for a minute
([uptime checks](https://cloud.google.com/monitoring/uptime-checks)). Uptime checks are free up to 1 million runs a
month per project, and alerting on them is not charged ([pricing](https://cloud.google.com/stackdriver/pricing)).

## 5. Deploy credentials

The GitHub repository that holds the release branch needs two **environments**, `test` and `production`:

- Settings → Environments.
- Give `production` a required reviewer.

Each environment needs the variables `VITE_FIREBASE_API_KEY`, `…_AUTH_DOMAIN`, `…_PROJECT_ID`,
`…_STORAGE_BUCKET`, `…_MESSAGING_SENDER_ID`, `…_APP_ID` and `…_MEASUREMENT_ID`, holding its project's web
config. These are public values; production's are what `https://www.learnvianotes.in/__/firebase/init.json`
returns.

**Signing in: Workload Identity Federation (preferred, no long-lived key)**
([google-github-actions/auth](https://github.com/google-github-actions/auth)).

```bash
PROJECT=learnvianotes-2e2d7; REPO=<github-owner>/<repo>
PROJECT_NUMBER=$(gcloud projects describe $PROJECT --format='value(projectNumber)')
gcloud iam service-accounts create github-deploy --project=$PROJECT --display-name="GitHub deploys"
SA=github-deploy@$PROJECT.iam.gserviceaccount.com
for role in roles/firebasehosting.admin roles/firebaserules.admin roles/serviceusage.serviceUsageConsumer; do
  gcloud projects add-iam-policy-binding $PROJECT --member="serviceAccount:$SA" --role=$role
done
gcloud iam workload-identity-pools create github --project=$PROJECT --location=global --display-name=GitHub
gcloud iam workload-identity-pools providers create-oidc github --project=$PROJECT --location=global \
  --workload-identity-pool=github --issuer-uri=https://token.actions.githubusercontent.com \
  --attribute-mapping=google.subject=assertion.sub,attribute.repository=assertion.repository \
  --attribute-condition="assertion.repository=='$REPO'"
gcloud iam service-accounts add-iam-policy-binding $SA --project=$PROJECT --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/$REPO"
```

Then set two environment variables:

- `GCP_WORKLOAD_IDENTITY_PROVIDER` = `projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github/providers/github`
- `GCP_DEPLOY_SERVICE_ACCOUNT` = `$SA`

Repeat for the test project.

*(Unverified)* That the three roles are enough for `firebase deploy --only firestore:rules,hosting`. If a deploy
names a missing permission, add that role.

**Or a key:** leave `GCP_WORKLOAD_IDENTITY_PROVIDER` unset and store the service account's JSON key as the
environment **secret** `FIREBASE_SERVICE_ACCOUNT`. `firebase init hosting:github` can create one for you
([GitHub integration](https://firebase.google.com/docs/hosting/github-integration)).

## 6. The grievance mailbox

`learnvianotes.in` has no MX record today, so mail to it bounces. The Grievance page needs a working address,
e.g. `grievance@learnvianotes.in`; it goes into `src/config.ts` → `LEGAL.email`. DNS is at GoDaddy
(`ns45/ns46.domaincontrol.com`). In either option:

- **Add** records only.
- Keep the A records that point at Firebase Hosting and the `hosting-site=learnvianote` TXT record.
- If an SPF TXT record already exists, merge the new one into it.

| Option | DNS records to add | Replies come from |
| --- | --- | --- |
| Zoho Mail free plan | the verification TXT, MX `mx.zoho.in` / `mx2.zoho.in` / `mx3.zoho.in`, SPF TXT, DKIM TXT (exact values on Zoho's setup page) | `grievance@learnvianotes.in` |
| Forwarding to Gmail (a forwarding service such as ImprovMX) | the service's MX records and SPF TXT | your Gmail, unless you set up “Send mail as” with SMTP |

*(Unverified)* Zoho's free-plan limits, and whether forwarding services include SMTP on their free tier. Check
both before choosing.

## 7. Google Analytics settings

Analytics runs only for visitors who allow it (Settings → Privacy). In GA4 → Admin:

- **Data retention:** 2 months. This must match `RETENTION.analyticsMonths`.
- **Google signals:** off.
- **Ads personalisation:** off.

To drop Google Analytics entirely, leave `VITE_FIREBASE_MEASUREMENT_ID` empty in the production environment.
The banner and the Settings control then disappear.
