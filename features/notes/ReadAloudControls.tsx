'use client'

import { Pause, Play, Square, Volume2 } from 'lucide-react'
import { useTranslations } from 'next-intl'
import type { useReadAloud } from './readAloud'

/** Play, pause, stop and speed for read aloud (ADR-0025); the editor, the reader and public pages share it. */
export function ReadAloudControls({ reader }: { reader: ReturnType<typeof useReadAloud> }) {
  const t = useTranslations('notes.readAloud')
  if (!reader.supported) return null
  return (
    <div className="flex items-center gap-1 rounded-full border border-border bg-surface p-0.5" role="group" aria-label={t('label')}>
      {reader.state === 'idle' ? (
        <button type="button" className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm hover:bg-surface-2" onClick={() => reader.play()}>
          <Volume2 className="size-4" aria-hidden />
          {t('play')}
        </button>
      ) : (
        <>
          <button type="button" aria-label={reader.state === 'playing' ? t('pause') : t('resume')} className="grid size-8 place-items-center rounded-full bg-accent text-accent-fg" onClick={() => (reader.state === 'playing' ? reader.pause() : reader.resume())}>
            {reader.state === 'playing' ? <Pause className="size-4" aria-hidden /> : <Play className="size-4" aria-hidden />}
          </button>
          <button type="button" aria-label={t('stop')} className="grid size-8 place-items-center rounded-full hover:bg-surface-2" onClick={reader.stop}>
            <Square className="size-3.5" aria-hidden />
          </button>
        </>
      )}
      <select aria-label={t('speed')} className="rounded-full bg-transparent px-1.5 py-1 text-sm" value={reader.rate} onChange={(e) => reader.setRate(Number(e.target.value))}>
        {[0.75, 1, 1.25, 1.5, 2].map((r) => (
          <option key={r} value={r}>
            {r}×
          </option>
        ))}
      </select>
    </div>
  )
}
