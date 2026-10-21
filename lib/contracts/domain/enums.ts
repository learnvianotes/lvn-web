// Copied from lvn-backend contracts/src/domain/enums.ts by scripts/contracts-sync.mjs — do not edit here.
/**
 * Domain enums shared by lvn-backend, lvn-web and lvn-mobile (spec §4, §5, §8, §9, §14).
 * Defined as const objects so they work as runtime values, TypeScript unions and Zod enums.
 */

const values = <T extends Record<string, string>>(o: T) => Object.values(o) as [T[keyof T], ...T[keyof T][]]

export const Visibility = { PRIVATE: 'PRIVATE', SHARED: 'SHARED', PUBLIC: 'PUBLIC' } as const
export type Visibility = (typeof Visibility)[keyof typeof Visibility]

export const GlobalRole = { STUDENT: 'STUDENT', TEACHER: 'TEACHER', PLATFORM_ADMIN: 'PLATFORM_ADMIN' } as const
export type GlobalRole = (typeof GlobalRole)[keyof typeof GlobalRole]

/** MENTOR exists only in PROJECT groups: a teacher the team invited (ADR-0015). */
export const GroupRole = { OWNER: 'GROUP_OWNER', ADMIN: 'GROUP_ADMIN', MODERATOR: 'GROUP_MODERATOR', MEMBER: 'GROUP_MEMBER', MENTOR: 'GROUP_MENTOR' } as const
export type GroupRole = (typeof GroupRole)[keyof typeof GroupRole]

export const ClassroomRole = { TEACHER: 'CLASSROOM_TEACHER', TA: 'CLASSROOM_TA', STUDENT: 'CLASSROOM_STUDENT' } as const
export type ClassroomRole = (typeof ClassroomRole)[keyof typeof ClassroomRole]

export const OrgRole = { ADMIN: 'ORG_ADMIN' } as const
export type OrgRole = (typeof OrgRole)[keyof typeof OrgRole]

/** Note-level grant on a NoteShare row. OWNER is implied by Note.ownerId, never stored as a share. */
export const NoteRole = { OWNER: 'OWNER', EDITOR: 'EDITOR', VIEWER: 'VIEWER' } as const
export type NoteRole = (typeof NoteRole)[keyof typeof NoteRole]

export const CardType = {
  TEXT: 'text', HEADING: 'heading', MARKDOWN: 'markdown', CODE: 'code', IMAGE: 'image', VIDEO: 'video',
  AUDIO: 'audio', FILE: 'file', DIAGRAM: 'diagram', QUOTE: 'quote', CALLOUT: 'callout', CHECKLIST: 'checklist',
  TABLE: 'table', QUESTION: 'question', QUIZ: 'quiz', FLASHCARD: 'flashcard',
} as const
export type CardType = (typeof CardType)[keyof typeof CardType]

/** A highlight in the PDF reader (ADR-0040): a passage of text, or an area of a page such as a figure. */
export const HighlightKind = { TEXT: 'TEXT', AREA: 'AREA' } as const
export type HighlightKind = (typeof HighlightKind)[keyof typeof HighlightKind]

export const HighlightColor = { YELLOW: 'YELLOW', GREEN: 'GREEN', BLUE: 'BLUE', PINK: 'PINK', PURPLE: 'PURPLE' } as const
export type HighlightColor = (typeof HighlightColor)[keyof typeof HighlightColor]

/**
 * What a note is presented as (ADR-0014, ADR-0015). Every kind is a Note — same editor, versions, visibility,
 * moderation, search and permissions. Anyone writes NOTE and PROJECT; BLOG and POST are teacher publications.
 */
export const NoteKind = { NOTE: 'NOTE', BLOG: 'BLOG', POST: 'POST', PROJECT: 'PROJECT' } as const
export type NoteKind = (typeof NoteKind)[keyof typeof NoteKind]

/**
 * PUBLISHED: what readers see (§4.3). CONFLICT: the losing side of a card edited on two devices (§13.2).
 * DRAFT: the draft as it was before a version was restored, so restoring never loses unpublished work (§4.3).
 */
export const NoteVersionKind = { PUBLISHED: 'PUBLISHED', CONFLICT: 'CONFLICT', DRAFT: 'DRAFT' } as const
export type NoteVersionKind = (typeof NoteVersionKind)[keyof typeof NoteVersionKind]

/** A request to join a group or classroom (ADR-0009). */
export const JoinRequestStatus = { PENDING: 'PENDING', APPROVED: 'APPROVED', REJECTED: 'REJECTED', WITHDRAWN: 'WITHDRAWN' } as const
export type JoinRequestStatus = (typeof JoinRequestStatus)[keyof typeof JoinRequestStatus]

