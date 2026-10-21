# Infrastructure for the launch: one-time setup

Each step needs the owner's sign-in (Google, AWS, GitHub or GoDaddy), so none of it has been done yet. The AWS side
(accounts, Terraform, backups, alarms) is lvn-backend's: `docs/runbooks/aws-deployment.md`, ADR-0035 and ADR-0089.
This page covers what the web launch adds. The old app's own setup is in its `docs/runbooks/infra.md` on
`release/college-launch`; sections 1, 5 and 6 here are shared with it.

## 1. The test Firebase project

The sandbox signs in with Google through its own Firebase project, never production's. `next build` refuses a sandbox
build with the production project id (`config/firebase-projects.json`).

1. Firebase console → Add project → `learnvianotes-test`.
   - If that id is taken, Firebase adds a suffix. Put the real id in `config/firebase-projects.json` → `test`.
2. Add a web app. Its config goes into the sandbox's `infra/terraform/envs/sandbox/.env` (`NEXT_PUBLIC_FIREBASE_*`,
   and `TF_VAR_firebase_project_id` for the API), which is also the `LVN_DEPLOY_ENV` secret (§4).
3. Authentication → Sign-in method: enable Google only (the launch shows email and Google; email accounts are the
   API's own).
4. Authentication → Settings → Authorized domains: add the sandbox's CloudFront host.

The project can stay on the free Spark plan: only Authentication is used (ADR-0007).

## 2. Production's Firebase project

`config/firebase-projects.json` names `learnvianotes-2e2d7`, the old site's project, so returning Google users keep
their accounts (ADR-0007). Confirm this before launch (see [launch.md](../launch.md)).

- Add `www.learnvianotes.in` to its Authorized domains, if it isn't there already.
- Its web config goes into production's `.env` and the `production` environment's `LVN_DEPLOY_ENV` secret.
- A production build accepts no other project, and no other build accepts this one.

## 3. Google Analytics (optional, ADR-0092)

Leave `NEXT_PUBLIC_GA_MEASUREMENT_ID` empty and there is no analytics, no banner and no footer control. To use it:

1. Create a GA4 property and a web data stream for `www.learnvianotes.in`; copy its measurement id (`G-…`) into
   production's `.env`. Give the sandbox its own property, or none.
2. In GA4 → Admin, set:
   - **Data retention:** 2 months. This must match `config/legal.ts` → `RETENTION.analyticsMonths`.
   - **Google signals:** off.
   - **Ads personalisation:** off.
   - **Enhanced measurement:** off for site search and form interactions. Page views are sent by the app, path only.
3. Check on the sandbox: the banner asks, nothing loads before "Allow", and "Analytics choice" in the footer asks
   again.

## 4. Deploy credentials

The lvn-web repository needs two GitHub **environments**, `sandbox` and `production` (Settings → Environments). Give
`production` a required reviewer, and limit each environment's deployment branches and tags:

- `sandbox`: `release/**`;
- `production`: tags `v*`.

Each environment needs:

| Kind | Name | Value |
| --- | --- | --- |
| secret | `LVN_DEPLOY_ENV` | the whole `infra/terraform/envs/<env>/.env` of lvn-backend (any `AWS_PROFILE` line is dropped) |
| variable | `AWS_DEPLOY_ROLE_ARN` | an IAM role in that environment's AWS account that trusts GitHub's OIDC provider for `repo:learnvianotes/lvn-web:environment:<env>` |
| variable | `AWS_REGION` | `ap-south-1` |

The repository also needs the secret `LVN_BACKEND_READ_TOKEN`: a fine-grained token with read access to
`learnvianotes/lvn-backend`, the same one CI's contract job uses. Optionally, the variable `LVN_BACKEND_REF` sets the
lvn-backend branch the sandbox deploys with (default `main`).

The OIDC role:

- [GitHub's guide](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
  covers the identity provider and the trust policy.
- *(Unverified)* Which permissions are enough for `deploy.sh`: ECR push, ECS, SSM parameters, the Terraform state
  bucket, and whatever the Terraform modules manage. Start from the administrator role the AWS runbook uses for
  `deploy.sh`, and narrow it once the first deploys pass.

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

*(Unverified)* Zoho's free-plan limits, and whether forwarding services include SMTP on their free tier. If the API's
own mail (SES) is set up for the domain first, merge its SPF include into the same record.

## 6. Uptime alerts

Use lvn-backend's monitoring (ADR-0089: Grafana alerting, `ALERT_EMAIL`, still waiting on the owner). It needs checks
on `https://www.learnvianotes.in/` and `/robots.txt`. The second one catches a broken deploy that still serves a cached
page.
