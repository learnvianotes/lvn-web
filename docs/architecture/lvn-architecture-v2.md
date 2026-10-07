# LearnViaNotes — Engineering Architecture Prompt v2

Oct 8, 2026 · @manideep

## 0. How to use this document

This is the single source of truth for the Web, Mobile and Backend agents building LearnViaNotes. Every decision below is pinned; an agent that wants to deviate writes an ADR in `docs/adr/` and gets it accepted before implementing.

Give each agent two things: this whole document, and a one-page role brief (sections 13, 14 or 7–12) telling it which agent it is. Do not paste a different architecture to each agent.

**What changed from v1.** Technology choices are pinned instead of "or equivalent". The domain model, visibility states, forking, versioning and offline conflict rules are defined. A permission matrix replaces the list of permission questions. Admin-platform tenancy, SEO for public notes, push/email delivery, upload hardening, moderation, compliance, AI cost control, backups and schema-change checks are added. Teacher is a role, not a client. "Problems" and "Stories" are removed from scope. Monetization and company recruitment are explicitly out of scope. Three repositories replace the monorepo; the backend is a modular monolith of five bounded contexts (users, notes, core, ai, communication) with a step-by-step extraction playbook to microservices and a per-context Grafana observability stack.

## 1. Product boundaries

LearnViaNotes (LVN) is a student-first learning community: personal and public notes, a block-based editor, groups, classrooms, quizzes, flashcards, exam prep, AI learning tools, learning history, recommendations, search and learning-resource discovery. It is built as one scalable product, not a set of screens.

**Two applications, one backend.**

| Application | Domain | Users | Status |
| --- | --- | --- | --- |
| Student platform (web + mobile) | learnvianotes.com | Student, Teacher, Group Admin (roles) | Build now |
| Admin platform | admin.learnvianotes.com | Platform Admin | Separate app, later |
| college platform | org.learnvianotes.com | College, org admin | seperate app |
| company platform | company.learnvianotes.com | Company | seperate admin app |

Both applications call the **same NestJS GraphQL API and the same PostgreSQL database**. The `Organization` and `Classroom` tables live in the shared schema now; only the admin *UI and admin mutations* are deferred. The student app reads organization and classroom data when a student is a member of them. It never contains organization, college, company or platform-admin registration or dashboards.

**Roles are not clients.** Teacher and Group Admin are roles on a `User`, served by the same web and mobile apps with role-gated routes.

**Explicitly out of scope for this build** (design the schema so they can be added without rewrites, implement nothing):

- Company features: recruitment, mock interviews, hiring challenges, career events
- Payments, subscriptions, ads, marketplace or e-commerce of any kind
- Organization onboarding and administration UI
- Real-time multi-cursor collaborative editing (single-writer notes in v1; see section 4)

**Resource discovery** is a learning-oriented catalogue of books, courses, tools, software and hardware that students search, save, share, recommend and discuss. It carries no cart, checkout or seller accounts.

## 2. Pinned technology decisions

These are decided. Agents use them as-is; changing one requires an accepted ADR.

| Concern | Decision | Why this and not the alternatives |
| --- | --- | --- |
| Repositories | Three repos: lvn-backend, lvn-web, lvn-mobile; lvn-backend publishes @lvn/contracts to GitHub Packages; pnpm + Turborepo inside lvn-backend | Independent release cadences per app; one versioned contract package keeps them in sync |
| Language | TypeScript strict mode everywhere | Shared types across all three apps |
| Backend | `NestJS 10+ modular monolith of five bounded contexts; code-first Apollo Federation 2 subgraphs composed in-process by Apollo Gateway, Apollo Router after extraction; EventBus with in-process and NATS JetStream adapters` | Service-shaped from day one so extraction is a deployment change; one schema for clients either way |
| ORM | Prisma | Typed client, migrations, good Postgres support; fewer footguns than TypeORM |
| Database | PostgreSQL 16 with `pgvector` and `pg_trgm` | One store for data, embeddings and fallback search in v1 |
| Cache / queues | Redis 7; BullMQ for jobs | BullMQ is the standard NestJS queue |
| Object storage | S3 (prod) / MinIO (dev, test); pre-signed URLs | Same API locally and in production |
| Search | PostgreSQL full-text (Phase 2–3) → Typesense (Phase 4) | Avoid a second system until search is a real feature; Typesense is self-hostable and typo-tolerant |
| Vector store | pgvector | Removes a separate vector DB; adequate to millions of chunks |
| Auth | Backend-issued JWT access token (15 min) + opaque rotating refresh token (30 days, stored hashed in Postgres); OAuth via Passport strategies | Standard, revocable, works for web and mobile |
| Auth providers | Email + password, Google, GitHub, LinkedIn | As specified |
| Email | Resend (or SES) via a `MailService` abstraction; React Email templates | Transactional email for verification, reset, notifications |
| Push | Firebase Cloud Messaging (Android, iOS via APNs) | Single provider for both platforms |
| Real-time | GraphQL subscriptions over WebSocket (`graphql-ws`) backed by Redis pub/sub | Notifications, comments, classroom activity |
| AI providers | Backend `AiGateway` with provider adapters (OpenAI, Anthropic, local via Ollama); embeddings `text-embedding-3-small` | Swappable, cost-controlled, never called from clients |
| Transcription | Whisper (API or self-hosted) behind the gateway | Voice notes |
| Web | Next.js 15 App Router, React 19, Tailwind, shadcn/ui, Apollo Client, React Hook Form + Zod, Tiptap editor, Zustand for global state | SSR/ISR for public notes; Tiptap is the most mature block editor |
| Mobile | Expo (SDK 52+) with dev client + EAS Build/Update, Expo Router, React Native Paper or Tamagui, Apollo Client, WatermelonDB (SQLite), expo-secure-store, MMKV for small key-value | Expo gives environments, OTA and native modules without ejecting; WatermelonDB is built for offline sync |
| Validation | Zod schemas in `@lvn/contracts/validation`, used by all three apps | One source for input rules |
| GraphQL codegen | `graphql-codegen` producing typed hooks for web and mobile from the backend schema | Replaces hand-written shared types |
| Testing | Vitest (unit), Testing Library, Playwright (web E2E), Maestro (mobile E2E), Jest + Supertest (backend), Testcontainers (Postgres/Redis/MinIO) | Fast, standard, isolated |
| Observability | OpenTelemetry → Grafana, Loki, Tempo, Prometheus (self-hosted, per-context dashboards); Sentry for errors | OTel-native, one UI, lighter than Elastic/Kibana to operate |
| Infra | Docker Compose (dev), Terraform (sandbox/prod), containers on AWS ECS Fargate or Fly.io, RDS Postgres, ElastiCache, S3 + CloudFront | Managed data stores, cheap compute |
| CI/CD | GitHub Actions per repo; backend publishes @lvn/contracts on tag; client CI fails on an unadopted contracts major | Standard |
| Feature flags | Database-backed flags table with Redis cache, read via GraphQL | No third-party dependency in v1 |

## 3. Repository layout

