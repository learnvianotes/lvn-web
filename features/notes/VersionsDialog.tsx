'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { NoteVersionPreviewDocument, NoteVersionsDocument, RestoreNoteVersionDocument } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { CardView } from './render/CardView'

/** Version history (lvn-backend §4.3): every version, a preview of any, and restore — the draft is kept as a version first. */
export function VersionsDialog({ noteId, open, initialVersionId, onClose, onRestored }: { noteId: string; open: boolean; initialVersionId?: string; onClose: () => void; onRestored: () => void }) {
  const t = useTranslations('notes.versions')
  const [picked, setPicked] = useState<string | null>(null)
  const selected = picked ?? initialVersionId ?? null
  const list = useQuery(NoteVersionsDocument, { variables: { id: noteId }, skip: !open, fetchPolicy: 'network-only' })
  const preview = useQuery(NoteVersionPreviewDocument, { variables: { id: noteId, versionId: selected ?? '' }, skip: !open || !selected })
  const [restore, restoring] = useMutation(RestoreNoteVersionDocument)
  const versions = list.data?.note?.versions?.edges.map((e) => e.node) ?? []
  const version = preview.data?.note?.version

  return (
    <Dialog open={open} onClose={() => (setPicked(null), onClose())} title={t('title')} wide>
      <div className="grid gap-4 sm:grid-cols-[14rem_minmax(0,1fr)]">
        <ol className="flex flex-col gap-1">
          {list.loading ? <li className="text-sm text-muted">…</li> : null}
          {versions.map((v) => (
            <li key={v.id}>
              <button type="button" aria-current={selected === v.id} className={cn('flex w-full flex-col rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2', selected === v.id && 'bg-accent-soft')} onClick={() => setPicked(v.id)}>
                <span className="font-medium">
                  {t('number', { n: v.number })} · {t(`kind.${v.kind}`)}
                </span>
                <span className="text-xs text-muted">
                  {new Date(v.createdAt).toLocaleString()} · {v.createdBy.displayName}
                </span>
              </button>
            </li>
          ))}
          {!list.loading && !versions.length ? <li className="text-sm text-muted">{t('none')}</li> : null}
        </ol>
        <section aria-live="polite" className="min-w-0">
          {!selected ? (
            <p className="text-sm text-muted">{t('pick')}</p>
          ) : !version ? (
            <p className="text-sm text-muted">…</p>
          ) : (
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between gap-2">
                <h3 className="truncate text-lg font-bold">{version.title || t('untitled')}</h3>
                <Button
                  size="sm"
                  disabled={restoring.loading}
                  onClick={async () => {
                    const res = await restore({ variables: { noteId, versionId: version.id } })
                    if (res.data?.restoreNoteVersion.note) {
                      setPicked(null)
                      onRestored()
                    }
                  }}
                >
                  {t('restore')}
                </Button>
              </div>
              <p className="text-xs text-muted">{t('restoreHint')}</p>
              <div className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4">
                {version.cards.edges.map(({ node: c }) => (
                  <CardView key={c.id} id={c.id} type={c.type} content={c.content} />
                ))}
              </div>
            </div>
          )}
        </section>
      </div>
    </Dialog>
  )
}
