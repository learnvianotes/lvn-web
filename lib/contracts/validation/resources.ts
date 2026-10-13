// Copied from lvn-backend contracts/src/validation/resources.ts by scripts/contracts-sync.mjs — do not edit here.
/** Limits on resources (§14.4, ADR-0074). The apps check them as people type; the API refuses what goes past. */
export const RESOURCE_LIMITS = {
  title: { min: 3, max: 200 },
  description: 2_000,
  url: 2_000,
  author: 200,
  topics: { min: 1, max: 5 },
  /** A cover picture, uploaded or copied from the page */
  coverBytes: 2 * 1024 * 1024,
  coverTypes: ['image/jpeg', 'image/png', 'image/webp'],
  /** Submissions a person makes in a day, and how many may wait at once */
  perDay: 10,
  waiting: 20,
  /** A recommendation's reason (ADR-0075) */
  reason: 280,
  /** Recommendations a person sends in an hour */
  recommendationsPerHour: 30,
  /** Previews a person asks for in an hour */
  previewsPerHour: 30,
} as const
