'use client'

import { useCallback } from 'react'
import { ReadAloudControls } from '@/features/notes/ReadAloudControls'
import { useReadAloud, type SpokenCard } from '@/features/notes/readAloud'

/** Read aloud on a public page: the words were extracted on the server. */
export function PublicReadAloud({ cards }: { cards: SpokenCard[] }) {
  const spoken = useCallback(() => cards, [cards])
  return <ReadAloudControls reader={useReadAloud(spoken)} />
}
