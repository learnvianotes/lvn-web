// Copied from lvn-backend contracts/src/domain/usage-events.ts by scripts/contracts-sync.mjs — do not edit here.
/**
 * First-party usage events (ADR-0107, extending the B9 allow-list): the names `ingestAnalytics` accepts and the fixed
 * values their props may carry. Web and mobile send these; the API refuses any other name and drops props it does not
 * know. No free text: a search sends its scope and word count, never the words.
 */

/** Every event name the ingest accepts. Anything else is refused. */
export const UsageEventName = {
  PAGE_VIEW: 'page_view',
  NOTE_OPEN: 'note_open',
  NOTE_UPLOAD: 'note_upload',
  SEARCH: 'search',
  DOWNLOAD: 'download',
  SIGN_IN: 'sign_in',
  /** Someone used a product area: props `{ feature: UsageFeature }`. */
  FEATURE_USE: 'feature_use',
  /** A search that found nothing, sent besides its `search`: props `{ scope: UsageSearchScope, wordCount }`. */
  SEARCH_NO_RESULTS: 'search_no_results',
  /** Someone started a quiz: props `{ kind: QuizStartKind }`. */
  QUIZ_START: 'quiz_start',
} as const
export type UsageEventName = (typeof UsageEventName)[keyof typeof UsageEventName]
export const USAGE_EVENT_NAMES = Object.values(UsageEventName) as readonly UsageEventName[]

const EVENT_NAMES: ReadonlySet<string> = new Set(USAGE_EVENT_NAMES)
export const isUsageEventName = (name: string): name is UsageEventName => EVENT_NAMES.has(name)

/**
 * Product areas a `feature_use` event can name. One id per area people open or act in, on web and mobile alike; send
 * it once per visit or action, not per keystroke. Add an id here (and to the GraphQL enum UsageFeature, upper case)
 * before a client sends it: the API refuses ids it does not know.
 */
export const UsageFeature = {
  /** The note editor (cards). */
  NOTES_EDITOR: 'notes_editor',
  /** Handwritten / drawn pages. */
  PAGE_EDITOR: 'page_editor',
  /** The PDF reader and its highlights. */
  PDF_VIEWER: 'pdf_viewer',
  /** Recording a voice note. */
  VOICE_NOTE: 'voice_note',
  /** Quick capture from photos and PDFs. */
  QUICK_CAPTURE: 'quick_capture',
  /** Read aloud. */
  READ_ALOUD: 'read_aloud',
  /** A classroom quiz. */
  CLASS_QUIZ: 'class_quiz',
  /** A shared or public quiz. */
  SHARED_QUIZ: 'shared_quiz',
  /** Flashcard reviews. */
  FLASHCARDS_REVIEW: 'flashcards_review',
  /** Exams and their study plan. */
  EXAM_PLAN: 'exam_plan',
  /** Focus sessions. */
  FOCUS: 'focus',
  GROUPS: 'groups',
  CLASSROOM: 'classroom',
  /** Doubts in groups and project workspaces. */
  DOUBTS: 'doubts',
  /** Ask AI, study aids and other AI actions. */
  AI_ASSIST: 'ai_assist',
  RESOURCES: 'resources',
  SEARCH: 'search',
  PROFILE: 'profile',
  SETTINGS: 'settings',
} as const
export type UsageFeature = (typeof UsageFeature)[keyof typeof UsageFeature]
export const USAGE_FEATURES = Object.values(UsageFeature) as readonly UsageFeature[]

/** Where a search was made: one of the API's search scopes, or `all` for a search across every scope. */
export const UsageSearchScope = {
  ALL: 'all',
  NOTES: 'notes',
  PEOPLE: 'people',
  GROUPS: 'groups',
  CLASSROOMS: 'classrooms',
  RESOURCES: 'resources',
  TOPICS: 'topics',
} as const
export type UsageSearchScope = (typeof UsageSearchScope)[keyof typeof UsageSearchScope]
export const USAGE_SEARCH_SCOPES = Object.values(UsageSearchScope) as readonly UsageSearchScope[]

/** What kind of quiz a `quiz_start` event started. */
export const QuizStartKind = {
  /** A classroom quiz (ClassQuiz). */
  CLASS: 'class',
  /** A shared or public quiz (SharedQuiz). */
  SHARED: 'shared',
  /** The quiz cards of a note. */
  NOTE: 'note',
  /** Practice questions: AI-made, or a topic's quiz. */
  PRACTICE: 'practice',
} as const
export type QuizStartKind = (typeof QuizStartKind)[keyof typeof QuizStartKind]
export const QUIZ_START_KINDS = Object.values(QuizStartKind) as readonly QuizStartKind[]

/** Limits on usage events. The clients keep within them; the API refuses a batch or props past them. */
export const USAGE_EVENT_LIMITS = {
  /** Events plus errors in one `ingestAnalytics` call */
  batch: 40,
  /** `props` as JSON, in characters */
  propsChars: 1_024,
  /** Keys in `props` */
  propsKeys: 16,
  /** A prop key: a letter, then letters, digits or `_` */
  keyChars: 32,
  /** A prop string value of the older events: a short token without spaces */
  tokenChars: 40,
  /** A larger prop number is dropped */
  maxNumber: 1_000_000_000,
  /** `wordCount` is capped here: 20 means 20 or more words */
  wordCountCap: 20,
  /** `appVersion`, after a leading `v` is dropped */
  appVersionChars: 32,
  sessionIdChars: 64,
  /** Days a usage event is kept */
  retentionDays: 180,
} as const
