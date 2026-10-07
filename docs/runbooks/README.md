# Runbooks

Required before real users (spec §16.5): restore from backup (`restore.md`), rotate secrets, drain a queue, roll back
a release, take a note offline, respond to a leakage report.

## Web today

- **Roll back the web app:** redeploy the previous image / deployment; the site is fully static except redirects.
- **Content looks wrong on /core:** content comes from `content-build/` at build time. Fix the source in
  `content-src/`, run `pnpm content:<subject>`, review the diff in `content-build/`, rebuild.