/** COMMUNITY: a study group. PROJECT: a team workspace with a linked repository, ideas, doubts and a mentor (ADR-0015). */
export const GroupType = { COMMUNITY: 'COMMUNITY', PROJECT: 'PROJECT' } as const
export type GroupType = (typeof GroupType)[keyof typeof GroupType]

/** Posts in a group; IDEA posts make up a project workspace's ideas board (ADR-0015). */
export const GroupPostKind = { POST: 'POST', IDEA: 'IDEA' } as const
export type GroupPostKind = (typeof GroupPostKind)[keyof typeof GroupPostKind]

/** A question a project team asks; the mentor or a teammate answers it (ADR-0015). */
export const DoubtStatus = { OPEN: 'OPEN', ANSWERED: 'ANSWERED', RESOLVED: 'RESOLVED' } as const
export type DoubtStatus = (typeof DoubtStatus)[keyof typeof DoubtStatus]

export const GroupPrivacy = { PUBLIC: 'PUBLIC', PRIVATE: 'PRIVATE' } as const
export type GroupPrivacy = (typeof GroupPrivacy)[keyof typeof GroupPrivacy]

/** How people join a group (ADR-0011). Only a PUBLIC group can be OPEN; a PRIVATE group always uses APPROVAL. */
export const GroupJoinPolicy = { OPEN: 'OPEN', APPROVAL: 'APPROVAL' } as const
export type GroupJoinPolicy = (typeof GroupJoinPolicy)[keyof typeof GroupJoinPolicy]

export const ModerationState = { OK: 'OK', PENDING_REVIEW: 'PENDING_REVIEW', HIDDEN: 'HIDDEN', REMOVED: 'REMOVED' } as const
export type ModerationState = (typeof ModerationState)[keyof typeof ModerationState]

/** GraphQL `extensions.code` values (§6.2). Nothing else reaches clients. */
export const ErrorCode = {
  UNAUTHENTICATED: 'UNAUTHENTICATED', FORBIDDEN: 'FORBIDDEN', NOT_FOUND: 'NOT_FOUND', VALIDATION: 'VALIDATION',
  CONFLICT: 'CONFLICT', RATE_LIMITED: 'RATE_LIMITED', INTERNAL: 'INTERNAL',
  /** A service the request needs is off or out of budget for now (AI, ADR-0058); worth trying later */
  UNAVAILABLE: 'UNAVAILABLE',
  /** Sign-up refused: the date of birth given is below ACCOUNT_MINIMUM_AGE (ADR-0091) */
  UNDER_MINIMUM_AGE: 'UNDER_MINIMUM_AGE',
} as const
export type ErrorCode = (typeof ErrorCode)[keyof typeof ErrorCode]

export const AuthProvider = { PASSWORD: 'PASSWORD', GOOGLE: 'GOOGLE', GITHUB: 'GITHUB', LINKEDIN: 'LINKEDIN' } as const
export type AuthProvider = (typeof AuthProvider)[keyof typeof AuthProvider]

export const FileStatus = {
  PENDING: 'PENDING', UPLOADED: 'UPLOADED', PROCESSING: 'PROCESSING', READY: 'READY', FAILED: 'FAILED',
  QUARANTINED: 'QUARANTINED', DELETED: 'DELETED',
} as const
export type FileStatus = (typeof FileStatus)[keyof typeof FileStatus]

export const FileParentType = { NOTE: 'NOTE', CARD: 'CARD', GROUP_POST: 'GROUP_POST', RESOURCE: 'RESOURCE', AVATAR: 'AVATAR', VERIFICATION_REQUEST: 'VERIFICATION_REQUEST' } as const
export type FileParentType = (typeof FileParentType)[keyof typeof FileParentType]

/**
 * IMPORT: a file to import notes from; EXPORT: a generated data export (ADR-0018). VERIFICATION_DOCUMENT: proof
 * of enrolment sent to platform admins, kept in a restricted prefix and deleted 30 days after the decision
 * (ADR-0019). All three are temporary.
 */
export const FilePurpose = { ATTACHMENT: 'ATTACHMENT', COVER: 'COVER', VOICE_NOTE: 'VOICE_NOTE', AVATAR: 'AVATAR', IMPORT: 'IMPORT', EXPORT: 'EXPORT', VERIFICATION_DOCUMENT: 'VERIFICATION_DOCUMENT' } as const
export type FilePurpose = (typeof FilePurpose)[keyof typeof FilePurpose]

