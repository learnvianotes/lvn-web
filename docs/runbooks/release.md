# Releasing

The web runs on a Lightsail VM per environment, beside lvn-backend's API (lvn-backend ADR-0096). Beta (the test site)
changes only when a `release/**` branch is pushed. Production (the live site) changes only when a `v*` tag is pushed.
Both go through `.github/workflows/deploy.yml`. CI (`ci.yml`) checks every push.

| Push | Deploys to | Web build | GitHub environment |
| --- | --- | --- | --- |
| a `release/**` branch | beta, `https://beta.learnvianotes.in` | `NEXT_PUBLIC_APP_ENV=sandbox`: noindex, robots `Disallow: /`, the test Firebase project | `beta` |
| a `v*` tag, e.g. `v1.0.0` | production, `https://www.learnvianotes.in` | `NEXT_PUBLIC_APP_ENV=production`: launch checks, sitemap, the production Firebase project | `production`, with a required reviewer |

**Production has no VM for now:** its server was deleted on 2026-10-22. A `v*` tag builds the image and then stops at
SSH, before touching anything. Don't push `v*` tags until production is back (lvn-backend `docs/runbooks/lightsail.md`).

Each deploy:

1. runs lint, type-check and unit tests;
2. builds the web image with the environment's `NEXT_PUBLIC_*` values (a production build runs the launch checks) and
   pushes it to GHCR as `lvn-web:<env>-<commit>`;
3. over SSH, points the VM's stack at it (`/opt/lvn/lvn.sh set-image web … && lvn.sh up`): `docker compose pull && up`,
   then waits until every service is healthy and the site answers over HTTPS. Otherwise the job fails;
4. checks `<site>/robots.txt` from outside.

The API, worker, database, Redis and Caddy are lvn-backend's deploy. It must have run once on the VM before the web's
first deploy: the web's deploy refuses until `/opt/lvn/lvn.sh` exists.

## Before the first production release

- `config/legal.ts` → `LEGAL` is filled in. Until it is, `next build` stops with a launch-check error, so a tag can't
  deploy. CI's "launch readiness" job shows the same error on every push.
- `config/legal.ts` → `RETENTION` matches reality: the backup schedule, log retention and Google Analytics → Admin →
  Data retention.
- `TERMS_VERSION` is bumped in both repositories once the legal text is final ([launch.md](../launch.md)).
- Production has a VM again, and the GitHub environments exist in both repositories ([infra.md §4](infra.md#4-deploy-credentials)).

## Releasing

1. Cut the release branch from `main` in **both** repositories and push lvn-backend's first. Beta follows:
   ```bash
   git -C lvn-backend switch -c release/2026-11 main && git -C lvn-backend push -u origin release/2026-11
   git -C lvn-web switch -c release/2026-11 main && git -C lvn-web push -u origin release/2026-11
   ```
   Fixes found on beta go on these branches, then back into `main`.
2. Check beta: the landing page, a subject, sign-up with an adult date of birth (the email arrives),
   `/legal/grievance`, `/robots.txt` (`Disallow: /`), and that `/no-such-page` answers 404.
3. Production, once it has a VM: tag the release commit in **both** repositories with the same tag, lvn-backend first:
   ```bash
   git -C lvn-backend tag -a v1.0.0 -m "v1.0.0" && git -C lvn-backend push origin v1.0.0
   git -C lvn-web tag -a v1.0.0 -m "v1.0.0: College/Interview track" && git -C lvn-web push origin v1.0.0
   ```
4. Approve the `production` deployment of each, watch the runs, then check the live site:
   - the landing page, a subject, `/legal/privacy`, `/robots.txt` and `/sitemap.xml`;
   - `curl -sI https://www.learnvianotes.in/no-such-page` answers 404.

## Rolling back

lvn-backend `docs/runbooks/roll-back.md`: on the VM, `lvn.sh set-image web <the previous image> && lvn.sh up` (the VM
keeps the image before the current one). Then fix forward: revert on the release branch, check beta, and tag the next
patch version.

## Manual fallback

When GitHub Actions is down: build and push the image from a machine logged in to GHCR, with the same build arguments
as the workflow, then on the VM as the deploy user:

```bash
/opt/lvn/lvn.sh set-image web ghcr.io/learnvianotes/lvn-web:<env>-<commit> && /opt/lvn/lvn.sh up
```

The same release rules apply: beta from a release branch, production from a `v*` tag, a production image only with
the launch checks passing.
