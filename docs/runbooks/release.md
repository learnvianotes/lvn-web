# Releasing

The sandbox (the test site) changes only when a `release/**` branch of lvn-web is pushed. Production (the live site)
changes only when a `v*` tag is pushed. Both go through `.github/workflows/deploy.yml`, which runs lvn-backend's
`infra/scripts/deploy.sh` (lvn-backend ADR-0093). CI (`ci.yml`) checks every push.

| Push | Deploys to | lvn-backend checked out at | Web build | GitHub environment |
| --- | --- | --- | --- | --- |
| an lvn-web `release/**` branch | sandbox | `vars.LVN_BACKEND_REF` (default `main`) | `NEXT_PUBLIC_APP_ENV=sandbox`: noindex, robots `Disallow: /`, the test Firebase project | `sandbox` |
| a `v*` tag, e.g. `v1.0.0` | production | the same tag | `NEXT_PUBLIC_APP_ENV=production`: launch checks, sitemap, the production Firebase project | `production` |

`deploy.sh` refuses anything else:

- production unless **both** repositories' HEADs carry a `v*` tag;
- the sandbox unless lvn-web is on a `release/**` branch (or a `v*` tag).

The local environment (`deploy-local.sh`) is not affected.

Each deploy:

1. runs lint, type-check and unit tests;
2. applies Terraform;
3. builds and pushes the API and web images (the web build runs the launch checks);
4. runs the migrations;
5. rolls the services.

## Before the first production release

- `config/legal.ts` → `LEGAL` is filled in. Until it is, `next build` stops with a launch-check error, so a tag can't
  deploy. CI's "launch readiness" job shows the same error on every push.
- `config/legal.ts` → `RETENTION` matches reality: the backup schedule, log retention and Google Analytics → Admin →
  Data retention.
- `TERMS_VERSION` is bumped in both repositories once the legal text is final ([launch.md](../launch.md)).
- The GitHub environments exist ([infra.md §4](infra.md#4-deploy-credentials)). Give `production` a required reviewer,
  so a pushed tag also waits for one click.
- lvn-backend has `infra/terraform/envs/production` (only `sandbox` and `local` exist today).

## Releasing

1. Cut the release branch from `main` in lvn-web and push it. The sandbox follows:
   ```bash
   git switch -c release/2026-11 main && git push -u origin release/2026-11
   ```
   Fixes found on the sandbox go on this branch, then back into `main`.
2. Check the sandbox: the landing page, a subject, sign-up with an adult date of birth, `/legal/grievance`,
   `/robots.txt` (`Disallow: /`), and that `/no-such-page` answers 404.
3. Tag the release commit in **both** repositories with the same tag, lvn-backend first:
   ```bash
   git -C lvn-backend tag -a v1.0.0 -m "v1.0.0" && git -C lvn-backend push origin v1.0.0
   git -C lvn-web tag -a v1.0.0 -m "v1.0.0: College/Interview track" && git -C lvn-web push origin v1.0.0
   ```
4. Approve the `production` deployment, watch the run, then check the live site:
   - the landing page, a subject, `/legal/privacy`, `/robots.txt` and `/sitemap.xml`;
   - `curl -sI https://www.learnvianotes.in/no-such-page` answers 404.

## Rolling back

lvn-backend `docs/runbooks/roll-back.md` (images are tagged by commit). Then fix
forward: revert on the release branch, check the sandbox, and tag the next patch version.

## Manual fallback

When CI is down, from a machine with the AWS profile and lvn-web checked out at the tag or release branch:

```bash
LVN_WEB_DIR=<lvn-web> lvn-backend/infra/scripts/deploy.sh production   # or sandbox
```

The same release-ref rules and launch checks apply.
