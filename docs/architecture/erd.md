# Entity-relationship diagram

Derived from [section 4](lvn-architecture-v2.md#4-domain-model) and the context ownership in
[section 6.1](lvn-architecture-v2.md#61-bounded-contexts). Owned by lvn-backend; this is the Phase 0 draft for sign-off.

Rules the diagram obeys: every id is UUIDv7; relationships **inside** a context are foreign keys; references
**across** contexts (dashed in the notes below) are plain UUID columns with a local read model, never a foreign key.

## users (schema `users`)

```mermaid
erDiagram
  User ||--o{ Session : has
  User ||--o{ OAuthAccount : links
  User ||--o{ DeviceToken : registers
  User ||--o{ Membership : "belongs to"
  Organization ||--o{ Membership : has
  User ||--o{ ConsentRecord : accepts
  User ||--o{ AuditLog : "acts in"

  User {
    uuid id PK
    citext email UK
    text handle UK
    text passwordHash "Argon2id, nullable for OAuth-only"
    timestamptz emailVerifiedAt
    date dateOfBirth
    enum globalRole "STUDENT | TEACHER | PLATFORM_ADMIN"
    timestamptz deletionRequestedAt
    timestamptz deletedAt
  }
  Session {
    uuid id PK
    uuid userId FK
    uuid familyId "reuse of a rotated token revokes the family"
    bytea refreshTokenHash "SHA-256"
    jsonb device
    timestamptz expiresAt
    timestamptz revokedAt
  }
  OAuthAccount {
    uuid id PK
    uuid userId FK
    enum provider "GOOGLE | GITHUB | LINKEDIN"
    text providerUserId
    bytea encryptedRefreshToken
  }
  DeviceToken {
    uuid id PK
    uuid userId FK
    text fcmToken UK
    enum platform
    timestamptz lastSeenAt
  }
  Organization {
    uuid id PK "read model from the admin app"
    text name
  }
  Membership {
    uuid userId FK
    uuid organizationId FK
    enum role "ORG_ADMIN | TEACHER | STUDENT"
  }
  ConsentRecord {
    uuid id PK
    uuid userId FK
    enum document "TERMS | PRIVACY | PUBLIC_LICENCE"
    text version
    timestamptz acceptedAt
  }
  AuditLog {
    uuid id PK
    uuid actorId
    text action
    text entityType
    uuid entityId
    jsonb diff "never note content"
    timestamptz at
  }
```

## notes (schema `notes`)

```mermaid
erDiagram
  Subject ||--o{ Topic : contains
  Topic ||--o{ Topic : parent
  Note ||--o{ Card : "ordered blocks"
  Note ||--o{ NoteVersion : snapshots
  Note ||--o{ NoteShare : "user grants"
  Note ||--o{ GroupShare : "shared to group"
  Note ||--o{ ClassroomShare : "shared to class"
  Note ||--o{ NoteTopic : tagged
  Topic ||--o{ NoteTopic : ""
  Folder ||--o{ Note : holds
  Folder ||--o{ Folder : parent
  Note ||--o{ NoteTag : ""
  Tag ||--o{ NoteTag : ""
  Note ||--o{ Attachment : ""
  Attachment }o--|| FileObject : ""
  Note |o--o{ Note : "forkedFrom"

  Subject {
    uuid id PK
    text slug UK
    text title
  }
  Topic {
    uuid id PK
    uuid subjectId FK
    uuid parentId FK
    text slug
    enum origin "CURATED | PROPOSED"
  }
  Note {
    uuid id PK
    uuid ownerId "→ users.User"
    uuid folderId FK
    text title
    text slug
    enum visibility "PRIVATE | SHARED | PUBLIC"
    enum moderationState "OK | PENDING_REVIEW | HIDDEN"
    int draftRevision
    uuid publishedVersionId FK
    timestamptz publishedAt
    bool forkingEnabled
    uuid forkedFromNoteId FK
    uuid forkedFromVersionId FK
    timestamptz deletedAt
  }
  Card {
    uuid id PK
    uuid noteId FK
    text position "fractional index"
    enum type "text … flashcard (16 types)"
    jsonb content "Tiptap JSON, Zod-validated per type"
    int revision
    timestamptz deletedAt
  }
  NoteVersion {
    uuid id PK
    uuid noteId FK
    int number
    jsonb cards "full snapshot"
    enum kind "PUBLISHED | CONFLICT"
    timestamptz createdAt
  }
  NoteShare {
    uuid noteId FK
    uuid userId "→ users.User"
    enum role "EDITOR | VIEWER"
  }
  GroupShare {
    uuid noteId FK
    uuid groupId "→ core.Group"
  }
  ClassroomShare {
    uuid noteId FK
    uuid classroomId "→ core.Classroom"
  }
  Folder {
    uuid id PK
    uuid ownerId
    uuid parentId FK
    text name
  }
  Tag {
    uuid id PK
    uuid ownerId
    text name
  }
  FileObject {
    uuid id PK
    uuid ownerId
    enum parentType
    uuid parentId
    enum purpose
    text storageKey
    enum status "PENDING … DELETED"
    text checksumSha256
    bigint sizeBytes
  }
  Attachment {
    uuid id PK
    uuid noteId FK
    uuid cardId FK
    uuid fileId FK
  }
```

Read models kept by `notes`: `membership_read_model(userId, groupId | classroomId)` for `visibleNotesWhere`.

## core (schema `core`)

```mermaid
erDiagram
  Group ||--o{ GroupMember : ""
  Group ||--o{ GroupPost : ""
  Classroom ||--o{ ClassroomMember : ""
  Quiz ||--o{ Question : ""
  Question ||--o{ Choice : ""
  Quiz ||--o{ QuizAttempt : ""
  QuizAttempt ||--o{ Answer : ""
  FlashcardDeck ||--o{ Flashcard : ""
  Flashcard ||--o{ FlashcardReview : "FSRS state per user"
  Resource ||--o{ ResourceSave : ""
  Resource ||--o{ ResourceRecommendation : ""
  Achievement ||--o{ UserAchievement : ""
  Report ||--o{ ModerationAction : ""

  Group {
    uuid id PK
    text name
    enum privacy "PUBLIC | PRIVATE"
    timestamptz deletedAt
  }
  GroupMember {
    uuid groupId FK
    uuid userId
    enum role "OWNER | ADMIN | MODERATOR | MEMBER"
    timestamptz mutedUntil
  }
  Classroom {
    uuid id PK
    uuid organizationId
    text name
    text joinCode UK
    timestamptz deletedAt
  }
  ClassroomMember {
    uuid classroomId FK
    uuid userId
    enum role "TEACHER | TA | STUDENT"
  }
  Quiz {
    uuid id PK
    uuid ownerId
    uuid classroomId
    uuid sourceNoteVersionId
    timestamptz publishedAt
    timestamptz deletedAt
  }
  QuizAttempt {
    uuid id PK
    uuid quizId FK
    uuid userId
    uuid clientOpId UK
  }
  FlashcardReview {
    uuid flashcardId FK
    uuid userId
    jsonb fsrsState
    timestamptz dueAt
    uuid clientOpId UK
  }
  Exam {
    uuid id PK
    uuid userId
    text name
    date examDate
    uuid_array topicIds
  }
  LearningEvent {
    uuid id PK
    uuid userId
    enum type
    text entityType
    uuid entityId
    int durationMs
    timestamptz serverTs "partition key, monthly"
  }
  Recommendation {
    uuid userId
    enum kind
    uuid entityId
    float score
    text reason
    timestamptz expiresAt
  }
  Resource {
    uuid id PK
    enum type
    text url
    uuid submittedById
    enum status "PENDING | APPROVED | REJECTED"
  }
  Comment {
    uuid id PK
    enum targetType "NOTE | CARD | RESOURCE | GROUP_POST"
    uuid targetId
    uuid authorId
    timestamptz deletedAt
  }
  Report {
    uuid id PK
    text entityType
    uuid entityId
    uuid reporterId
    enum reason
    enum status
  }
  ModerationAction {
    uuid id PK
    uuid reportId FK
    uuid actorId
    enum action "hide | remove | warn | suspend | dismiss"
  }
```

Also in `core`: `Streak`, `PointsLedger`, `Reaction`, `JobStatus` (per context that runs jobs).

## ai (schema `ai`) and communication (schema `comms`)

```mermaid
erDiagram
  NoteChunk {
    uuid id PK
    uuid noteId
    uuid versionId
    uuid cardId
    int position
    text text
    vector embedding "pgvector, 1536"
  }
  NoteArtifact {
    uuid id PK
    uuid noteId
    uuid versionId
    enum type "SUMMARY | CONCEPTS | QUESTIONS | QUIZ | FLASHCARDS | TRANSCRIPT"
    enum status
    jsonb payload
    bool hiddenByOwner
  }
  AiUsage {
    uuid id PK
    uuid userId
    text task
    text model
    int promptTokens
    int completionTokens
    bigint costMicroUsd
    int latencyMs
  }
  AiModelRoute {
    text task PK
    text provider
    text model
  }
  Notification {
    uuid id PK
    uuid userId
    enum category
    jsonb payload "ids only"
    timestamptz readAt
  }
  NotificationPreference {
    uuid userId
    enum category
    bool push
    bool email
    time quietStart
    time quietEnd
  }
```

Shared infrastructure tables, one per schema that needs them: `outbox` (transactional outbox, §9.1) and
`feature_flag` (in `users`, read via GraphQL).
