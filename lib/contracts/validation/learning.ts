// Copied from lvn-backend contracts/src/validation/learning.ts by scripts/contracts-sync.mjs — do not edit here.
import { z } from 'zod'
import { enumValues, LearningEventType, Platform } from '../domain/enums'

/** Limits on learning events (§14.1, ADR-0067). The clients batch within them; the API refuses what goes past. */
export const LEARNING_LIMITS = {
  /** Events in one `trackEvents` call */
  batch: 100,
  /** Clients send every 10 s, or sooner at this many events */
  flushEvery: 20,
  flushSeconds: 10,
  /** Events a client keeps while offline; past it the oldest go */
  queued: 1_000,
  /** `metadata` as JSON, in bytes */
  metadataBytes: 2_048,
  /** One event's duration */
  durationMs: 4 * 60 * 60 * 1000,
  topicKeys: 10,
  /** A client's clock is believed back this far; older times are set to it */
  pastDays: 30,
} as const

/**
 * A topic an event is about: `topic:<uuid>` (a notes topic) or `core:<subject>/<topic>` (a /core page, ADR-0023).
 * Letters, digits and `_ . / -` after the prefix.
 */
export const topicKeySchema = z.string().regex(/^(topic|core):[A-Za-z0-9_./-]{1,100}$/, 'A topic is topic:<id> or core:<subject>/<topic>')

const jsonBytes = (v: unknown) => new TextEncoder().encode(JSON.stringify(v ?? {})).length

/** One event as a client sends it in `trackEvents` (ADR-0067). `id` is the client's UUIDv7, so a retry counts once. */
export const learningEventInputSchema = z.object({
  id: z.uuid(),
  type: z.enum(enumValues(LearningEventType)),
  entityType: z.string().regex(/^[A-Z_]{1,40}$/, 'An entity type is upper-case letters').nullish(),
  entityId: z.string().min(1).max(100).nullish(),
  topicKeys: z.array(topicKeySchema).max(LEARNING_LIMITS.topicKeys).nullish(),
  durationMs: z.number().int().min(0).max(LEARNING_LIMITS.durationMs).nullish(),
  metadata: z.record(z.string(), z.unknown()).refine((m) => jsonBytes(m) <= LEARNING_LIMITS.metadataBytes, `Metadata is at most ${LEARNING_LIMITS.metadataBytes} bytes`).nullish(),
  clientTs: z.iso.datetime({ offset: true }),
  sessionId: z.string().min(1).max(64).nullish(),
  platform: z.enum(enumValues(Platform)),
})
export type LearningEventInput = z.infer<typeof learningEventInputSchema>

/** An IANA time zone this runtime knows, e.g. Asia/Kolkata. */
export function isTimeZone(zone: string): boolean {
  if (!zone || zone.length > 64) return false
  try {
    new Intl.DateTimeFormat('en', { timeZone: zone })
    return true
  } catch {
    return false
  }
}
