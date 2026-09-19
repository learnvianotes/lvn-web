/* ============================================================
   C-NOTE COMMON TYPES
   Shared utility types used across the application.
   ============================================================ */

/** Makes specific fields of T required */
export type Require<T, K extends keyof T> = T & Required<Pick<T, K>>

/** Makes all fields of T optional */
export type Maybe<T> = T | null | undefined

/** ISO 8601 date string */
export type ISODateString = string

/** A non-empty string (semantic alias) */
export type NonEmptyString = string

/** Slug — URL-safe identifier */
export type Slug = string
