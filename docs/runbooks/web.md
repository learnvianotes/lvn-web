# Web runbook

Platform-wide runbooks (backups, secrets, queues, leakage response) live in lvn-backend `docs/runbooks/`.

- **Roll back the web app:** redeploy the previous image / deployment; the site is fully static except redirects.
- **Content looks wrong on /core:** content comes from `content-build/` at build time. Fix the source in
  `content-src/`, run `pnpm content:<subject>`, review the diff in `content-build/`, rebuild.
- **Releasing, and the launch setup:** [release.md](release.md) and [infra.md](infra.md); status in
  [../launch.md](../launch.md).
