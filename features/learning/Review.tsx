'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { RichDoc } from '@/features/notes/render/RichText'
import { ReviewCardDocument, ReviewQueueDocument, type ReviewQueueQuery, type ReviewRating } from '@/graphql/generated/graphql'
import { newId } from '@/lib/ids'
import type { Doc } from '@/lib/contracts/validation'

type Card = ReviewQueueQuery['reviewQueue']['cards'][number]
type Grade = { cardId: string; rating: ReviewRating; reviewedAt: string; durationMs: number; clientOpId: string }

const RATINGS: ReviewRating[] = ['AGAIN', 'HARD', 'GOOD', 'EASY']
const PENDING = 'lvn.reviews.pending'

const loadPending = (): Grade[] => {
  try {
    return JSON.parse(localStorage.getItem(PENDING) ?? '[]') as Grade[]
  } catch {
    return []
  }
}
const savePending = (grades: Grade[]) => {
  try {
    localStorage.setItem(PENDING, JSON.stringify(grades))
  } catch {
    // Storage blocked: the grades stay in memory for this visit.
  }
}

/**
 * A review session (lvn-backend ADR-0068): today's cards one by one, the front, then the back and four grades
 * (keys 1–4, Space to show the answer). Grading moves on at once; the grade goes to the API behind it, and one that
 * could not go waits in this browser and is sent when the connection returns (each with its own id, so it counts once).
 * A card graded Again comes back at the end of the session.
 */
export function Review() {
  const t = useTranslations('review')
  const { data, loading, error } = useQuery(ReviewQueueDocument, { fetchPolicy: 'network-only' })
  const [send] = useMutation(ReviewCardDocument)
  const [cards, setCards] = useState<Card[] | null>(null)
  const [index, setIndex] = useState(0)
  const [shown, setShown] = useState(false)
  const [done, setDone] = useState(0)
  const [waiting, setWaiting] = useState(0)
  const started = useRef(Date.now())

  useEffect(() => {
    if (data && cards === null) setCards(data.reviewQueue.cards)
  }, [data, cards])

  // One sender at a time; a call while it runs makes it go round once more.
  const sending = useRef<{ again: boolean } | null>(null)
  const flush = useCallback(async () => {
    if (sending.current) {
      sending.current.again = true
      return
    }
    sending.current = { again: false }
    try {
      do {
        sending.current.again = false
        for (const grade of loadPending()) {
          setWaiting(loadPending().length)
          const res = await send({ variables: { input: grade } }).catch(() => null)
          // Kept only when it could not go; a refusal (the card left the deck) will not change by trying again.
          if (!res) return
          savePending(loadPending().filter((g) => g.clientOpId !== grade.clientOpId))
        }
      } while (sending.current.again)
    } finally {
      sending.current = null
      setWaiting(loadPending().length)
    }
  }, [send])

  useEffect(() => {
    void flush()
    const online = () => void flush()
    window.addEventListener('online', online)
    return () => window.removeEventListener('online', online)
  }, [flush])

  const card = cards?.[index]
  const grade = useCallback(
    (rating: ReviewRating) => {
      if (!card || !cards) return
      const g: Grade = { cardId: card.cardId, rating, reviewedAt: new Date().toISOString(), durationMs: Date.now() - started.current, clientOpId: newId() }
      savePending([...loadPending(), g])
      void flush()
      setDone((n) => n + 1)
      // Again: the card comes back at the end of this session.
      if (rating === 'AGAIN') setCards([...cards, card])
      setIndex((i) => i + 1)
      setShown(false)
      started.current = Date.now()
    },
    [card, cards, flush],
  )

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!card || (e.target as HTMLElement | null)?.closest('input, textarea, select, [contenteditable="true"]')) return
      if (!shown && (e.key === ' ' || e.key === 'Enter')) {
        e.preventDefault()
        setShown(true)
      } else if (shown && ['1', '2', '3', '4'].includes(e.key)) grade(RATINGS[Number(e.key) - 1]!)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [card, shown, grade])

  if (error && !data) return <p className="text-muted">{t('failed')}</p>
  if (loading && !cards) return <p className="text-muted">{t('loading')}</p>
  const queue = data?.reviewQueue
  if (!cards?.length) {
    return (
      <section className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border px-6 py-10 text-center">
        <h1 className="text-xl font-bold">{t('nothingTitle')}</h1>
        <p className="text-sm text-muted">{t('nothing')}</p>
        <Link href="/notes" className="text-accent hover:underline">
          {t('toNotes')}
        </Link>
      </section>
    )
  }
  if (!card) {
    return (
      <section className="flex flex-col items-center gap-3 rounded-2xl border border-border bg-surface px-6 py-10 text-center">
        <h1 className="text-xl font-bold">{t('doneTitle')}</h1>
        <p className="text-sm text-muted">{t('done', { count: done })}</p>
        {queue?.waiting ? <p className="text-sm text-muted">{t('later', { count: queue.waiting })}</p> : null}
        {waiting ? <p role="status" className="text-sm text-muted">{t('waitingToSend', { count: waiting })}</p> : null}
      </section>
    )
  }
  return (
    <section aria-label={t('session')} className="flex flex-col gap-4">
      <div className="flex items-center justify-between text-sm text-muted">
        <span>{t('progress', { n: Math.min(index + 1, cards.length), total: cards.length })}</span>
        <Link href={`/notes/${card.noteId}`} className="truncate hover:text-accent">
          {card.noteTitle || t('untitled')}
        </Link>
      </div>
      <article aria-label={t('card')} className="flex min-h-56 flex-col gap-4 rounded-2xl border border-border bg-surface p-6">
        <div aria-label={t('front')}>
          <RichDoc doc={card.front as Doc} />
        </div>
        {shown ? (
          <div aria-label={t('back')} className="border-t border-border pt-4">
            <RichDoc doc={card.back as Doc} />
          </div>
        ) : null}
      </article>
      {shown ? (
        <div role="group" aria-label={t('howWell')} className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {RATINGS.map((r, i) => (
            <Button key={r} variant={r === 'GOOD' ? 'primary' : 'secondary'} onClick={() => grade(r)} aria-keyshortcuts={String(i + 1)}>
              {t(`rating.${r}`)}
            </Button>
          ))}
        </div>
      ) : (
        <Button onClick={() => setShown(true)} aria-keyshortcuts="Space">
          {t('show')}
        </Button>
      )}
      {waiting ? <p role="status" className="text-xs text-muted">{t('waitingToSend', { count: waiting })}</p> : null}
    </section>
  )
}