Three repositories: `lvn-backend`, `lvn-web`, `lvn-mobile`. The backend is a **modular monolith organised as five bounded contexts** — `users`, `notes`, `core`, `ai`, `communication` — each built from day one as if it were already a separate service (own database schema, own GraphQL subgraph, own events, no imports of another context's internals). Extraction to microservices is then a deployment change, not a rewrite (section 6.5). `lvn-backend` publishes `@lvn/contracts` to GitHub Packages; web and mobile pin a version.

Phase 0 starts by inspecting what already exists in each repository and recording, in `docs/architecture/existing-state.md`, what is kept, migrated or deleted. Nothing is rewritten blindly.

```text
lvn-backend/                     NestJS modular monolith → extractable services
  apps/
    api/                         composition root: composes all five subgraphs, serves GraphQL + WebSocket
    worker/                      composition root: runs all contexts' BullMQ processors
  contexts/                      ONE folder per future microservice — the extraction unit
    users/                       auth, sessions, users, roles, PolicyService, organizations (read model)
    notes/                       subjects, topics, folders, tags, notes, cards, versions, shares, forks, files, search indexing
    core/                        groups, classrooms, quizzes, flashcards, exams, learning events, recommendations, resources, achievements, moderation
    ai/                          AiGateway, RAG, embeddings, public-note pipeline, usage and quotas
    communication/               notifications, push, email, real-time fan-out
  libs/                          shared and business-free: config, logging/otel, errors, auth-guard, event-bus, prisma-base, testing
  contracts/                     → published as @lvn/contracts: supergraph schema, generated TS types, Zod validation, domain enums,
                                   permission matrix, event schemas
  prisma/
    schema.prisma                one database today; every model carries @@schema("users" | "notes" | "core" | "ai" | "comms")
    migrations/
  infra/
    docker/                      compose for dev and test
    terraform/                   sandbox and production
    observability/               Grafana dashboards, Loki, Tempo, Prometheus rules, OTel collector config
  docs/                          architecture/  adr/  api-changes/  runbooks/  releases/

contexts/notes/                  internal shape of every context
  notes.module.ts                the only export apps/api and apps/worker import
  graphql/                       resolvers, object types, inputs — one federation subgraph
  application/                   use-case services
  domain/                        entities, rules, events this context emits
  infrastructure/                Prisma repositories (schema "notes" only), external adapters
  workers/                       BullMQ processors
  events/                        handlers for other contexts' events → local read models
  index.ts                       public facade (typed interface) — nothing else is exported

lvn-web/                         Next.js 15
  app/                           (public)/  (auth)/  (app)/  (app)/teacher/  (app)/group-admin/
  features/<domain>/             components, hooks, GraphQL operations, feature state
  components/ui/                 shadcn primitives only
  lib/                           apollo client, auth helpers, env (typed via @lvn/contracts/config)
  state/                         Zustand: session, theme, command palette, notifications, workspace
  graphql/                       operations and codegen config (types come from @lvn/contracts)
  tests/  e2e/  .github/workflows/

lvn-mobile/                      Expo
  app/                           expo-router routes and tabs
  features/<domain>/             screens, hooks, GraphQL operations
  components/                    shared RN components
  db/                            WatermelonDB models, schema, sync engine, outbox
  lib/                           apollo client, secure storage, env (typed via @lvn/contracts/config)
  state/                         MMKV-backed preferences
  assets/  e2e/ (maestro)  eas.json  app.config.ts  .github/workflows/
```

Rules:

- **No cross-context imports.** A context imports another only through the facade interface declared in `libs/` (dependency inversion); the implementation is in-process today and an HTTP/gRPC client after extraction. Enforced by `dependency-cruiser` rules in CI; a violation fails the build.
- **One Postgres schema per context, no foreign keys across schemas.** Cross-context references are plain UUID columns. Data a context needs from another is a local read model kept current by events (e.g. `notes` keeps `membership_read_model` so `visibleNotesWhere` never joins into `core`).
- **Each context is a federation subgraph** (`@nestjs/graphql` federation driver, Apollo Federation 2 `@key` entities). `apps/api` composes the five subgraphs in-process with Apollo Gateway over local data sources; after extraction the same supergraph is served by Apollo Router pointing at service URLs. Clients see one schema either way.
- **Events over an `EventBus` interface** with two adapters: `InProcessEventBus` (default, dispatched after the outbox commit) and `NatsEventBus` (JetStream). Event payloads are versioned Zod schemas in `@lvn/contracts/events`. Switching a context to NATS is a config flag.
- **Shared code is business-free.** `libs/` holds config, logging, errors, guards, the event bus and Prisma base; anything domain-specific lives in exactly one context.
- **Observability is per context from the start.** Every span, log line and metric carries `context=<name>`; Grafana dashboards are built per context, so the day a context becomes a service its dashboard already exists. Grafana + Loki + Tempo + Prometheus is pinned over Kibana/Elastic: OpenTelemetry-native, one UI, lighter to run.
- **UI is never shared** between web and mobile. Share only `@lvn/contracts` (types, validation, enums, permission matrix, GraphQL operations where useful).
- **Contracts are semver.** A breaking GraphQL or event change bumps the major version and ships with an `api-changes/` note; web and mobile upgrade within one sprint and CI blocks a client on a major it has not adopted.

## 4. Domain model

The backend owns these definitions. Clients render them; they never reinterpret them.

### 4.1 Core entities

```text
User ──< Membership >── Organization
User ──< GroupMember >── Group ──< GroupShare >── Note
User ──< ClassroomMember >── Classroom ──< ClassroomShare >── Note
User ──< Note ──< Card (ordered blocks)
            │  ├── NoteVersion (snapshots)
            │  ├── NoteShare (user-level grants)
            │  ├── NoteArtifact (AI output: summary, quiz, flashcards, embeddings)
            │  └── Attachment ──> FileObject (S3 metadata)
            └── forkedFromNoteId / forkedFromVersionId
Subject ──< Topic (hierarchical, platform-curated + user-proposed)
Note ──< NoteTopic >── Topic
Folder (per user, nested) ──< Note
Tag (per user) ──< NoteTag >── Note
Quiz ──< Question ──< Choice;  QuizAttempt ──< Answer
FlashcardDeck ──< Flashcard;  FlashcardReview (SRS state per user)
Exam (per user: name, date, topics) 
LearningEvent (append-only)
Streak, Achievement, UserAchievement, Points ledger
Resource ──< ResourceSave, ResourceRecommendation, Comment
Comment (polymorphic: Note, Card, Resource, Group post), Reaction
Notification, DeviceToken
Report (moderation), ModerationAction
```

**Note vs Card.** A `Note` is the document (title, visibility, owner, subject/topics, folder). A `Card` is one ordered block inside it with `type` (text, heading, markdown, code, image, video, audio, file, diagram, quote, callout, checklist, table, question, quiz, flashcard) and a typed JSONB `content`. Cards are the unit of reordering, media attachment and AI processing. The editor persists Tiptap JSON per card; the backend validates each card type against a Zod schema from `@lvn/contracts/validation`.

### 4.2 Visibility

A note has exactly one `visibility`:

| Value | Who can read | Who can edit |
| --- | --- | --- |
| `PRIVATE` | Owner | Owner |
| `SHARED` | Owner + users in `NoteShare` + members of groups/classrooms in `GroupShare`/`ClassroomShare` | Owner + `NoteShare` rows with `EDITOR` |
| `PUBLIC` | Everyone, including anonymous web visitors (SEO pages) | Owner |

Transitions: `PRIVATE ⇄ SHARED ⇄ PUBLIC`. Moving **to** `PUBLIC` requires a published version, runs moderation and starts the public-note AI pipeline (section 10). Moving **away** from `PUBLIC` keeps the note URL resolving to a 404 page and removes it from search and recommendations within 60 seconds (synchronous DB update, async index removal). Existing forks are unaffected.

### 4.3 Draft, publish and versions

- Every note has a `draftRevision` (editable, autosaved) and zero or one `publishedVersionId`. Readers other than editors always see the published version.
- Autosave writes the draft every 2 s of inactivity (web) and on every card blur (mobile). Drafts are never lost: the client also persists the draft locally until the server acknowledges.
- `Publish` creates an immutable `NoteVersion` (full snapshot of all cards, not a diff). Keep all versions for `PUBLIC` notes; keep the last 50 for others, pruning oldest in a nightly job.
- Restore = create a new draft from any version. Versions are never edited.

### 4.4 Forking

- Only `PUBLIC` notes and `SHARED` notes the user can read are forkable; the owner can disable forking per note.
- A fork copies the **published version's** cards into a new `PRIVATE` note owned by the forker, with `forkedFromNoteId`, `forkedFromVersionId` and an attribution line that the fork UI shows and the forker cannot remove.
- Media attachments are referenced, not duplicated in S3; the `FileObject` gets a new permission grant for the forker.
- Forks do not sync with upstream. "Upstream has a newer version" is shown as information only.
- Content licence: by publishing publicly, a user grants LVN and other users a licence to view and fork with attribution. State this in Terms and in the publish dialog.

### 4.5 Soft delete and audit

- Notes, cards, groups, classrooms, quizzes and resources use `deletedAt`. Trash is restorable for 30 days, then hard-deleted by a job together with orphaned S3 objects.
- `AuditLog` records who changed visibility, shares, roles, memberships and moderation state. Never log note content there.

### 4.6 Identifiers

All ids are UUIDv7 (time-ordered). Public URLs use a short slug + id suffix for notes and a handle for users. Never expose sequential integers.

## 5. Permission matrix

Authorization is enforced in the backend by a single `PolicyService` (`can(user, action, resource)`), called from every resolver, every DataLoader, every search query, every file URL request and every RAG retrieval. Clients use the same matrix only to hide buttons. Permissions are defined once as constants in `@lvn/contracts/domain`.

**Roles.** Global: `STUDENT`, `TEACHER` (verified via organization or manual approval), `PLATFORM_ADMIN` (admin app only). Scoped: `GROUP_OWNER`, `GROUP_ADMIN`, `GROUP_MODERATOR`, `GROUP_MEMBER`; `CLASSROOM_TEACHER`, `CLASSROOM_TA`, `CLASSROOM_STUDENT`; `ORG_ADMIN` (admin app only). Note-level: `OWNER`, `EDITOR`, `VIEWER`.

| Action | Owner | Note Editor | Note Viewer / share recipient | Group Member | Group Mod / Admin | Classroom Student | Classroom Teacher / TA | Any logged-in user | Anonymous |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Read PRIVATE note | ✓ | – | – | – | – | – | – | – | – |
| Read SHARED note | ✓ | ✓ | ✓ | ✓ if shared to group | ✓ if shared to group | ✓ if shared to class | ✓ if shared to class | – | – |
| Read PUBLIC note | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Edit draft | ✓ | ✓ | – | – | – | – | – | – | – |
| Publish / change visibility / delete | ✓ | – | – | – | – | – | – | – | – |
| Share note (user, group, class) | ✓ | – | – | – | – | – | – | – | – |
| Fork | ✓ | ✓ | ✓ | ✓ if readable | ✓ if readable | ✓ if readable | ✓ if readable | ✓ PUBLIC only | – |
| Comment / react on note | ✓ | ✓ | ✓ | ✓ if readable | ✓ if readable | ✓ if readable | ✓ if readable | ✓ PUBLIC only | – |
| Create group |  |  |  |  |  |  |  | ✓ | – |
| Join public group / request private |  |  |  |  |  |  |  | ✓ | – |
| Post in group |  |  |  | ✓ | ✓ |  |  | – | – |
| Remove post, mute member |  |  |  | – | ✓ |  |  | – | – |
| Manage members, roles, settings |  |  |  | – | ✓ (Admin/Owner) |  |  | – | – |
| Delete group |  |  |  | – | Owner only |  |  | – | – |
| Create classroom |  |  |  |  |  | – | ✓ (TEACHER role) | – | – |
| Join classroom |  |  |  |  |  | ✓ via code/invite |  | – | – |
| Publish quiz to classroom |  |  |  |  |  | – | ✓ | – | – |
| View class member performance |  |  |  |  |  | own only | ✓ | – | – |
| Create personal quiz / deck / exam |  |  |  |  |  |  |  | ✓ | – |
| Ask AI about a note | ✓ | ✓ | ✓ | ✓ if readable | ✓ if readable | ✓ if readable | ✓ if readable | ✓ PUBLIC only | – |
| Access attachment file | same as read permission on the parent note or post, checked per request |  |  |  |  |  |  |  |  |
| Report content |  |  |  |  |  |  |  | ✓ | – |
| Moderate reports |  |  |  |  | ✓ group scope |  | ✓ class scope | – | – |

Rules that follow from the matrix:

- Search, recommendations, AI retrieval and file URLs are **filtered by the same predicate** as `Read`. Implement the predicate once as a reusable Prisma `where` builder (`visibleNotesWhere(userId)`) and a matching Typesense filter string; unit-test that both produce identical result sets on seeded data.
- Anonymous users receive only `PUBLIC` data through a dedicated unauthenticated GraphQL context; mutations are rejected.
- A `TEACHER` role is granted by an organization (admin app) or by manual review; it is never self-selected at signup.
- Minors (section 15) can be restricted from `PUBLIC` publishing and from DMs by a feature flag; the matrix is evaluated after that flag.

## 6. Backend architecture

A modular NestJS monolith deploys as two processes (`api`, `worker`) and is the source of truth for all business rules. Internally it is five bounded contexts that already behave like services; a context is extracted into its own deployment only when a metric in section 16.3 demands it, following the playbook in 6.5.

```text
TODAY (Phase 1–9)                                      LATER (per-context extraction)

Web · Mobile · Admin                                    Web · Mobile · Admin
        │ GraphQL over HTTPS/WS                                 │
   apps/api  (one process)                               Apollo Router (supergraph)
   Apollo Gateway, local data sources                   ┌─────┬──────┬──────┬──────┬─────────────┐
   ┌─────┬──────┬──────┬──────┬─────────────┐           users notes  core   ai   communication
   users notes  core   ai   communication      ──►      svc   svc    svc    svc   svc
   └─────┴──────┴──────┴──────┴─────────────┘           (each: own api+worker, own Postgres)
        │ InProcessEventBus (outbox)                            │ NATS JetStream
   apps/worker (one process, all queues)                  Redis · S3 · Typesense · AI providers
        │
   Postgres (schemas: users, notes, core, ai, comms) · Redis · S3 · Typesense
```

### 6.1 Bounded contexts

| Context | Owns | Postgres schema | Emits | Consumes (read models) |
| --- | --- | --- | --- | --- |
| `users` | auth, sessions, users, profiles, roles, `PolicyService`, device tokens, organizations (read model from admin app) | `users` | `UserRegistered`, `UserDeleted`, `RoleChanged`, `SessionRevoked` | `GroupMembershipChanged`, `ClassroomMembershipChanged` |
| `notes` | subjects, topics, folders, tags, notes, cards, versions, shares, forks, `FileObject`, search indexing, Postgres/Typesense `SearchProvider` | `notes` | `NotePublished`, `NoteUnpublished`, `NoteForked`, `NoteShared`, `FileReady` | `UserDeleted`, `GroupMembershipChanged`, `ClassroomMembershipChanged`, `NoteArtifactReady` |
| `core` | groups, classrooms, quizzes, flashcards, exams, learning events, streaks, recommendations, resources, achievements, moderation, reports | `core` | `GroupMembershipChanged`, `ClassroomMembershipChanged`, `CommentAdded`, `QuizPublished`, `ContentReported`, `LearningEventRecorded` | `NotePublished`, `UserDeleted` |
| `ai` | `AiGateway`, providers, usage and quotas, `NoteChunk` embeddings, RAG, public-note pipeline, transcription, moderation scoring | `ai` | `NoteArtifactReady`, `ModerationScored`, `AiBudgetThreshold` | `NotePublished`, `NoteUnpublished`, `FileReady`, `UserDeleted` |
| `communication` | notifications, preferences, push (FCM), email, digests, WebSocket fan-out for subscriptions | `comms` | `NotificationDelivered` | nearly everything above |

The `users` context exposes `PolicyService` through its facade; other contexts call it in-process today and over gRPC after extraction, so authorization has exactly one implementation. Modules inside a context (`notes/graphql`, `notes/application`, …) call each other freely; only the context boundary is guarded.

### 6.2 GraphQL conventions

- Code-first with `@nestjs/graphql`; the SDL is exported to `contracts/graphql/supergraph.graphql` on every build and diffed in CI (`graphql-inspector`). A breaking change fails the PR unless an `api-changes/` file marks it approved.
- Relay-style cursor pagination for every list (`edges`, `node`, `pageInfo`); max 100 per page.
- Mutations take one `input` object and return a payload type with the entity and `userErrors`; naming `createNote`, `updateNoteDraft`, `publishNote`, `forkNote`.
- Every nested field that hits the database goes through a DataLoader. Query depth limit 8, complexity limit 1000 (`graphql-query-complexity`), persisted queries only in production (Apollo APQ + allow-list generated by codegen).
- Errors use a fixed `extensions.code` set: `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION`, `CONFLICT`, `RATE_LIMITED`, `INTERNAL`. Stack traces never reach clients.
- Subscriptions: `notificationReceived`, `commentAdded(noteId)`, `classroomActivity(classroomId)`, `noteProcessingStatus(noteId)`.

### 6.3 Performance

- Measure first: OpenTelemetry spans per resolver, slow-query log at 200 ms, `EXPLAIN ANALYZE` for anything in the top 20.
- Redis cache only for: feature flags, user session claims, public note render payloads (TTL 5 min, invalidated on publish), rate-limit counters, recommendation results (TTL 1 h). Never for permission decisions.
- Full notes load in two steps: metadata + outline first, cards paginated or streamed by section.
- Indexes are part of the migration that introduces the query. Composite indexes on `(ownerId, deletedAt, updatedAt)`, `(visibility, publishedAt)`, `(noteId, position)`, membership tables on `(userId, …)` and `(groupId, …)`.

### 6.4 Migrations

Prisma Migrate, one migration per PR, reviewed, reversible where practical. `prisma migrate deploy` runs as a pre-deploy step; the deployment aborts if it fails. Production schema is never edited by hand.

### 6.5 Monolith → microservices extraction playbook

Extraction is a repeatable procedure, not a project. Recommended order: `ai` first (most isolated, most variable load), then `communication`, `notes`, `core`, and `users` last (every service depends on it).

1. **Preconditions (measured, not assumed).** A section 16.3 trigger points at this context; the `dependency-cruiser` boundary rule has been green for 30 days; no SQL joins across its schema (checked by a CI query against `information_schema`); its facade is the only thing other contexts import.
2. **Switch its events to NATS.** Flip the context's `EVENT_BUS=nats` flag in sandbox; both adapters publish the same `@lvn/contracts/events` payloads, so consumers do not change. Run for a week.
3. **Give it its own database.** Create the new Postgres instance; use logical replication of its schema from the shared instance; cut over writes during a maintenance window; the Prisma schema for the context moves to `contexts/<name>/prisma/`.
4. **Deploy it as a service.** Add `apps/<name>-service` (a composition root importing only that context module plus `libs/`), publish its subgraph SDL, register it in Apollo Router's supergraph, remove it from `apps/api`'s local composition. Its workers move to `apps/<name>-worker`.
5. **Swap the facade implementation.** Replace the in-process facade binding with the gRPC/HTTP client generated from the same interface; retries, timeouts and circuit breaker come from `libs/`.
6. **Observe, then delete.** The per-context Grafana dashboard already exists; compare p95, error rate and queue depth for a week, then delete the in-process binding.

Things that make this cheap, and that are therefore non-negotiable from Phase 1: schema-per-context with no cross-schema FKs, read models instead of cross-context queries, events through the bus interface, facades as the only import surface, and the boundary rule in CI. Skipping any of them turns extraction back into a rewrite.

## 7. Authentication and security

The backend owns identity, sessions, roles and verification. Clients call `signUp`, `signIn`, `oauthExchange`, `refreshSession`, `signOut`, `verifyEmail`, `requestPasswordReset`, `resetPassword` and contain no auth business logic.

### 7.1 Sessions

- Access token: JWT, RS256, 15 min, claims `sub`, `roles`, `sid`. Refresh token: 256-bit random, 30 days, rotated on every use, stored as SHA-256 hash in `Session` with device info; reuse of a rotated token revokes the whole session family.
- Web stores the refresh token in an `HttpOnly; Secure; SameSite=Lax` cookie and the access token in memory. Mobile stores both in `expo-secure-store`. Nothing auth-related in `localStorage` or `AsyncStorage`.
- OAuth (Google, GitHub, LinkedIn) uses Authorization Code + PKCE. The client receives the provider code and sends it to `oauthExchange`; the backend verifies it and issues LVN tokens. Account linking by verified email only.
- Email verification required before publishing, joining groups or commenting. Password policy: minimum 10 characters, checked against a breached-password list, hashed with Argon2id.
- Rate limits (Redis sliding window): 5 sign-in attempts per account per 15 min, 3 password resets per hour, 100 GraphQL operations per minute per user, 20 AI requests per minute per user.

### 7.2 Security requirements

- Helmet, strict CORS allow-list per environment, CSRF protection on the cookie-based refresh endpoint.
- All inputs validated with Zod at the resolver boundary; file uploads validated by magic bytes, not extension.
- Secrets from AWS Secrets Manager (sandbox/prod) or `.env.local` (dev, git-ignored). CI scans with `gitleaks`.
- Dependency scanning (`pnpm audit`, Dependabot) on every PR; container image scanning before deploy.
- Logs redact passwords, tokens, email bodies and note content. Request ids propagate from client to logs.
- Account deletion: user-initiated, 14-day grace period, then hard delete of personal data and anonymisation of public contributions (author shown as "Deleted user").

## 8. Storage

Each store has one job. PostgreSQL is the only source of truth; Redis holds nothing that cannot be rebuilt; S3 holds bytes, never metadata of record.

| Store | Holds | Never holds |
| --- | --- | --- |
| PostgreSQL | All entities in section 4, embeddings (pgvector), `FileObject` metadata, feature flags, audit log | File bytes, session-only data, queue payloads |
| Redis | Rate limits, BullMQ queues, pub/sub for subscriptions, short-TTL caches listed in 6.3, distributed locks | Anything without a TTL except queues; permission decisions |
| S3 | Images, audio, video, PDF, documents, generated thumbnails and transcodes | Anything queryable |

### 8.1 Upload flow

1. Client calls `createUploadIntent(input: {fileName, mimeType, sizeBytes, purpose, parentId})`. Backend checks permission on the parent, quota and limits, and returns a pre-signed PUT URL (10 min) plus a `FileObject` in `PENDING` state.
2. Client uploads directly to S3.
3. Client calls `completeUpload(fileId)`. Backend verifies the object exists, checks magic bytes and size, sets `READY`, and enqueues processing (image resize to 3 sizes, video transcode to H.264 720p, audio normalise, PDF text extraction, malware scan with ClamAV).
4. Reads use pre-signed GET URLs (15 min) issued only after `PolicyService.can(user, 'read', parent)`. Public note media is served through CloudFront with signed cookies on the public note page.

Limits: images 20 MB, audio 100 MB, video 500 MB, documents 50 MB; 5 GB per student, 20 GB per teacher, enforced server-side. Keys are `{env}/{ownerId}/{fileId}/{variant}` with no original filename in the key.

### 8.3 Asset metadata (every S3 object has a `FileObject` row)

No object is written to S3 without a `FileObject` row created first, and no `FileObject` reaches `READY` without a verified object. A nightly reconciliation job lists both sides and flags drift. Clients never receive raw S3 keys; they receive `fileId` and resolve URLs through the API.

| Column | Type | Source | Purpose |
| --- | --- | --- | --- |
| `id` | UUIDv7 | API | Public handle used everywhere |
| `ownerId` | UUID → User | API | Quota, permissions |
| `parentType`, `parentId` | enum + UUID | API | `NOTE`, `CARD`, `GROUP_POST`, `RESOURCE`, `AVATAR`; drives the permission check |
| `purpose` | enum | API | `ATTACHMENT`, `COVER`, `VOICE_NOTE`, `AVATAR`, `IMPORT` |
| `bucket`, `storageKey` | text | API | `{env}/{ownerId}/{fileId}/original` |
| `variants` | JSONB | worker | `{thumb: key, medium: key, hls: key, transcript: fileId}` |
| `mimeType` (declared), `detectedMimeType` | text | client / worker | Mismatch → reject |
| `sizeBytes` | bigint | S3 HEAD | Quota accounting |
| `checksumSha256` | text | worker | Dedup and integrity |
| `width`, `height`, `durationMs`, `pageCount` | int | worker | Layout without loading the file |
| `originalFileName` | text | client | Display only; never in the key |
| `status` | enum | API/worker | `PENDING`, `UPLOADED`, `PROCESSING`, `READY`, `FAILED`, `QUARANTINED`, `DELETED` |
| `scanResult`, `scannedAt` | enum, timestamp | worker | ClamAV outcome |
| `visibilitySnapshot` | enum | API | Cached parent visibility for CDN cache keys; refreshed on parent change |
| `accessCount`, `lastAccessedAt` | int, timestamp | API (batched via Redis) | Lifecycle tiering |
| `expiresAt` | timestamp | API | Temporary files (imports, exports) |
| `createdAt`, `updatedAt`, `deletedAt` | timestamps | API | Soft delete; 30-day trash |

S3 object metadata and tags mirror the identity fields (`x-amz-meta-file-id`, `x-amz-meta-owner-id`, `x-amz-meta-env`, tag `parentType`) so lifecycle rules, cost reports and incident forensics work from S3 alone. Lifecycle: objects not accessed for 180 days move to Infrequent Access; `DELETED` objects expire after 30 days; `QUARANTINED` objects are retained 90 days in a restricted prefix.

Dedup: identical `checksumSha256` within one owner reuses the object with a new `FileObject` row (metadata is per use, bytes are shared); cross-owner dedup is not done, to avoid leaking existence of private files.

### 8.2 Backups

RDS automated backups with 30-day point-in-time recovery; S3 versioning + cross-region replication for production; weekly restore drill into the sandbox account, documented in `docs/runbooks/restore.md`.

## 9. Background jobs, real-time and notifications

The API responds in under 300 ms p95; anything slower than a database transaction runs as a BullMQ job in the worker process.

### 9.1 Queues

| Queue | Jobs | Retry | Idempotency key |
| --- | --- | --- | --- |
| `media` | resize, transcode, scan, pdf-extract | 3, exponential | `fileId` |
| `ai` | summarise, generate-quiz, generate-flashcards, embed, transcribe, moderate | 3, exponential, 10 min timeout | `noteVersionId:task` |
| `search` | index-note, remove-note, index-resource, reindex-all | 5 | `entityId:version` |
| `notifications` | push, email, digest | 3 | `notificationId` |
| `learning` | aggregate-events, compute-streaks, recommendations | 1, scheduled | `userId:date` |
| `housekeeping` | prune-versions, empty-trash, delete-accounts, orphan-s3 | 1, nightly | date |

Every job is idempotent, writes its state to a `JobStatus` row the client can query (`noteProcessingStatus` subscription), and goes to a dead-letter queue after final failure with an alert. Jobs are enqueued **after** the Postgres transaction commits (transactional outbox table polled by the worker) so a rolled-back write never leaves a job behind.

### 9.2 Real-time

GraphQL subscriptions via `graphql-ws`, fan-out through Redis pub/sub so multiple API instances work. Subscriptions carry ids only; the client refetches the entity, so permission checks happen on the fetch. Mobile uses subscriptions only while foregrounded; in the background it relies on push.

### 9.3 Notification delivery

| Channel | Used for | Notes |
| --- | --- | --- |
| In-app (`Notification` table + subscription) | Everything | Always written first |
| Push (FCM) | Comments, shares, classroom posts, quiz published, revision reminders, streak at risk | Per-category user setting; quiet hours default 22:00–07:00 local |
| Email | Verification, reset, weekly digest, classroom announcements | React Email templates; one-click unsubscribe per category |

`DeviceToken` rows are refreshed on app launch and pruned on FCM `NotRegistered`. Deep links use `learnvianotes://` and universal links to `https://learnvianotes.com/...` resolved by Expo Router.

## 10. AI gateway and RAG

All AI runs behind the backend `ai` module. Clients never hold provider keys or call providers; they call GraphQL mutations that enqueue or stream through the gateway.

### 10.1 Gateway

```text
Client ─► GraphQL (askAi, summariseNote, generateQuiz, …)
            │  PolicyService + quota check + prompt-injection filter
            ▼
        AiGateway (provider adapters: OpenAI | Anthropic | Ollama)
            │  model routing by task · token accounting · retries · circuit breaker
            ▼
   sync (streamed over subscription, ≤ 30 s)   |   async (BullMQ `ai` queue)
```

- Task → default model table lives in the database (feature-flag style) so models can be swapped without a deploy. Cheap model for summaries and flashcards, stronger model for RAG answers and code explanation.
- Every call writes `AiUsage` (`userId`, `task`, `model`, `promptTokens`, `completionTokens`, `costMicroUsd`, `latencyMs`). Quotas: students 200k tokens/day, teachers 1M/day, enforced before the call; a per-environment monthly budget cap trips a circuit breaker and degrades to "AI temporarily unavailable".
- Prompts are versioned templates in `apps/api/src/modules/ai/prompts/`; outputs that must be structured use JSON schema / tool-calling and are validated with Zod before storage.
- Content sent to third-party providers excludes user identity; a per-provider data-processing flag decides which providers may receive private notes (default: only providers with zero-retention agreements; otherwise private notes use the self-hosted model).

### 10.2 Permission-aware RAG

```text
Question ─► authenticated user ─► scope (this note | my notes | my groups/classes | public)
   ─► candidate set = visibleNotesWhere(userId) ∩ scope          (Postgres, before retrieval)
   ─► pgvector ANN over NoteChunk filtered by that candidate set   (top 40)
   ─► rerank (cross-encoder or LLM scoring) ─► top 8 chunks
   ─► LLM with citations ─► answer + sources (noteId, cardId, versionId)
```

- Chunks are built per published `NoteVersion` (not drafts), \~500 tokens with 50 overlap, stored in `NoteChunk(noteId, versionId, cardId, position, text, embedding)`. Unpublishing deletes chunks in the same job that removes search entries.
- The visibility filter is applied **in the SQL query**, never after retrieval. A test seeds two users with private notes on the same topic and asserts zero cross-leakage across 1,000 random questions.
- Answers always return sources; a source the user cannot open is a bug, not a UI problem.

### 10.3 Public-note pipeline

On `publishNote` → `PUBLIC`: moderation → text extraction → summary → key concepts → questions → quiz → flashcards → embeddings → search index → recommendation signals. Each step is a separate job writing a `NoteArtifact(type, versionId, status, payload)`; the original note is never modified. The student sees progress via `noteProcessingStatus` and can hide any generated artifact.

## 11. Search

Search is one `search` module with a `SearchProvider` interface and two implementations: `PostgresSearchProvider` (Phases 2–3, `tsvector` + `pg_trgm`) and `TypesenseSearchProvider` (Phase 4+). Clients call one `search(query, filters, scope)` GraphQL field and never know which provider answered.

- Collections: `notes` (published versions only), `users` (handle, name, bio), `groups`, `classrooms` (members only), `resources`, `topics`. One Typesense collection per entity type, one `search` field with a union result type.
- Permission filtering: each `notes` document carries `visibility`, `ownerId`, `sharedUserIds[]`, `groupIds[]`, `classroomIds[]`. The API builds the Typesense `filter_by` from the user's memberships on every request. Membership changes enqueue a re-index of affected documents; a stale window above 60 s is an incident.
- Semantic search: hybrid ranking combining Typesense keyword score with pgvector similarity (reciprocal rank fusion) behind a feature flag.
- Web: Cmd/Ctrl+K palette with grouped results and keyboard navigation. Mobile: Explore tab search with recent queries stored locally.
- Indexing is always asynchronous through the `search` queue; a `reindex-all` job streams from Postgres in batches of 500 with a version check so it can run while writes continue.

## 12. Web agent

Web is the power-user surface: create, organise, research, manage. It owns `apps/web` only — UI, routing, web state, the editor, teacher and group-admin screens, web tests. It owns no business rules, no auth logic, no direct storage or AI access.

### 12.1 Structure

```text
app/
  (public)/        landing, /n/[slug]-[id] public notes (ISR), /u/[handle], /explore   ← SSR/ISR, SEO
  (auth)/          sign-in, sign-up, verify, reset, oauth callback
  (app)/           authenticated shell: home, notes, groups, classrooms, quizzes, search, ai, profile
    teacher/       classroom management, quiz builder, analytics  (role-gated)
    group-admin/   group settings, members, moderation            (role-gated)
features/<domain>/ components, hooks, graphql operations, local state for that feature
components/ui/     shadcn primitives only — no business logic
lib/               apollo client, auth helpers, env (typed from @lvn/contracts/config)
state/             Zustand stores: session, theme, command palette, notifications, workspace context
```

### 12.2 Rules

- **Public notes are SEO pages.** `/n/[slug]-[id]` renders server-side with ISR (revalidate on publish via on-demand revalidation webhook from the API), Open Graph image generated per note, `sitemap.xml` and `robots.txt` from the API's public-note list. Private and shared notes are client-rendered behind auth.
- State follows the four scopes: local React state → feature hooks → Apollo cache for server data → Zustand only for the five global stores above. A value used by two components is not a reason for a global store.
- Apollo: normalised cache keyed by `id`, `fetchPolicy: cache-and-network` for lists, optimistic responses for reactions, saves and card reorders, `useFragment` for cards. Persisted-query hashes generated by codegen.
- Forms: React Hook Form + the shared Zod schema from `@lvn/contracts/validation`; server `userErrors` map to fields.
- Editor: Tiptap with one extension per card type, three-pane layout (outline · cards · AI panel), autosave with a local IndexedDB mirror of the draft until the server acknowledges, version history drawer, slash-command block insertion, paste handling for images (upload flow 8.1) and code.
- Accessibility from day one: keyboard navigation for the editor and command palette, focus management in dialogs, WCAG 2.1 AA contrast, axe checks in Playwright.
- i18n via `next-intl` with English only shipped, all strings in message files from the first screen.
- Performance budgets: LCP < 2.5 s on public notes, route JS < 200 kB gzipped per page, images via `next/image` from CloudFront. Lighthouse CI on every PR for the public routes.

## 13. Mobile agent

Mobile answers "what should I learn right now?": quick capture, reading, AI, community, notifications, exam prep, focus mode, voice notes. It owns `apps/mobile` only — navigation, mobile UX, local storage, offline sync, push handling, media capture, mobile tests. Native Expo app, not a web wrapper.

### 13.1 Navigation and storage

- Expo Router tabs: Home · Explore · Create (centre sheet: Note, Quick Note, Voice Note, Photo, Upload, Quiz, Flashcard) · Community · Profile. Teacher and group-admin actions appear inside the relevant classroom/group screens, not as extra tabs.
- Storage tiers: `expo-secure-store` for tokens and encryption keys; WatermelonDB (SQLite) for notes, cards, subjects, groups, drafts and the sync queue; MMKV for small preferences and last-opened state; `expo-file-system` cache directory for media with an LRU cap of 500 MB.
- Three environments via EAS build profiles and `app.config.ts` reading `EXPO_PUBLIC_*` from `@lvn/contracts/config`; bundle ids `com.learnvianotes.dev`, `.sandbox`, \`\` (prod) so all three install side by side. No URL or key is hardcoded.

### 13.2 Offline and sync

```text
edit ─► WatermelonDB (local, instant) ─► outbox row {entity, op, payload, baseVersion, clientOpId}
                                               │ connectivity restored / app foregrounded
                                               ▼
                                   syncPush(ops) ─► API applies in order, returns per-op result
                                               │
                                   syncPull(since cursor) ─► changed entities ─► merge into local DB
```

Conflict resolution is defined per entity and implemented in the backend; the client only applies the server's verdict:

| Entity | Rule |
| --- | --- |
| Note metadata (title, folder, tags) | Last-writer-wins by server receive time |
| Card content (same card edited on two devices) | Server keeps the latest write and stores the other as a `NoteVersion` tagged `CONFLICT`; the client shows a "conflicting copy" banner with a one-tap restore |
| Card order | Positions are fractional indexes; concurrent inserts never collide, concurrent moves resolve LWW |
| Card create / delete | Create always wins; delete of a card edited elsewhere after `baseVersion` is rejected and surfaced |
| Quiz attempts, flashcard reviews, learning events | Append-only, idempotent on `clientOpId`; never conflict |
| Visibility / publish | Online-only mutations; disabled offline |

Every outbox op carries a `clientOpId` (UUID) so retries are idempotent. Media uploads queue separately and resume with S3 multipart. A draft is never discarded without the user confirming; if sync fails five times the op moves to a visible "needs attention" list.

### 13.3 Platform requirements

- Push via FCM with notification channels on Android and provisional authorisation on iOS; tapping opens the deep link.
- Voice notes: record with `expo-av`, upload, transcription returns as a `NoteArtifact`; the user accepts or edits before it becomes a card.
- Biometric unlock (optional) guards the app, not the tokens.
- OTA updates via EAS Update for JS-only changes; native changes go through store builds. Runtime version policy `appVersion`.
- Performance: cold start < 2 s on a mid-range Android device, lists virtualised with FlashList, images via `expo-image` with disk cache.
- Accessibility: labels on every control, dynamic type, reduced-motion respected.

## 14. Learning events, recommendations and resources

### 14.1 Learning events

One append-only `LearningEvent(id, userId, type, entityType, entityId, topicIds[], durationMs, metadata JSONB, clientTs, serverTs, sessionId, platform)` table, partitioned monthly, feeds history, streaks, recommendations, analytics and notifications. Clients emit through a single `trackEvents(batch)` mutation (batched every 10 s or 20 events, queued offline); no UI component calls analytics directly. Event types are an enum in `@lvn/contracts/domain`: `NOTE_OPENED`, `NOTE_CREATED`, `NOTE_PUBLISHED`, `NOTE_FORKED`, `CARD_VIEWED`, `TOPIC_VIEWED`, `VIDEO_STARTED`, `VIDEO_COMPLETED`, `QUIZ_STARTED`, `QUIZ_COMPLETED`, `FLASHCARD_REVIEWED`, `TIME_SPENT`, `NOTE_SAVED`, `TOPIC_REVISITED`, `EXAM_CREATED`, `RESOURCE_VIEWED`, `RESOURCE_SAVED`, `AI_REQUESTED`, `SEARCH_PERFORMED`. Product analytics (PostHog, self-hosted) receives a derived, pseudonymous copy from the worker, never from clients.

### 14.2 Streaks, history and exams

- Streak = a day with ≥ 1 qualifying event (note opened ≥ 2 min, quiz completed, flashcards reviewed, note created) in the user's time zone; one freeze per week earned by a 7-day streak. Computed nightly and incrementally on event ingest.
- Learning history is a paginated view over events grouped by day and topic; weak-topic detection = topics with quiz accuracy < 60 % over the last 3 attempts or no revisit in 14 days before an exam.
- Exam planning: user enters exam name, date and topics; the planner distributes revision sessions backward from the date and emits reminders through the notification system.
- Flashcards use FSRS scheduling; review state is per user per card.

### 14.3 Recommendations

Phase 6 ships rule-based recommendations computed hourly per active user into `Recommendation(userId, kind, entityId, score, reason, expiresAt)`: revise weak topics, continue unfinished notes, upcoming-exam topics, popular public notes in the user's subjects, quizzes on recently read topics. Every item carries a human-readable `reason`. The structure allows a later embedding-based model to write into the same table. Results are filtered by `visibleNotesWhere` at read time, not only at compute time.

### 14.4 Resources

`Resource(type: BOOK | COURSE | TOOL | SOFTWARE | HARDWARE | OTHER, title, description, url, author, imageFileId, topicIds[], submittedById, status: PENDING | APPROVED | REJECTED)` with `ResourceSave`, `ResourceRecommendation(toUserId | toGroupId)` and polymorphic comments. Students submit, moderators approve, everyone searches and saves. Outbound links carry `rel="nofollow ugc"`. No price tracking, affiliate links, cart or vendor accounts in this scope.

## 15. Moderation, compliance and privacy

A student community with public content and minors needs human moderation and a legal baseline before the first public note ships (Phase 2 exit criterion, not Phase 9).

### 15.1 Moderation

- Automated: AI moderation on publish and on comments (categories: harassment, sexual, self-harm, hate, spam, copyright claim). Scores above threshold put content in `PENDING_REVIEW` instead of `PUBLIC`; the author is told, with a reason.
- User reporting: `reportContent(entityType, entityId, reason, details)` on notes, comments, groups, resources and profiles. Users can block other users (hides their content and prevents DMs/comments).
- Queue: `Report` rows feed a moderation queue. Group moderators handle group scope, classroom teachers handle class scope, platform moderators (admin app) handle public scope. Actions (`hide`, `remove`, `warn`, `suspend`, `dismiss`) are recorded in `ModerationAction` and the audit log; the author can appeal once.
- Until the admin app exists, a minimal internal moderation page lives behind a `PLATFORM_ADMIN`-only route in the web app and is removed when admin.learnvianotes.com ships.

### 15.2 Compliance

| Requirement | Implementation |
| --- | --- |
| Age | Date of birth at signup. Under 13 (or local digital-consent age: 16 in parts of the EU, 18 under India's DPDP Act) requires verifiable parental or institutional consent; without it the account is limited to private notes and classroom content, no public publishing, no DMs, no behavioural recommendations |
| Consent and terms | Versioned Terms, Privacy Policy and public-content licence; acceptance recorded with version and timestamp; re-prompt on material change |
| Data export | `requestDataExport` produces a ZIP (notes as Markdown + media + JSON) within 24 h via a job; downloadable for 7 days |
| Deletion | Section 7.2; a deletion also purges search index, embeddings, S3 objects and FCM tokens, and anonymises comments |
| Data residency | One primary region per deployment (India: `ap-south-1`); no cross-region replication of personal data except encrypted backups |
| Retention | Learning events raw 24 months then aggregated; audit log 7 years; AI usage 12 months; logs 30 days |
| Encryption | TLS 1.2+ in transit; AES-256 at rest for RDS, S3, ElastiCache; application-level encryption for OAuth refresh tokens |
| Cookies / tracking | No third-party trackers on the student app; analytics is first-party and pseudonymous |
| Copyright | DMCA/takedown flow via `reportContent(reason: COPYRIGHT)`; repeat-infringer policy |

Product analytics never receives note content, and AI providers never receive user identity (section 10.1).

## 16. Environments, deployment and scaling

Three fully isolated environments, infrastructure as code, immutable container images, and a deployment pipeline that cannot reach production without passing migrations and the full test suite.

### 16.1 Environments

|  | Development | Sandbox | Production |
| --- | --- | --- | --- |
| Purpose | Local laptop | Shared staging, QA, demo, mobile store review | Real users |
| Infra | Docker Compose: Postgres, Redis, MinIO, Typesense, Mailpit, Ollama (optional) | Terraform, separate AWS account | Terraform, separate AWS account |
| Data | Seed script, deterministic | Synthetic + anonymised fixtures, reset weekly | Real; never copied downward |
| Domains | `localhost`, `*.lvn.local` | `sandbox.learnvianotes.com`, `api.sandbox…` | `learnvianotes.com`, `api.learnvianotes.com` |
| OAuth apps | Dev credentials | Sandbox credentials | Production credentials |
| AI | Ollama or capped dev keys | Capped keys, cheap models | Production keys, budget cap |
| Mobile | `com.learnvianotes.dev`, EAS `development` profile | `.sandbox`, EAS `preview`, TestFlight / internal track | store build, EAS `production` |

All configuration is read through `@lvn/contracts/config`, which validates every variable with Zod at process start and fails fast on a missing or malformed value. The canonical list lives in `docs/architecture/env.md` and `.env.example`; CI fails if a variable is used in code but missing from the example. Secrets come from AWS Secrets Manager (injected as ECS task secrets) in sandbox/prod and from git-ignored `.env.local` in dev. Nothing is ever hardcoded.

### 16.2 Deployment topology (production)

```text
Route 53 ─► CloudFront ─┬─► S3 (web static assets, public media via signed cookies)
                        └─► ALB (WAF: rate rules, OWASP managed rules)
                               ├─► ECS Fargate: web      (Next.js, 2+ tasks, autoscale on CPU/req)
                               ├─► ECS Fargate: api      (NestJS, all five contexts, 2+ tasks, autoscale on CPU/p95)
                               └─► ECS Fargate: worker   (BullMQ, all queues, autoscale on queue depth)
   RDS PostgreSQL 16 (Multi-AZ, read replica, pgvector; schemas users/notes/core/ai/comms)
   ElastiCache Redis (Multi-AZ)   Typesense (ECS)   S3 (versioned, replicated)   Secrets Manager
   Observability: OTel collector sidecar → Prometheus + Loki + Tempo on ECS (or Grafana Cloud) → Grafana

After the first extraction, the same diagram gains: ECS Fargate: apollo-router · ECS Fargate: <context>-service + <context>-worker ·
RDS instance per extracted context · NATS JetStream (3-node) · a service mesh is NOT added until ≥ 4 services are extracted.
Move to EKS only when ECS service count exceeds ~15 or per-pod sidecars become necessary.
```

Requirements:

- Stateless `web`, `api` and `worker` containers; all state in Postgres, Redis, S3. Any task can be killed at any moment without data loss (jobs are idempotent, drafts are acknowledged).
- One immutable image per commit SHA, built once, promoted sandbox → production. No rebuilds between environments.
- Zero-downtime deploys: rolling ECS deployment with health checks (`/health/live`, `/health/ready`); readiness waits for DB, Redis and schema version match.
- Migrations run as a one-off ECS task **before** the new api tasks start; expand/contract pattern (add column → deploy code → backfill → drop) so old and new code run together during rollout. Rollback = redeploy previous image; destructive migrations only after the following release.
- Private subnets for all compute and data; only ALB and CloudFront are public. Security groups allow api→RDS/Redis only.
- Production deploy requires: green CI on `main`, sandbox soak of ≥ 1 h with no new Sentry errors, manual approval, deployment window outside Indian evening peak unless hotfix.
- Mobile releases: EAS Update for JS changes after sandbox verification; native builds through TestFlight / Play internal track → staged rollout 10 % → 50 % → 100 % with crash-rate gate (< 0.5 %).

### 16.3 Scaling plan

Start small and measured; every step below is triggered by a metric, not by anticipation.

| Trigger | Action |
| --- | --- |
| api p95 > 300 ms or CPU > 60 % | Add Fargate tasks (autoscaling, min 2, max 20) |
| Read-heavy queries dominate | Route public-note reads and search-index builds to the read replica via Prisma read-replica extension |
| `LearningEvent` > 100 M rows | Already monthly-partitioned; detach and archive partitions older than 24 months to S3 Parquet |
| Queue depth > 1,000 for 5 min | Worker autoscale on BullMQ depth; separate worker services per queue when one queue starves another |
| Postgres connections exhausted | PgBouncer (RDS Proxy) in transaction mode; Prisma pool sized per task |
| Redis memory > 70 % | Review TTLs; shard by moving queues to a dedicated Redis |
| Postgres full-text too slow | Already planned: switch `SearchProvider` to Typesense (Phase 4) |
| pgvector > 20 M chunks | Partition `NoteChunk` by subject or move to a dedicated vector service behind the same interface |
| A module needs independent scaling or isolation (AI, media) | Run the extraction playbook (6.5) for that context; recommended order ai → communication → notes → core → users |
| Multi-region demand | Second region with its own Postgres primary for a different data-residency zone; no active-active |

### 16.4 CI/CD

Every PR: format, lint, type-check, unit + component tests, integration tests with Testcontainers, GraphQL schema diff, build all apps, `gitleaks`, dependency audit, Lighthouse CI on public routes. `main` merge: build images, deploy to sandbox, run Playwright + Maestro E2E against sandbox, migration dry-run against a sandbox snapshot. Production: manual approval → migration task → rolling deploy → smoke tests → automatic rollback on failed health or error-rate spike.

### 16.5 Observability and operations

- OpenTelemetry traces across web → api → worker → Postgres; Prometheus metrics (request rate, p50/p95/p99, error rate, queue depth, job duration, DB pool, Redis hit rate, AI tokens and cost per task); Loki structured JSON logs with request id; Sentry for exceptions on all three apps.
- SLOs: API availability 99.9 %, API p95 < 300 ms, job success 99.5 %, public note TTFB < 500 ms. Alerts on SLO burn rate, DLQ growth, replica lag > 10 s, failed deploys, AI budget at 80 %.
- Runbooks in `docs/runbooks/` for: restore from backup, rotate secrets, drain a queue, roll back a release, take a note offline, respond to a leakage report. On-call rotation once there are real users.

## 17. Testing strategy

Tests run only against isolated infrastructure (Testcontainers Postgres/Redis/MinIO, mocked AI provider with recorded fixtures) and never against sandbox or production data. Seed data is deterministic (`pnpm db:seed --scenario=<name>`).

| Layer | Backend | Web | Mobile | Gate |
| --- | --- | --- | --- | --- |
| Unit | Services, domain rules, `PolicyService`, validators, job handlers | Utilities, hooks, Zustand stores, editor transforms | Utilities, sync merge logic, stores | 80 % line coverage on `contracts/ and libs/`, `PolicyService` 100 % branch |
| Component | — | Editor, card types, forms, search palette, quiz UI (Testing Library) | Cards, editor, forms, navigation (RN Testing Library) | Every exported component with props has a test |
| Integration | GraphQL resolvers against real Postgres/Redis/MinIO; auth flows; upload flow; queue → worker → status | Apollo operations against a schema-mocked server (MSW) | WatermelonDB sync against mocked API; secure-store; upload resume | All mutations and list queries |
| Contract | Schema diff + persisted-query allow-list | Codegen types compile against current schema | Same | Breaking change without `api-changes/` entry fails |
| E2E | — | Playwright: sign-in, create/edit/publish/fork note, join group/class, take quiz, search, Ask AI | Maestro on Android emulator + iOS simulator: open, sign-in, create note offline, reconnect, sync, read, share, fork, join group, quiz, Ask AI | Run on every `main` merge against sandbox |
| Security | Section 17.1 | Dependency + axe | Dependency | Mandatory, blocks release |
| Performance | k6 load test: 500 concurrent users, p95 < 300 ms; `EXPLAIN` checks on top queries | Lighthouse CI budgets | Cold-start and list-scroll profiling on a mid-range device | Phase 9 exit, then weekly |

### 17.1 Security tests (mandatory)

A fixed suite seeds Student A, Student B, Teacher T, Group G (A member, B not), Classroom C (B member, A not) and asserts for every channel — GraphQL query, GraphQL mutation, search, recommendations, file URL, RAG, subscription, SEO page — that:

- B cannot read, fork, comment on or receive AI answers about A's private notes.
- B cannot see G's shared notes or posts; A cannot see C's content.
- A student cannot obtain `TEACHER` or `GROUP_ADMIN` through any mutation.
- A pre-signed URL issued to A does not work after A loses access (URL TTL ≤ 15 min and permission re-checked on issue).
- Unpublishing a note removes it from search, recommendations and RAG within 60 s.
- Query depth, complexity, pagination caps and rate limits reject abuse.
- Uploads with spoofed MIME, oversized payloads or EICAR test file are rejected or quarantined.
- Brute-force and credential-stuffing patterns are rate-limited; refresh-token reuse revokes the session family.

The suite runs on every PR touching `auth`, `notes`, `files`, `search`, `ai`, `groups` or `classrooms`, and nightly in full.

## 18. Phases and exit criteria

Work proceeds strictly in order. A phase is closed only when its exit criteria pass in sandbox and the application is buildable, deployed and green. Later-phase code is not written early; schema fields for later phases are added only when a current feature needs them.

| Phase | Scope | Exit criteria |
| --- | --- | --- |
| 0 Architecture | Inspect existing repo; write `existing-state.md`, this document's app-specific addenda, ERD, env reference, ADR-0001…; GraphQL schema skeleton; permission matrix encoded in `@lvn/contracts/domain` | Three agents sign off on the same documents; empty monorepo builds and CI runs |
| 1 Foundation | Monorepo, `packages/config`, NestJS + Prisma + Redis + MinIO, auth (email + 3 OAuth), sessions, roles, `PolicyService`, upload flow, logging, error codes, Testcontainers, Docker Compose, Terraform for sandbox, CI, Sentry, OTel | Web and mobile sign in on all providers in dev and sandbox; migration deploys; file upload round-trips; security suite scaffold passes |
| 2 Content | Subjects, topics, folders, tags, notes, cards (all types), editor web + mobile, autosave, drafts, versions, visibility, user sharing, forking, soft delete, public note SEO page, Postgres search, moderation gate, Terms/consent, age gate | Full note lifecycle E2E on web and mobile incl. offline edit and sync; leakage tests pass; Lighthouse ≥ 90 on public note |
| 3 Community | Groups + roles, classrooms + teacher role, group/class sharing, comments, reactions, activity feed, notifications (in-app, push, email), reporting + moderation queue | Join/post/moderate flows E2E; subscription fan-out across 2 api tasks; permission matrix fully tested |
| 4 Search | Typesense provider, Cmd/K, mobile search, filters, re-index job, hybrid ranking flag | Index parity test vs Postgres provider; permission filter test; p95 < 150 ms |
| 5 AI | `AiGateway`, usage + quotas, summaries, quick notes, RAG Ask AI with sources, quiz + flashcard generation, code explanation, transcription, public-note pipeline | RAG leakage test 0/1,000; budget breaker verified; all artifacts stored separately from notes |
| 6 Learning intelligence | `trackEvents`, partitioned events, history, streaks, FSRS flashcards, exam planner, weak-topic detection, rule-based recommendations, focus mode | Recommendations respect visibility; streak timezone tests; events survive offline |
| 7 Resources | Resource model, submission + approval, search, save, share, recommend, discuss | Moderation on submissions; no commerce surface |
| 8 Engagement | Achievements, points ledger, contributor levels, tasks, leaderboards (opt-in), weekly contests, mock-interview data model only | Leaderboards exclude minors by default; no company features |
| 9 Hardening | Security audit (external if possible), k6 load, query analysis, index review, Redis review, S3 policy review, offline chaos tests, accessibility audit, error/empty states review, runbooks, on-call, restore drill | SLOs met for 7 days in sandbox under load; audit findings closed |

Each phase ends with a `docs/releases/phase-N.md` listing what shipped, test evidence, known gaps and the GraphQL schema version.

## 19. Definition of done and agent coordination

A feature is done when a user can complete it end-to-end on every platform in scope, it cannot be misused, and the next engineer can understand it without asking. A screen alone is not a feature.

**Checklist for every feature:**

- [ ] GraphQL schema change documented in `docs/api-changes/<date>-<name>.md` (what, why, input, output, authorization, breaking or not, migration) and reviewed by the consuming agents
- [ ] Prisma migration with indexes, reviewed, reversible where practical
- [ ] Backend: service + domain logic + `PolicyService` rule + Zod validation + typed error codes
- [ ] Async work: queue, idempotent worker, retry, `JobStatus`, DLQ alert
- [ ] Learning events emitted where relevant (section 14.1 enum, not ad-hoc strings)
- [ ] Web and/or mobile UI with loading, empty, error and offline states; accessibility labels
- [ ] Unit, integration and (for critical paths) E2E tests; security suite extended if permissions changed
- [ ] Observability: span names, metric or log line that lets you see the feature working in production
- [ ] Feature flag if the feature is user-visible and not yet complete across platforms
- [ ] Documentation: ADR for any decision, README section for any new module, runbook if operations change

**Coordination protocol.** Before implementing: read this document, the current `schema.graphql`, the domain model and the permission matrix. The Backend agent lands the schema and migration first; the Web and Mobile agents build against the generated types, using schema mocks (MSW) until the real resolvers land. No agent edits another agent's app directory except through a reviewed PR. Disagreements are settled by an ADR, not by divergent code. Every PR description states which section of this document it implements.

**Ownership summary.**

| Owns | Backend | Web | Mobile |
| --- | --- | --- | --- |
| Business rules, auth, authorization, data, jobs, AI, search, storage, notifications delivery | ✓ | – | – |
| Next.js app, editor, teacher and group-admin UI, SEO pages, web state and tests | – | ✓ | – |
| Expo app, navigation, offline sync client, push handling, media capture, mobile tests | – | – | ✓ |
| `@lvn/contracts/validation`, `@lvn/contracts/domain` | ✓ (proposes) | reviews | reviews |
| `@lvn/contracts` (generated) | ✓ | consumes | consumes |
| Infra, CI/CD, Terraform | ✓ | web pipeline steps | mobile EAS steps |

## 20. Final instruction to all agents

Architect → model → implement → test → review → optimise → document → next phase. Do not start Phase 1 code before Phase 0 documents exist and agree.

Never:

- Build organization, college, company or platform-admin registration or dashboards in the student app
- Implement company recruitment, payments or e-commerce
- Duplicate business logic in a client, or invent a client-specific API
- Call an AI provider, S3 or Redis from web or mobile
- Hardcode a URL, key or environment value, or commit a secret
- Store a file in Postgres or a record of truth in Redis
- Write an S3 object without a `FileObject` row, or hand a client a raw S3 key
- Let private content reach another user through GraphQL, search, recommendations, file URLs, subscriptions, SEO pages or AI
- Lose a draft, an offline edit or a queued upload
- Ship a screen without its backend, tests, states and documentation
- Skip a phase, or leave the application un-buildable at the end of one

The student experience stays simple: discover → learn → create → share → practise → improve → repeat. The architecture exists to make that loop fast, safe and scalable; nothing in this document is an end in itself.

> **LearnViaNotes — a student-first learning community where knowledge is created, shared, discovered, practised and continuously improved.**
