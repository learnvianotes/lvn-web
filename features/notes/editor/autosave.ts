'use client'

import type { JSONContent } from '@tiptap/core'
import { useCallback, useEffect, useRef, useState } from 'react'
import { docToCards } from '../model/doc'
import { afterSave, planSave, type CardOp, type OpResult, type SavedState } from '../model/save'
import { removeMirror, toMirror, writeMirror } from './mirror'

export type SaveStatus = 'saved' | 'pending' | 'saving' | 'offline' | 'error'

export interface SaveResponse {
  results: OpResult[]
  conflictVersionId: string | null
  userErrors: { message: string }[]
}

/** Sends one save to the API; throws when the network or the server failed (the save is retried). */
export type SendSave = (input: { noteId: string; title?: string; ops: CardOp[] }) => Promise<SaveResponse>

const QUIET_MS = 2_000
const RETRY_MS = [5_000, 15_000, 30_000, 60_000]

/**
 * Autosave (lvn-backend §4.3, §12.2): after 2 s without typing the changes go to the API as one `updateNoteDraft`;
 * every change is mirrored to IndexedDB first and the mirror is removed once the server has everything. One save at a
 * time; a failed save is retried with backoff and when the browser comes back online; leaving the page saves at once.
 */
export function useAutosave({ userId, noteId, saved: initial, send }: { userId: string; noteId: string; saved: SavedState; send: SendSave }) {
  const saved = useRef(initial)
  const latest = useRef<{ title: string; doc: JSONContent } | null>(null)
  const dirty = useRef(false)
  const busy = useRef(false)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const attempt = useRef(0)
  const [status, setStatus] = useState<SaveStatus>('saved')
  const [problem, setProblem] = useState<string | null>(null)
  const [conflictVersionId, setConflictVersionId] = useState<string | null>(null)
  const [refused, setRefused] = useState(0)

  const schedule = useCallback((ms: number, run: () => void) => {
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(run, ms)
  }, [])

  const flush = useCallback(async (): Promise<void> => {
    if (busy.current || !latest.current) return
    if (timer.current) clearTimeout(timer.current)
    const { title, doc } = latest.current
    const plan = planSave(saved.current, title, docToCards(doc))
    dirty.current = false
    setProblem(plan.invalid.length ? plan.invalid[0]!.message : null)
    if (!plan.ops.length && plan.title === undefined) {
      if (!plan.invalid.length) await removeMirror(userId, noteId)
      setStatus(plan.invalid.length ? 'error' : 'saved')
      return
    }
    busy.current = true
    setStatus('saving')
    try {
      const res = await send({ noteId, ...(plan.title !== undefined ? { title: plan.title } : {}), ops: plan.ops })
      attempt.current = 0
      if (res.userErrors.length) {
        setProblem(res.userErrors[0]!.message)
        setStatus('error')
        return
      }
      saved.current = afterSave(plan, res.results)
      if (res.conflictVersionId) setConflictVersionId(res.conflictVersionId)
      if (res.results.some((r) => r.status === 'REJECTED')) setRefused((n) => n + 1)
      if (dirty.current) {
        await writeMirror(userId, noteId, toMirror(latest.current!.title, latest.current!.doc, saved.current))
        setStatus('pending')
        schedule(0, () => void flush())
      } else {
        await removeMirror(userId, noteId)
        setStatus(plan.invalid.length ? 'error' : 'saved')
      }
    } catch {
      // Offline or the server failed: the mirror has every change; try again later.
      dirty.current = true
      setStatus('offline')
      const wait = RETRY_MS[Math.min(attempt.current++, RETRY_MS.length - 1)]!
      schedule(wait, () => void flush())
    } finally {
      busy.current = false
    }
  }, [noteId, schedule, send, userId])

  /** Call on every change of the title or the document. */
  const changed = useCallback(
    (title: string, doc: JSONContent) => {
      latest.current = { title, doc }
      dirty.current = true
      setStatus((s) => (s === 'offline' ? s : 'pending'))
      void writeMirror(userId, noteId, toMirror(title, doc, saved.current))
      if (!busy.current) schedule(QUIET_MS, () => void flush())
    },
    [flush, noteId, schedule, userId],
  )

  useEffect(() => {
    const online = () => void flush()
    const hidden = () => document.visibilityState === 'hidden' && void flush()
    window.addEventListener('online', online)
    document.addEventListener('visibilitychange', hidden)
    return () => {
      window.removeEventListener('online', online)
      document.removeEventListener('visibilitychange', hidden)
      if (timer.current) clearTimeout(timer.current)
      void flush()
    }
  }, [flush])

  return { status, problem, conflictVersionId, refused, changed, flush, dismissConflict: () => setConflictVersionId(null) }
}
