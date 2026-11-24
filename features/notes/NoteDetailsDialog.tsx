'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Field } from '@/components/ui/field'
import { Input } from '@/components/ui/input'
import { FindTopicsDocument, OrganiseDocument, UpdateNoteDraftDocument } from '@/graphql/generated/graphql'
import type { NoteMeta } from './api'

/** Where a note lives and what it is about: folder, tags and topics (the owner's; last-writer-wins, §13.2). */
export function NoteDetailsDialog({ meta, open, onClose, onSaved }: { meta: NoteMeta; open: boolean; onClose: () => void; onSaved: (meta: NoteMeta) => void }) {
  const t = useTranslations('notes.details')
  const organise = useQuery(OrganiseDocument, { skip: !open })
  const [folderId, setFolderId] = useState(meta.folder?.id ?? '')
  const [tags, setTags] = useState(meta.tags.map((x) => x.name).join(', '))
  const [topics, setTopics] = useState(meta.topics.map((x) => ({ id: x.id, title: x.title, subject: x.subject.title })))
  const [query, setQuery] = useState('')
  const found = useQuery(FindTopicsDocument, { variables: { query }, skip: query.trim().length < 2 })
  const [save, saving] = useMutation(UpdateNoteDraftDocument)
  const [error, setError] = useState<string | null>(null)
  const folders = organise.data?.myFolders ?? []
  const depth = (id: string | null | undefined): number => (id ? 1 + depth(folders.find((f) => f.id === id)?.parentId) : 0)

  const submit = async () => {
    setError(null)
    const res = await save({
      variables: {
        input: {
          noteId: meta.id,
          folderId: folderId || null,
          tagNames: tags.split(',').map((s) => s.trim()).filter(Boolean),
          topicIds: topics.map((x) => x.id),
        },
      },
    }).catch(() => null)
    const payload = res?.data?.updateNoteDraft
    if (payload?.note) {
      onSaved(payload.note)
      onClose()
    } else setError(payload?.userErrors[0]?.message ?? t('failed'))
  }

  return (
    <Dialog open={open} onClose={onClose} title={t('title')}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(e) => {
          e.preventDefault()
          void submit()
        }}
      >
        <Field label={t('folder')}>
          <select className="h-11 w-full rounded-xl border border-border bg-surface px-3 text-[15px]" value={folderId} onChange={(e) => setFolderId(e.target.value)}>
            <option value="">{t('noFolder')}</option>
            {folders.map((f) => (
              <option key={f.id} value={f.id}>
                {'  '.repeat(depth(f.parentId))}
                {f.name}
              </option>
            ))}
          </select>
        </Field>
        <Field label={t('tags')} hint={t('tagsHint')}>
          <Input value={tags} onChange={(e) => setTags(e.target.value)} />
        </Field>
        <div className="flex flex-col gap-2">
          <Field label={t('topics')} hint={t('topicsHint')}>
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('topicSearch')} />
          </Field>
          {query.trim().length >= 2 ? (
            <ul className="max-h-40 overflow-y-auto rounded-xl border border-border">
              {(found.data?.findTopics ?? []).map((x) => (
                <li key={x.id}>
                  <button
                    type="button"
                    className="flex w-full justify-between gap-2 px-3 py-2 text-left text-sm hover:bg-surface-2 disabled:opacity-50"
                    disabled={topics.some((y) => y.id === x.id) || topics.length >= 10}
                    onClick={() => setTopics((list) => [...list, { id: x.id, title: x.title, subject: x.subject.title }])}
                  >
                    <span>{x.title}</span>
                    <span className="text-xs text-muted">{x.subject.title}</span>
                  </button>
                </li>
              ))}
              {found.data && !found.data.findTopics.length ? <li className="px-3 py-2 text-sm text-muted">{t('noTopics')}</li> : null}
            </ul>
          ) : null}
          <ul className="flex flex-wrap gap-2">
            {topics.map((x) => (
              <li key={x.id} className="flex items-center gap-1 rounded-[10px] bg-accent-soft px-3 py-1 text-sm">
                {x.title}
                <button type="button" aria-label={t('removeTopic', { topic: x.title })} className="text-muted hover:text-fg" onClick={() => setTopics((list) => list.filter((y) => y.id !== x.id))}>
                  ✕
                </button>
              </li>
            ))}
          </ul>
        </div>
        {error ? (
          <p role="alert" className="text-sm text-bad">
            {error}
          </p>
        ) : null}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="ghost" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button type="submit" disabled={saving.loading}>
            {t('save')}
          </Button>
        </div>
      </form>
    </Dialog>
  )
}
