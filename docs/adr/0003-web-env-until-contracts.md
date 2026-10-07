# ADR-0003: Validate web environment locally until @lvn/contracts/config ships

- Status: Accepted
- Date: 2026-10-08
- Spec sections: §2 (Validation), §16.1

## Context

§16.1 requires every app to read configuration through `@lvn/contracts/config`. That package is published by
lvn-backend, which does not exist yet. lvn-web already needs two variables (`NEXT_PUBLIC_APP_ENV`,
`NEXT_PUBLIC_SITE_URL`).

## Decision

`lib/env.ts` validates the web variables with Zod and fails the build on bad values, matching what
`@lvn/contracts/config` will do. When the package is published, `lib/env.ts` re-exports from it and the local
schema is deleted in the same PR.

## Consequences

One small temporary duplicate. No other contract types (domain enums, validation, GraphQL) are hand-written in
lvn-web; those wait for the package.
