# syntax=docker/dockerfile:1.7
# The web image (lvn-backend spec §16.2): Next's standalone server on :3000. NEXT_PUBLIC_* values are compiled into the
# browser code, so they are build arguments and the image is built per environment (lvn-backend
# docs/runbooks/lightsail.md). Nothing is read from a .env file.
#   docker build -t lvn-web --build-arg NEXT_PUBLIC_APP_ENV=sandbox \
#     --build-arg NEXT_PUBLIC_SITE_URL=https://beta.learnvianotes.in \
#     --build-arg NEXT_PUBLIC_API_URL=https://beta.learnvianotes.in/graphql .
# deploy.yml builds it per environment and pushes it to GHCR (lvn-backend ADR-0096).

# 22.23.4 is the Node.js 22 security release (CVE-2026-111497 Brotli RCE, CVE-2026-105482, CVE-2026-106069).
# A floating 22 tag can still resolve to an older cached build.
ARG NODE_IMAGE=node:22.23.4-bookworm-slim

FROM ${NODE_IMAGE} AS build
ENV PNPM_HOME=/pnpm PATH=/pnpm:$PATH CI=true NEXT_TELEMETRY_DISABLED=1 NEXT_OUTPUT=standalone
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
COPY . .
ARG NEXT_PUBLIC_APP_ENV=development
ARG NEXT_PUBLIC_SITE_URL
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_LIVE_URL=
ARG NEXT_PUBLIC_FEEDBACK_URL=
ARG NEXT_PUBLIC_SENTRY_DSN=
ARG NEXT_PUBLIC_STORAGE_ORIGINS=
ARG NEXT_PUBLIC_GA_MEASUREMENT_ID=
ARG NEXT_PUBLIC_FIREBASE_API_KEY=
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID=
ARG NEXT_PUBLIC_FIREBASE_APP_ID=
ARG NEXT_PUBLIC_GITHUB_CLIENT_ID=
ARG NEXT_PUBLIC_GITHUB_AUTHORIZE_URL=https://github.com/login/oauth/authorize
ARG NEXT_PUBLIC_LINKEDIN_CLIENT_ID=
ARG NEXT_PUBLIC_LINKEDIN_AUTHORIZE_URL=https://www.linkedin.com/oauth/v2/authorization
# /version's commit. Omitted builds say "unknown"; deploy.yml passes the git SHA.
ARG NEXT_PUBLIC_GIT_SHA=unknown
RUN pnpm build

FROM ${NODE_IMAGE}
RUN apt-get update && apt-get install -y --no-install-recommends tini && rm -rf /var/lib/apt/lists/*
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
WORKDIR /app
# The traced server and its node_modules, the static assets it does not trace, and the /core content it reads at run
# time (core-app/server/content.ts).
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/content-build ./content-build
USER node
EXPOSE 3000
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["node", "server.js"]