/** Upload limits in bytes (§8.1), enforced server-side; clients use them for early feedback only. */
export const UploadLimits = {
  image: 20 * 1024 ** 2,
  audio: 100 * 1024 ** 2,
  video: 500 * 1024 ** 2,
  document: 50 * 1024 ** 2,
  quotaStudent: 5 * 1024 ** 3,
  quotaTeacher: 20 * 1024 ** 3,
} as const

/**
 * Notes made by AI from photos and PDFs (ADR-0084): the most a quick note reads, photos and PDFs together, and the
 * largest PDF the apps add to one. Pictures are made smaller on the device first (at most `pictureSide` pixels on the
 * longer side, as JPEG), so they upload quickly; the server's own limits stay as UploadLimits.
 */
export const QuickNoteLimits = {
  files: 10,
  pdfBytes: 20 * 1024 ** 2,
  pictureSide: 2048,
} as const

export const NoteArtifactType = {
  SUMMARY: 'SUMMARY', KEY_CONCEPTS: 'KEY_CONCEPTS', QUESTIONS: 'QUESTIONS', QUIZ: 'QUIZ', FLASHCARDS: 'FLASHCARDS',
  EMBEDDINGS: 'EMBEDDINGS', TRANSCRIPT: 'TRANSCRIPT',
} as const
export type NoteArtifactType = (typeof NoteArtifactType)[keyof typeof NoteArtifactType]

/** How an account became verified (ADR-0017, ADR-0019). */
export const VerificationMethod = { INSTITUTIONAL_EMAIL: 'INSTITUTIONAL_EMAIL', TEACHER: 'TEACHER', DOCUMENTS: 'DOCUMENTS' } as const
export type VerificationMethod = (typeof VerificationMethod)[keyof typeof VerificationMethod]

/** The old learnvianotes.in data waiting for its owner (ADR-0023). */
export const LegacyImportStatus = { NOT_FOUND: 'NOT_FOUND', AVAILABLE: 'AVAILABLE', CLAIMED: 'CLAIMED', DECLINED: 'DECLINED' } as const
export type LegacyImportStatus = (typeof LegacyImportStatus)[keyof typeof LegacyImportStatus]

/**
 * Every usage limit, read from the user's (or organisation's) plan — never written in code (ADR-0024). Only the
 * FREE plan exists today; paid plans and organisation seat limits come later without code changes.
 */
export const LimitKey = {
  STORAGE_BYTES: 'STORAGE_BYTES', AI_TOKENS_DAILY: 'AI_TOKENS_DAILY', PDF_PAGES_MONTHLY: 'PDF_PAGES_MONTHLY',
  GROUPS_OWNED: 'GROUPS_OWNED', GROUP_MEMBERS: 'GROUP_MEMBERS', CLASSROOMS_OWNED: 'CLASSROOMS_OWNED',
  CLASSROOM_MEMBERS: 'CLASSROOM_MEMBERS', PROJECT_WORKSPACES: 'PROJECT_WORKSPACES', EXPORTS_DAILY: 'EXPORTS_DAILY',
  IMPORTS_DAILY: 'IMPORTS_DAILY', ORG_SEATS: 'ORG_SEATS',
} as const
export type LimitKey = (typeof LimitKey)[keyof typeof LimitKey]

/**
 * AI tasks a user runs on something they can read (ADR-0025). Tasks that produce a new note of their own from someone
 * else's content are "derivative" and follow the fork rule; the rest follow the Ask-AI rule.
 */
export const AiTaskType = {
  SUMMARIZE: 'SUMMARIZE', KEY_CONCEPTS: 'KEY_CONCEPTS', EXPLAIN_SIMPLY: 'EXPLAIN_SIMPLY', FLASHCARDS: 'FLASHCARDS',
  QUIZ: 'QUIZ', PRACTICE_QUESTIONS: 'PRACTICE_QUESTIONS', TRANSLATE: 'TRANSLATE', FIND_MISTAKES: 'FIND_MISTAKES',
  CREATE_NOTES: 'CREATE_NOTES', OUTLINE_TO_NOTE: 'OUTLINE_TO_NOTE',
  /** On code cards (§18 "code explanation", ADR-0059) */
  EXPLAIN_CODE: 'EXPLAIN_CODE',
  /** One short page of key points, definitions and formulas (owner, 2026-10-09; ADR-0025) */
  REVISION_SHEET: 'REVISION_SHEET',
  /** What an audio or video card says, as a text card to keep (ADR-0062) */
  TRANSCRIBE: 'TRANSCRIBE',
  /** Rough text and photos of one's own note, as a structured note (ADR-0062) */
  QUICK_NOTE: 'QUICK_NOTE',
  /** What conversion broke in a note's text, mended card by card for the person to apply (ADR-0063) */
  CLEAN_UP: 'CLEAN_UP',
} as const
export type AiTaskType = (typeof AiTaskType)[keyof typeof AiTaskType]
export const DERIVATIVE_AI_TASKS: ReadonlySet<AiTaskType> = new Set([AiTaskType.CREATE_NOTES, AiTaskType.OUTLINE_TO_NOTE])

/**
 * Where Ask AI looks (§10.2, ADR-0060): one note as the asker reads it, their own notes, notes shared with their groups
 * and classes, public notes, or the notes shared with a workspace (a doubt, ADR-0015). Always within what they may read.
 */
export const AskAiScope = { THIS_NOTE: 'THIS_NOTE', MY_NOTES: 'MY_NOTES', MY_PLACES: 'MY_PLACES', PUBLIC: 'PUBLIC', WORKSPACE: 'WORKSPACE' } as const
export type AskAiScope = (typeof AskAiScope)[keyof typeof AskAiScope]

/** Year of study on a student profile (ADR-0026). */
export const YearOfStudy = {
  YEAR_1: 'YEAR_1', YEAR_2: 'YEAR_2', YEAR_3: 'YEAR_3', YEAR_4: 'YEAR_4', YEAR_5: 'YEAR_5',
  POSTGRADUATE: 'POSTGRADUATE', GRADUATED: 'GRADUATED', SCHOOL: 'SCHOOL', NOT_STUDYING: 'NOT_STUDYING',
} as const
export type YearOfStudy = (typeof YearOfStudy)[keyof typeof YearOfStudy]

/** The five bounded contexts (spec §6.1); each contributes its part of a data export (ADR-0018). */
export const BoundedContext = { USERS: 'users', NOTES: 'notes', CORE: 'core', AI: 'ai', COMMUNICATION: 'communication' } as const
export type BoundedContext = (typeof BoundedContext)[keyof typeof BoundedContext]

export const JobState = { QUEUED: 'QUEUED', RUNNING: 'RUNNING', SUCCEEDED: 'SUCCEEDED', FAILED: 'FAILED', DEAD: 'DEAD' } as const
export type JobState = (typeof JobState)[keyof typeof JobState]

/** §14.1 — the only event types clients may send through `trackEvents`. */
export const LearningEventType = {
  NOTE_OPENED: 'NOTE_OPENED', NOTE_CREATED: 'NOTE_CREATED', NOTE_PUBLISHED: 'NOTE_PUBLISHED', NOTE_FORKED: 'NOTE_FORKED',
  CARD_VIEWED: 'CARD_VIEWED', TOPIC_VIEWED: 'TOPIC_VIEWED', VIDEO_STARTED: 'VIDEO_STARTED', VIDEO_COMPLETED: 'VIDEO_COMPLETED',
  QUIZ_STARTED: 'QUIZ_STARTED', QUIZ_COMPLETED: 'QUIZ_COMPLETED', FLASHCARD_REVIEWED: 'FLASHCARD_REVIEWED',
  TIME_SPENT: 'TIME_SPENT', NOTE_SAVED: 'NOTE_SAVED', TOPIC_REVISITED: 'TOPIC_REVISITED', EXAM_CREATED: 'EXAM_CREATED',
  RESOURCE_VIEWED: 'RESOURCE_VIEWED', RESOURCE_SAVED: 'RESOURCE_SAVED', AI_REQUESTED: 'AI_REQUESTED',
  SEARCH_PERFORMED: 'SEARCH_PERFORMED',
  /** Read a /core topic to the end, and marked a /core problem — the old site's progress, carried on (ADR-0023). */
  TOPIC_COMPLETED: 'TOPIC_COMPLETED', PROBLEM_MARKED: 'PROBLEM_MARKED',
} as const
export type LearningEventType = (typeof LearningEventType)[keyof typeof LearningEventType]

/**
 * Events the server records itself, from what it already knows (ADR-0067); `trackEvents` refuses them from clients so
 * nobody can claim a note they never wrote or an exam they never planned. Searches are the apps' to send: the API sees
 * every keystroke of a search box, the apps know when a search was made.
 */
export const SERVER_LEARNING_EVENTS: ReadonlySet<LearningEventType> = new Set([
  LearningEventType.NOTE_CREATED, LearningEventType.NOTE_PUBLISHED, LearningEventType.NOTE_FORKED, LearningEventType.EXAM_CREATED,
  LearningEventType.AI_REQUESTED,
])

/**
 * What a `TIME_SPENT` event's time was (`metadata.activity`, ADR-0067). Only learning actions fill Rhythm (ADR-0030):
 * focus sessions, reviews and quizzes; reading is history only, as passive reading never counts.
 */
export const TimeSpentActivity = { FOCUS: 'FOCUS', REVIEW: 'REVIEW', QUIZ: 'QUIZ', READING: 'READING' } as const
export type TimeSpentActivity = (typeof TimeSpentActivity)[keyof typeof TimeSpentActivity]
export const LEARNING_ACTIVITIES: ReadonlySet<TimeSpentActivity> = new Set([TimeSpentActivity.FOCUS, TimeSpentActivity.REVIEW, TimeSpentActivity.QUIZ])

export const Platform = { WEB: 'WEB', ANDROID: 'ANDROID', IOS: 'IOS' } as const
export type Platform = (typeof Platform)[keyof typeof Platform]

export const ResourceType = { BOOK: 'BOOK', COURSE: 'COURSE', TOOL: 'TOOL', SOFTWARE: 'SOFTWARE', HARDWARE: 'HARDWARE', OTHER: 'OTHER' } as const
export type ResourceType = (typeof ResourceType)[keyof typeof ResourceType]

export const ResourceStatus = { PENDING: 'PENDING', APPROVED: 'APPROVED', REJECTED: 'REJECTED' } as const
export type ResourceStatus = (typeof ResourceStatus)[keyof typeof ResourceStatus]

export const ReportReason = {
  HARASSMENT: 'HARASSMENT', SEXUAL: 'SEXUAL', SELF_HARM: 'SELF_HARM', HATE: 'HATE', SPAM: 'SPAM', COPYRIGHT: 'COPYRIGHT', OTHER: 'OTHER',
} as const
export type ReportReason = (typeof ReportReason)[keyof typeof ReportReason]

/** What can be reported (ADR-0037, ADR-0051); each has a scope that decides whose queue it goes to. */
export const ReportEntityType = { NOTE: 'NOTE', USER: 'USER', COMMENT: 'COMMENT', GROUP_POST: 'GROUP_POST', CLASSROOM_POST: 'CLASSROOM_POST', DOUBT: 'DOUBT', GROUP: 'GROUP', RESOURCE: 'RESOURCE' } as const
export type ReportEntityType = (typeof ReportEntityType)[keyof typeof ReportEntityType]

/** §15.1 actions, plus APPROVE: a held note goes (back) to the public (ADR-0037). */
export const ModerationActionType = { APPROVE: 'APPROVE', HIDE: 'HIDE', REMOVE: 'REMOVE', WARN: 'WARN', SUSPEND: 'SUSPEND', DISMISS: 'DISMISS' } as const
export type ModerationActionType = (typeof ModerationActionType)[keyof typeof ModerationActionType]

export const enumValues = values

/** What a comment is on (ADR-0047): a note (optionally one of its cards), a group post or a class announcement. */
export const CommentTargetType = { NOTE: 'NOTE', GROUP_POST: 'GROUP_POST', CLASSROOM_POST: 'CLASSROOM_POST', RESOURCE: 'RESOURCE' } as const
export type CommentTargetType = (typeof CommentTargetType)[keyof typeof CommentTargetType]

/** What a reaction is on (ADR-0047). */
export const ReactionTargetType = { NOTE: 'NOTE', COMMENT: 'COMMENT', GROUP_POST: 'GROUP_POST', CLASSROOM_POST: 'CLASSROOM_POST' } as const
export type ReactionTargetType = (typeof ReactionTargetType)[keyof typeof ReactionTargetType]

/** One reaction per person per target (ADR-0047). */
export const ReactionKind = { LIKE: 'LIKE', HELPFUL: 'HELPFUL', CELEBRATE: 'CELEBRATE' } as const
export type ReactionKind = (typeof ReactionKind)[keyof typeof ReactionKind]

/** Where a workspace's repository lives (ADR-0048). LVN never hosts git. */
export const RepositoryProvider = { GITHUB: 'GITHUB', GITLAB: 'GITLAB' } as const
export type RepositoryProvider = (typeof RepositoryProvider)[keyof typeof RepositoryProvider]

/** Whose queue a report goes to (ADR-0051): a group's moderators, a class's staff, or the platform's admins. */
export const ModerationScope = { PLATFORM: 'PLATFORM', GROUP: 'GROUP', CLASSROOM: 'CLASSROOM' } as const
export type ModerationScope = (typeof ModerationScope)[keyof typeof ModerationScope]
